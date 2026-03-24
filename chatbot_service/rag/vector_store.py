import faiss
import numpy as np

class FAISSStore:
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []  # List of dicts, e.g. {"product_id": 1, "text": "..."}

    def add_document(self, embedding: np.ndarray, meta_data: dict):
        self.index.add(np.array([embedding]).astype('float32'))
        self.documents.append(meta_data)

    def search(self, query_embedding: np.ndarray, top_k=3):
        if self.index.ntotal == 0:
            return []
        
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results

# Global RAG store instance
store = FAISSStore()
