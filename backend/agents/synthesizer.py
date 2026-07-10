import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def generate_graph_payload(user_id: str, matches: List[Dict]) -> Dict:
    """
    Synthesizes the enriched job matches into a flat Graphology-compliant JSON.
    """
    logger.info(f"Synthesizing {len(matches)} matches into graph payload.")
    
    nodes = {}
    edges = []
    
    # 1. User Node
    user_node_key = f"user_{user_id}"
    nodes[user_node_key] = {
        "key": user_node_key,
        "attributes": {"label": f"User {user_id}", "type": "User", "color": "#ffffff", "size": 15}
    }
    
    for i, match in enumerate(matches):
        job_title = match.get("title", "Unknown Title")
        company = match.get("company", "Unknown Company")
        
        # 2. Company Node
        comp_key = f"comp_{company.replace(' ', '_')}"
        if comp_key not in nodes:
            nodes[comp_key] = {
                "key": comp_key,
                "attributes": {"label": company, "type": "Company", "color": "#a855f7", "size": 10}
            }
            
        # 3. Job Node
        job_key = f"job_{i}"
        nodes[job_key] = {
            "key": job_key,
            "attributes": {
                "label": job_title, 
                "type": "Job", 
                "color": "#10b981", 
                "size": 8,
                "link": match.get("link", ""),
                "fit_score": round(match.get("match_score", 0.0) * 100, 1),
                "company": company
            }
        }
        
        # Job to Company Edge
        edges.append({
            "key": f"edge_{job_key}_{comp_key}",
            "source": job_key,
            "target": comp_key,
            "attributes": {"type": "BELONGS_TO", "weight": 1.0}
        })
        
        paths = match.get("network_paths", [])
        
        for path in paths:
            chain = path.get("connection_chain", [])
            hops = path.get("hops", 0)
            
            prev_node_key = user_node_key
            
            for j, person in enumerate(chain):
                person_name = person.get("name", f"Person_{j}")
                person_pos = person.get("position", "")
                person_key = f"person_{person_name.replace(' ', '_')}"
                
                if person_key not in nodes:
                    nodes[person_key] = {
                        "key": person_key,
                        "attributes": {
                            "label": person_name, 
                            "type": "Contact", 
                            "color": "#3b82f6", 
                            "size": 6,
                            "position": person_pos
                        }
                    }
                
                # Edge from prev to this person
                edge_key = f"edge_{prev_node_key}_{person_key}"
                
                if not any(e["key"] == edge_key for e in edges):
                    action_prompt = ""
                    if prev_node_key == user_node_key:
                        if hops == 1 and j == 0:
                            action_prompt = f"Hi {person_name}, I saw the {job_title} opening at {company}. Do you have a few minutes to chat about the role?"
                        elif hops == 2 and j == 0:
                            action_prompt = f"Hi {person_name}, I noticed you're connected to {chain[-1].get('name')} at {company}. Could you potentially introduce me? I'm applying for the {job_title} role."
                    
                    edges.append({
                        "key": edge_key,
                        "source": prev_node_key,
                        "target": person_key,
                        "attributes": {
                            "type": "CONNECTED_TO", 
                            "weight": 0.8,
                            "message": action_prompt
                        }
                    })
                
                prev_node_key = person_key
                
            if chain:
                last_person_key = f"person_{chain[-1].get('name', '').replace(' ', '_')}"
                edge_comp_key = f"edge_{last_person_key}_{comp_key}"
                if not any(e["key"] == edge_comp_key for e in edges):
                    edges.append({
                        "key": edge_comp_key,
                        "source": last_person_key,
                        "target": comp_key,
                        "attributes": {"type": "WORKS_AT", "weight": 0.9}
                    })
                
    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

