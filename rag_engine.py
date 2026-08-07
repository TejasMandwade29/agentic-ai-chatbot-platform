import os
import re
import math
from collections import Counter

# ── Lightweight Vector Search & RAG Engine ────────────────────────────────────
# Built for production reliability across cloud platforms without heavy C++ dependencies.

DOCUMENT_PATH = os.path.join(os.path.dirname(__file__), "data", "policy_documents.txt")

def _load_and_chunk_documents():
    """Loads policy document and splits into logical sections/paragraphs."""
    if not os.path.exists(DOCUMENT_PATH):
        return ["Policy document not found."]
    
    with open(DOCUMENT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by double newlines or numbered sections
    raw_chunks = re.split(r'\n\s*\n', content)
    chunks = [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > 30]
    return chunks

def _tokenize(text):
    """Simple word tokenizer for TF-IDF vector embedding."""
    return re.findall(r'\w+', text.lower())

def _cosine_similarity(vec1, vec2):
    """Calculates cosine similarity between two term-frequency vectors."""
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator

class PolicyVectorStore:
    def __init__(self):
        self.chunks = _load_and_chunk_documents()
        self.vectorized_chunks = [Counter(_tokenize(chunk)) for chunk in self.chunks]

    def search(self, query: str, top_k: int = 2) -> str:
        """Performs vector similarity search against policy knowledge base."""
        query_vec = Counter(_tokenize(query))
        
        scores = []
        for idx, chunk_vec in enumerate(self.vectorized_chunks):
            score = _cosine_similarity(query_vec, chunk_vec)
            scores.append((score, self.chunks[idx]))
        
        # Sort by similarity score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        top_results = [chunk for score, chunk in scores[:top_k] if score > 0.0]
        
        if not top_results:
            # Fallback to returning general policy chunks if no exact keyword match
            top_results = self.chunks[:top_k]
            
        return "\n\n---\n\n".join(top_results)

# Global Vector Store Instance
_vector_store = PolicyVectorStore()

def query_policy_knowledgebase(query: str) -> str:
    """Searches the official Fintech Policy Knowledge Base using vector semantic search."""
    return _vector_store.search(query, top_k=2)

if __name__ == "__main__":
    print("Testing RAG Engine:")
    print(query_policy_knowledgebase("international dispute time limit"))
