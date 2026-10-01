import numpy as np
from django.conf import settings

_EMBEDDER_INSTANCE = None

class EmbeddingService:
    """Service wrapper around sentence-transformers with fallback mechanism."""

    def __init__(self, model_name=None):
        self.model_name = model_name or getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"Loaded sentence-transformer model: {self.model_name} (dim: {self.dimension})")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer ('{self.model_name}'): {e}")
            print("Using fallback deterministic embedding generator for development/testing.")
            self.model = None
            self.dimension = 384

    def generate_embeddings(self, texts):
        """Generates embeddings for a list of text strings."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)

        # Fallback pseudo-embeddings using hashing if sentence-transformers unavailable
        return self._fallback_embeddings(texts)

    def generate_query_embedding(self, query):
        """Generates embedding for a single search query string."""
        if self.model is not None:
            embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
            return embedding[0].astype(np.float32)

        embeddings = self._fallback_embeddings([query])
        return embeddings[0]

    def _fallback_embeddings(self, texts):
        """Generates deterministic unit vector embeddings based on text hash for offline testing."""
        arr = []
        for text in texts:
            seed = sum(ord(c) for c in text) % (2**32)
            rng = np.random.RandomState(seed)
            vec = rng.randn(self.dimension).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            arr.append(vec)
        return np.array(arr, dtype=np.float32)

def get_embedding_service():
    """Singleton getter for EmbeddingService."""
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        _EMBEDDER_INSTANCE = EmbeddingService()
    return _EMBEDDER_INSTANCE
