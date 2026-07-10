import time
from services.neo4j_client import neo4j_client

def init_schema():
    print("Waiting for Neo4j to be ready...")
    retries = 30
    ready = False
    while retries > 0:
        if neo4j_client.verify_connection():
            ready = True
            break
        print(f"Neo4j not ready. Retrying in 5 seconds... ({retries} left)")
        time.sleep(5)
        retries -= 1
        
    if not ready:
        print("Failed to connect to Neo4j. Is the container running?")
        return

    print("Connected! Initializing constraints and schema...")
    
    # Drop existing vector indexes to recreate with new dimensions
    try:
        neo4j_client.execute_query("DROP INDEX user_resume_embedding IF EXISTS")
        neo4j_client.execute_query("DROP INDEX person_profile_embedding IF EXISTS")
    except Exception as e:
        print(f"Error dropping indexes: {e}")

    queries = [
        # User constraint
        "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
        
        # Person constraint (connections)
        "CREATE CONSTRAINT person_url IF NOT EXISTS FOR (p:Person) REQUIRE p.url IS UNIQUE",
        
        # Company constraint
        "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",

        # Vector Index for User Resume Embeddings
        """
        CREATE VECTOR INDEX user_resume_embedding IF NOT EXISTS
        FOR (u:User) ON (u.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 3072,
         `vector.similarity_function`: 'cosine'
        }}
        """,
        
        # Vector Index for Person Profile Embeddings
        """
        CREATE VECTOR INDEX person_profile_embedding IF NOT EXISTS
        FOR (p:Person) ON (p.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 3072,
         `vector.similarity_function`: 'cosine'
        }}
        """
    ]
    
    for query in queries:
        try:
            neo4j_client.execute_query(query)
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Error executing {query}:\n{e}")

    print("Schema initialization complete.")
    
    # Verify schema
    result = neo4j_client.execute_query("SHOW CONSTRAINTS")
    print("\nCurrent Constraints:")
    for record in result:
        print(f" - {record['name']}: {record['labelsOrTypes']} {record['properties']}")

    # Verify vector indexes
    result = neo4j_client.execute_query("SHOW VECTOR INDEXES")
    print("\nCurrent Vector Indexes:")
    for record in result:
        print(f" - {record['name']}: {record['labelsOrTypes']} ON {record['properties']} (dim: {record.get('options', {}).get('indexConfig', {}).get('vector.dimensions', 'N/A')})")

if __name__ == "__main__":
    init_schema()
    neo4j_client.close()
