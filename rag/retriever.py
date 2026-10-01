from django.conf import settings
from .embeddings import get_embedding_service
from .vector_store import get_vector_store

class Retriever:
    """Handles semantic vector retrieval and similarity threshold filtering."""

    def __init__(self, top_k=None, threshold=None):
        self.top_k = top_k or getattr(settings, 'TOP_K', 5)
        self.threshold = threshold if threshold is not None else getattr(settings, 'SIMILARITY_THRESHOLD', 0.35)
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()

    def retrieve(self, question: str):
        """
        Retrieves context chunks matching question.
        Returns dict containing:
            - chunks: list of chunk item dicts
            - sources: formatted list of unique source citation objects
            - max_score: highest similarity score found
            - meets_threshold: boolean flag whether results satisfy threshold
        """
        if not question or not question.strip():
            return {
                "chunks": [],
                "sources": [],
                "max_score": 0.0,
                "meets_threshold": False
            }

        # Generate query vector
        query_vec = self.embedding_service.generate_query_embedding(question)

        # Search FAISS index
        raw_results = self.vector_store.search(query_vec, top_k=self.top_k)

        if not raw_results:
            return {
                "chunks": [],
                "sources": [],
                "max_score": 0.0,
                "meets_threshold": False
            }

        max_score = max(score for _, score in raw_results)
        meets_threshold = max_score >= self.threshold

        valid_chunks = []
        sources_map = {}

        for item, score in raw_results:
            # Filter low similarity results if required
            if score >= self.threshold or not meets_threshold:
                meta = item.get('metadata', {})
                valid_chunks.append({
                    "chunk_id": item.get('chunk_id'),
                    "content": item.get('content'),
                    "title": meta.get('title', 'Documentation'),
                    "section": meta.get('section', 'General'),
                    "source_url": meta.get('source_url', '#'),
                    "category": meta.get('category', 'python'),
                    "score": score
                })

                # Deduplicate source citations
                key = (meta.get('title'), meta.get('section'))
                if key not in sources_map:
                    sources_map[key] = {
                        "title": meta.get('title', 'Documentation'),
                        "section": meta.get('section', 'General'),
                        "url": meta.get('source_url', '#'),
                        "category": meta.get('category', 'python')
                    }

        return {
            "chunks": valid_chunks,
            "sources": list(sources_map.values()),
            "max_score": max_score,
            "meets_threshold": meets_threshold
        }
