import os
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
            
    def verify_connection(self):
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

# Singleton instance
neo4j_client = Neo4jClient()
