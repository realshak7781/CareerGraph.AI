import json
from agents.synthesizer import generate_graph_payload

dummy_matches = [
    {
        "title": "Data Scientist",
        "company": "TechNova",
        "link": "http://example.com/job",
        "match_score": 0.85,
        "network_paths": [
            {
                "company_matched": "TechNova",
                "hops": 1,
                "connection_chain": [
                    {"name": "Alice Smith", "position": "Software Engineer"}
                ]
            }
        ]
    }
]

payload = generate_graph_payload("user1", dummy_matches)
print(json.dumps(payload, indent=2))
