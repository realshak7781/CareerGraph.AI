import asyncio
import json
import logging
from services.neo4j_client import neo4j_client
from services.graph_ingestion import ingest_user_resume, ingest_linkedin_data
from agents.orchestrator import career_graph_orchestrator

logging.basicConfig(level=logging.INFO)

async def run_test():
    user_id = "sharique"
    
    print("--- 2. Running LangGraph Orchestrator ---")
    # Execute the graph
    initial_state = {
        "user_id": user_id,
        "job_postings": [],
        "matches": [],
        "action_cards": []
    }
    
    # Since orchestrator is compiled, we use ainvoke
    final_state = await career_graph_orchestrator.ainvoke(initial_state)
    
    print("--- 3. Orchestrator Final State ---")
    print(f"Ingestion Complete: {final_state.get('ingestion_complete')}")
    print(f"Number of Scraped Jobs: {len(final_state.get('job_postings', []))}")
    print(f"Number of Processed Matches: {len(final_state.get('matches', []))}")
    
    if final_state.get('action_cards'):
        top_card = final_state['action_cards'][0]
        print("\n--- Top Action Card ---")
        print(json.dumps(top_card, indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
