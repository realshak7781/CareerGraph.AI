import logging
import time
from services.neo4j_client import neo4j_client
from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

def ingest_linkedin_data(user_id: str, parsed_data: dict):
    """
    Ingest parsed LinkedIn data into the Neo4j graph.
    """
    connections = parsed_data.get("connections", [])
    
    # Filter out connections without URLs first
    valid_connections = [c for c in connections if c.get("URL")]
    
    logger.info(f"Ingesting {len(valid_connections)} valid connections for user {user_id}")
    
    batch_size = 100
    for i in range(0, len(valid_connections), batch_size):
        batch = valid_connections[i:i+batch_size]
        
        # Prepare texts for batch embedding
        batch_texts = []
        for conn in batch:
            first = conn.get("First Name", "")
            last = conn.get("Last Name", "")
            pos = conn.get("Position", "")
            comp = conn.get("Company", "")
            batch_texts.append(f"{first} {last} is a {pos} at {comp}")
            
        # Generate embeddings in one single API request for the entire batch
        batch_embeddings = embedding_service.generate_embeddings(batch_texts)
        
        # Ingest into Neo4j
        for conn, embedding in zip(batch, batch_embeddings):
            url = conn.get("URL")
            first_name = conn.get("First Name", "")
            last_name = conn.get("Last Name", "")
            company_name = conn.get("Company")
            position = conn.get("Position", "")
            
            # User -> Person
            query_person = """
            MERGE (u:User {id: $user_id})
            MERGE (p:Person {url: $url})
            SET p.firstName = $first_name, 
                p.lastName = $last_name, 
                p.position = $position,
                p.embedding = $embedding
            MERGE (u)-[:CONNECTED_TO]->(p)
            """
            neo4j_client.execute_query(query_person, {
                "user_id": user_id,
                "url": url,
                "first_name": first_name,
                "last_name": last_name,
                "position": position,
                "embedding": embedding
            })
            
            # Person -> Company
            if company_name:
                query_company = """
                MATCH (p:Person {url: $url})
                MERGE (c:Company {name: $company_name})
                MERGE (p)-[:WORKS_AT {role: $position}]->(c)
                """
                neo4j_client.execute_query(query_company, {
                    "url": url, 
                    "company_name": company_name, 
                    "position": position
                })
        
        # Defensive throttling between batch transactions to respect Gemini RPM limits
        time.sleep(0.5)

def ingest_user_resume(user_id: str, resume_text: str):
    """
    Ingest the user's parsed resume text into the Neo4j graph.
    """
    logger.info(f"Ingesting resume for user {user_id}")
    embedding = embedding_service.generate_embedding(resume_text)
    
    query = """
    MERGE (u:User {id: $user_id})
    SET u.resume_text = $resume_text,
        u.embedding = $embedding
    """
    neo4j_client.execute_query(query, {
        "user_id": user_id,
        "resume_text": resume_text,
        "embedding": embedding
    })
