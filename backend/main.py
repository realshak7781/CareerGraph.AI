import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
import base64
from tasks import process_linkedin_zip_task, process_resume_pdf_task
import sys
import asyncio
import io
import json
from fastapi.responses import StreamingResponse

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CareerGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to CareerGraph API"}

@app.post("/upload/linkedin")
async def upload_linkedin_data(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Must be a .zip file (LinkedinData.zip)")
    
    zip_bytes = await file.read()
    zip_b64 = base64.b64encode(zip_bytes).decode('utf-8')
    task = process_linkedin_zip_task.delay(zip_b64)
    
    return {
        "message": "LinkedIn data uploaded successfully. Processing in background.",
        "task_id": task.id
    }

@app.post("/upload/resume")
async def upload_resume_data(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Must be a .pdf file")
    
    pdf_bytes = await file.read()
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    task = process_resume_pdf_task.delay(pdf_b64)
    
    return {
        "message": "Resume uploaded successfully. Processing in background.",
        "task_id": task.id
    }

@app.post("/api/v1/ingest")
async def ingest_payload(resume: UploadFile = File(...), career_archive: UploadFile = File(...)):
    from services.linkedin_parser import parse_linkedin_zip
    from services.pdf_parser import extract_text_from_pdf
    from services.graph_ingestion import ingest_linkedin_data, ingest_user_resume
    from agents.orchestrator import career_graph_orchestrator
    
    async def event_stream():
        try:
            # Stage 1: Uploading files
            yield f"data: {json.dumps({'stage': 1, 'status': 'active', 'message': 'Uploading files'})}\n\n"
            
            resume_bytes = await resume.read()
            archive_bytes = await career_archive.read()
            
            if len(resume_bytes) > 10 * 1024 * 1024:
                yield f"data: {json.dumps({'stage': 1, 'status': 'error', 'message': 'Resume exceeds 10MB'})}\n\n"
                return
            if len(archive_bytes) > 50 * 1024 * 1024:
                yield f"data: {json.dumps({'stage': 1, 'status': 'error', 'message': 'ZIP exceeds 50MB'})}\n\n"
                return
                
            yield f"data: {json.dumps({'stage': 1, 'status': 'complete'})}\n\n"
            
            user_id = "sharique" # Default
            
            import base64
            import asyncio
            resume_b64 = base64.b64encode(resume_bytes).decode('utf-8')
            archive_b64 = base64.b64encode(archive_bytes).decode('utf-8')
            
            yield f"data: {json.dumps({'stage': 2, 'status': 'active', 'message': 'Parsing resume (Celery)'})}\n\n"
            yield f"data: {json.dumps({'stage': 3, 'status': 'active', 'message': 'Extracting contacts (Celery)'})}\n\n"
            yield f"data: {json.dumps({'stage': 5, 'status': 'active', 'message': 'Writing to Neo4j (Celery)'})}\n\n"
            
            # Dispatch Celery tasks
            resume_task = process_resume_pdf_task.delay(resume_b64, user_id)
            linkedin_task = process_linkedin_zip_task.delay(archive_b64, user_id)
            
            while not (resume_task.ready() and linkedin_task.ready()):
                await asyncio.sleep(1.0)
                
            if resume_task.failed() or linkedin_task.failed():
                raise Exception("One or more Celery background tasks failed during ingestion.")
                
            yield f"data: {json.dumps({'stage': 2, 'status': 'complete'})}\n\n"
            yield f"data: {json.dumps({'stage': 3, 'status': 'complete'})}\n\n"
            yield f"data: {json.dumps({'stage': 5, 'status': 'complete'})}\n\n"
            
            # Stage 4: Running GraphRAG synthesis
            yield f"data: {json.dumps({'stage': 4, 'status': 'active', 'message': 'Running GraphRAG synthesis'})}\n\n"
            initial_state = {"user_id": user_id}
            final_state = await career_graph_orchestrator.ainvoke(initial_state)
            yield f"data: {json.dumps({'stage': 4, 'status': 'complete'})}\n\n"
            
            # Stage 6: Generating graph layout
            yield f"data: {json.dumps({'stage': 6, 'status': 'active', 'message': 'Generating graph layout'})}\n\n"
            payload = final_state.get("graph_payload")
            yield f"data: {json.dumps({'stage': 6, 'status': 'complete'})}\n\n"
            
            # Stage 7: Ready
            yield f"data: {json.dumps({'stage': 7, 'status': 'active', 'message': 'Ready'})}\n\n"
            yield f"data: {json.dumps({'stage': 7, 'status': 'complete', 'payload': payload})}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'stage': 'error', 'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/api/graph")
async def get_graph_data(user_id: str = "default_user"):
    from agents.orchestrator import career_graph_orchestrator
    
    initial_state = {"user_id": user_id}
    final_state = await career_graph_orchestrator.ainvoke(initial_state)
    
    if not final_state.get("ingestion_complete"):
        raise HTTPException(status_code=400, detail="Data ingestion not complete. Graph locked.")
        
    payload = final_state.get("graph_payload")
    if not payload:
        raise HTTPException(status_code=404, detail="Graph data not available yet.")
        
    return payload

if __name__ == "__main__":
    import uvicorn
    # The policy is already set at the top of the file, but we run uvicorn here
    # so the policy takes effect before the loop is created.
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
