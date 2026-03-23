import faiss
import numpy as np

class FAISSStore:
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []  # Persistent DB mapping id -> text should be used in production

    def add_document(self, embedding: np.ndarray, text: str):
        self.index.add(np.array([embedding]).astype('float32'))
        self.documents.append(text)

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
