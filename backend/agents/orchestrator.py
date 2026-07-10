import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END
from services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

# Define the State for the LangGraph orchestrator
class OrchestratorState(TypedDict):
    user_id: str
    ingestion_complete: bool
    job_postings: list[dict]
    matches: list[dict]
    action_cards: list[dict]
    graph_payload: dict

# Node 1: Check Ingestion Status (The Lock)
def check_ingestion_node(state: OrchestratorState):
    """
    Checks if the vector index and graph schema are populated for the user.
    Enforces the strict sequential execution constraint (Phase 1 must finish).
    """
    logger.info(f"Checking ingestion status for user: {state.get('user_id')}")
    query = """
    MATCH (u:User {id: $user_id})
    RETURN u.embedding IS NOT NULL AS has_embedding
    """
    
    try:
        result = neo4j_client.execute_query(query, {"user_id": state.get("user_id")})
        is_ready = False
        if result and result[0].get("has_embedding"):
            # Also check if we have connections to verify full data presence
            conn_query = "MATCH (u:User {id: $user_id})-[:CONNECTED_TO]->(p:Person) RETURN count(p) as conn_count"
            conn_res = neo4j_client.execute_query(conn_query, {"user_id": state.get("user_id")})
            if conn_res and conn_res[0].get("conn_count", 0) > 0:
                is_ready = True
                
        return {"ingestion_complete": is_ready}
    except Exception as e:
        logger.error(f"Error checking ingestion state: {e}")
        return {"ingestion_complete": False}

# Conditional Edge: Route based on lock status
def route_after_ingestion_check(state: OrchestratorState):
    if state.get("ingestion_complete"):
        logger.info("Ingestion complete. Unlocking Phase 2...")
        return "scraper_agent"
    logger.warning("Ingestion NOT complete. Phase 2 remains locked.")
    return "locked_wait"

# Node: Locked/Wait state
def locked_wait_node(state: OrchestratorState):
    """Fallback node when the system is locked."""
    return state

from agents.scraper import scrape_jobs
import asyncio

# Node 2: Scraper Agent (T08 Real Implementation)
async def scraper_node(state: OrchestratorState):
    logger.info("Running Scraper Agent...")
    # Using nest_asyncio just in case LangGraph is running in a running event loop
    import nest_asyncio
    nest_asyncio.apply()
    
    # We can pass a query based on User's profile, but for now we hardcode or extract from state
    postings = await scrape_jobs("Data Scientist")
    
    return {"job_postings": postings}


from agents.matchmaker import run_matchmaker

# Node 3: Matchmaker Agent (T09 Real Implementation)
def matchmaker_node(state: OrchestratorState):
    logger.info("Running Matchmaker Agent...")
    job_postings = state.get("job_postings", [])
    user_id = state.get("user_id", "default_user")
    
    matches = run_matchmaker(user_id, job_postings)
    
    return {"matches": matches}

from agents.synthesizer import generate_graph_payload

# Node 4: Synthesizer Agent (T10 Real Implementation)
def synthesizer_node(state: OrchestratorState):
    logger.info("Running Synthesizer Agent...")
    matches = state.get("matches", [])
    user_id = state.get("user_id", "default_user")
    
    graph_payload = generate_graph_payload(user_id, matches)
    
    return {"graph_payload": graph_payload}


# Build the StateGraph
workflow = StateGraph(OrchestratorState)

workflow.add_node("check_ingestion", check_ingestion_node)
workflow.add_node("locked_wait", locked_wait_node)
workflow.add_node("scraper_agent", scraper_node)
workflow.add_node("matchmaker_agent", matchmaker_node)
workflow.add_node("synthesizer_agent", synthesizer_node)

# Entry Point
workflow.set_entry_point("check_ingestion")

# Edges
workflow.add_conditional_edges(
    "check_ingestion",
    route_after_ingestion_check,
    {
        "scraper_agent": "scraper_agent",
        "locked_wait": "locked_wait"
    }
)

workflow.add_edge("locked_wait", END)
workflow.add_edge("scraper_agent", "matchmaker_agent")
workflow.add_edge("matchmaker_agent", "synthesizer_agent")
workflow.add_edge("synthesizer_agent", END)

# Compile orchestrator
career_graph_orchestrator = workflow.compile()
