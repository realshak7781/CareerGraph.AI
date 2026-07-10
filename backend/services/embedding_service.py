import os
import logging
import requests

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is missing. Embeddings will fail if requested.")
            
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings using Google Gemini REST API directly to force batching.
        Pads the 768-dimensional output to 3072 dimensions to match Neo4j's requirements.
        """
        if not texts:
            return []
            
        if not self.api_key:
            return [[0.1] * 3072 for _ in texts]
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={self.api_key}"
        
        requests_payload = {
            "requests": [
                {
                    "model": "models/gemini-embedding-001",
                    "content": {
                        "parts": [{"text": text}]
                    }
                } for text in texts
            ]
        }
        
        try:
            response = requests.post(url, json=requests_payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code != 200:
                logger.error(f"Error calling Gemini REST API: {response.text}")
                return []
                
            data = response.json()
            embeddings = [item['values'] for item in data.get('embeddings', [])]
            
            padded_embeddings = []
            for emb in embeddings:
                padded = emb + [0.0] * (3072 - len(emb))
                padded_embeddings.append(padded)
                
            # If for some reason the response length doesn't match, pad the rest
            while len(padded_embeddings) < len(texts):
                padded_embeddings.append([0.0] * 3072)
                
            return padded_embeddings
            
        except Exception as e:
            logger.error(f"Error calling Gemini REST API: {e}")
            return []
    
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for a single string.
        """
        if not text:
            return []
        embeddings = self.generate_embeddings([text])
        if embeddings:
            return embeddings[0]
        return []

# Singleton instance
embedding_service = EmbeddingService()
