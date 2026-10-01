import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
import faiss
from django.conf import settings

class BaseVectorStore(ABC):
    """Abstract Base Class for Vector Store implementations (FAISS / ChromaDB / etc.)."""

    @abstractmethod
    def add_chunks(self, chunks, embeddings):
        pass

    @abstractmethod
    def search(self, query_embedding, top_k=5):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def clear(self):
        pass

class FAISSVectorStore(BaseVectorStore):
    """FAISS-based vector database implementation with metadata sidecar."""

    def __init__(self, storage_dir=None, dimension=384):
        if storage_dir is None:
            self.storage_dir = Path(getattr(settings, 'VECTOR_DB_PATH', 'vector_store'))
        else:
            self.storage_dir = Path(storage_dir)

        self.dimension = dimension
        self.index_file = self.storage_dir / "index.faiss"
        self.metadata_file = self.storage_dir / "metadata.json"

        self.index = None
        self.metadata_store = [] # List of dicts matching FAISS indices

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.load()

    def _create_new_index(self):
        # IndexFlatIP with normalized vectors calculates Cosine Similarity
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata_store = []

    def add_chunks(self, chunks, embeddings):
        """Adds text chunks and corresponding embedding vectors to the FAISS index."""
        if len(chunks) == 0:
            return

        if embeddings.shape[1] != self.dimension:
            # Update dimension if model dimension differs
            self.dimension = embeddings.shape[1]
            if self.index is None or self.index.ntotal == 0:
                self._create_new_index()

        if self.index is None:
            self._create_new_index()

        # Ensure L2 normalization for inner product (cosine similarity)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        normalized_embeddings = embeddings / norms

        self.index.add(normalized_embeddings.astype(np.float32))

        for chunk in chunks:
            self.metadata_store.append({
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "metadata": chunk.metadata
            })

    def search(self, query_embedding, top_k=5):
        """
        Searches FAISS index for top K most similar vectors.
        Returns list of tuples: (item_dict, float_score)
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        # Normalize query vector
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm
        query_vec = np.array([query_embedding], dtype=np.float32)

        actual_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, actual_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.metadata_store):
                item = self.metadata_store[idx]
                results.append((item, float(score)))

        return results

    def save(self):
        """Persists FAISS index and metadata sidecar file to disk."""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_store, f, indent=2, ensure_ascii=False)
            print(f"Saved FAISS vector index with {self.index.ntotal} vectors to {self.storage_dir}")

    def load(self):
        """Loads FAISS index and metadata sidecar from disk if available."""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata_store = json.load(f)
                self.dimension = self.index.d
                print(f"Loaded existing FAISS index with {self.index.ntotal} vectors.")
                return True
            except Exception as e:
                print(f"Failed to load FAISS index from disk: {e}")

        self._create_new_index()
        return False

    def clear(self):
        """Clears the FAISS index and deletes disk files."""
        self._create_new_index()
        if self.index_file.exists():
            try:
                os.remove(self.index_file)
            except OSError:
                pass
        if self.metadata_file.exists():
            try:
                os.remove(self.metadata_file)
            except OSError:
                pass

_VECTOR_STORE_INSTANCE = None

def get_vector_store():
    """Singleton getter for FAISSVectorStore."""
    global _VECTOR_STORE_INSTANCE
    if _VECTOR_STORE_INSTANCE is None:
        _VECTOR_STORE_INSTANCE = FAISSVectorStore()
    return _VECTOR_STORE_INSTANCE
