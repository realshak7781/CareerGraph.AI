import os
import logging
from services.pdf_parser import extract_text_from_pdf
from services.linkedin_parser import parse_linkedin_zip
from services.graph_ingestion import ingest_user_resume, ingest_linkedin_data

logging.basicConfig(level=logging.INFO)

def run_real_ingestion():
    user_id = "sharique"
    
    resume_path = os.path.join("data", "Sharique_Resume_.pdf")
    linkedin_path = os.path.join("data", "linkedin zip data for sharique.zip")
    
    # 1. Parse and ingest Resume
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            pdf_bytes = f.read()
            
        print("Extracting text from Resume PDF...")
        resume_text = extract_text_from_pdf(pdf_bytes)
        print(f"Extracted {len(resume_text)} characters from Resume. Ingesting to Neo4j...")
        ingest_user_resume(user_id, resume_text)
    else:
        print(f"Resume not found at {resume_path}")

    # 2. Parse and ingest LinkedIn
    if os.path.exists(linkedin_path):
        with open(linkedin_path, "rb") as f:
            zip_bytes = f.read()
            
        print("Parsing LinkedIn ZIP...")
        parsed_data = parse_linkedin_zip(zip_bytes)
        print(f"Found {len(parsed_data.get('connections', []))} connections in ZIP. Ingesting to Neo4j...")
        ingest_linkedin_data(user_id, parsed_data)
    else:
        print(f"LinkedIn ZIP not found at {linkedin_path}")

    print("Phase 1: Real Data Ingestion Complete!")

if __name__ == "__main__":
    run_real_ingestion()
