import base64
import logging
from celery_app import celery_app
from services.linkedin_parser import parse_linkedin_zip
from services.pdf_parser import extract_text_from_pdf
from services.graph_ingestion import ingest_linkedin_data, ingest_user_resume

logger = logging.getLogger(__name__)

@celery_app.task(name="process_linkedin_zip")
def process_linkedin_zip_task(zip_b64: str, user_id: str = "default_user"):
    """
    Celery task to process the uploaded LinkedIn ZIP file asynchronously.
    """
    # Decode base64 to bytes
    zip_bytes = base64.b64decode(zip_b64)
    
    # Parse in memory
    parsed_data = parse_linkedin_zip(zip_bytes)
    
    # TEMPORARY DEV OVERRIDE: Cap data stream to bypass Gemini 1K daily limit
    if "connections" in parsed_data:
        parsed_data["connections"] = parsed_data["connections"][:50]
        logger.info(f"DEV MODE: Truncated network dataset to {len(parsed_data['connections'])} items for visual QA scaling.")
    
    # Trigger graph ingestion
    ingest_linkedin_data(user_id, parsed_data)
    
    return {
        "status": "success",
        "connections_count": len(parsed_data.get("connections", [])),
        "positions_count": len(parsed_data.get("positions", []))
    }

@celery_app.task(name="process_resume_pdf")
def process_resume_pdf_task(pdf_b64: str, user_id: str = "default_user"):
    """
    Celery task to process the uploaded Resume PDF file asynchronously.
    """
    pdf_bytes = base64.b64decode(pdf_b64)
    resume_text = extract_text_from_pdf(pdf_bytes)
    
    ingest_user_resume(user_id, resume_text)
    
    return {
        "status": "success",
        "text_length": len(resume_text)
    }
