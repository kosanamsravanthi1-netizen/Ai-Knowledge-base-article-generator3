from .domain_classifier import DomainClassifier
from .retriever import Retriever
from .prompts import RAGPrompts
from .llm import get_llm_client

class RAGPipeline:
    """Complete RAG Pipeline orchestrator."""

    def __init__(self):
        self.retriever = Retriever()
        self.llm_client = get_llm_client()

    def process_question(self, question: str) -> dict:
        """
        Processes a user question through the complete RAG pipeline.

        Returns dict:
        {
            "answer": str,
            "sources": list of dicts [{"title", "section", "url"}],
            "domain": str ('python' | 'django' | 'out_of_domain'),
            "is_grounded": bool,
            "similarity_score": float
        }
        """
        if not question or not question.strip():
            return {
                "answer": "Please ask a question related to Python or Django.",
                "sources": [],
                "domain": "out_of_domain",
                "is_grounded": False,
                "similarity_score": 0.0
            }

        cleaned_question = question.strip()

        # Step 1: Domain Classification
        classification = DomainClassifier.classify(cleaned_question)
        if not classification["is_in_domain"]:
            return {
                "answer": RAGPrompts.OUT_OF_DOMAIN_RESPONSE,
                "sources": [],
                "domain": "out_of_domain",
                "is_grounded": False,
                "similarity_score": 0.0
            }

        domain = classification["domain"]

        # Step 2: Semantic FAISS Retrieval
        retrieval_result = self.retriever.retrieve(cleaned_question)
        chunks = retrieval_result["chunks"]
        sources = retrieval_result["sources"]
        max_score = retrieval_result["max_score"]
        meets_threshold = retrieval_result["meets_threshold"]

        # Step 3: Check if context is adequate
        if not chunks or not meets_threshold:
            # If FAISS returns empty or low relevance score
            user_prompt = RAGPrompts.build_user_prompt(cleaned_question, [])
            answer = self.llm_client.generate(user_prompt)
            if "## Documentation Sources" not in answer and sources:
                answer += "\n\n## Documentation Sources\n" + "\n".join([f"- [{s['title']} — {s['section']}]({s['url']})" for s in sources])

            return {
                "answer": answer,
                "sources": sources,
                "domain": domain,
                "is_grounded": False,
                "similarity_score": max_score
            }

        # Step 4: Build Grounded System & User Prompt
        user_prompt = RAGPrompts.build_user_prompt(cleaned_question, chunks)

        # Step 5: LLM Generation
        raw_answer = self.llm_client.generate(user_prompt)

        # Step 6: Format Documentation Sources in Answer if missing
        formatted_answer = raw_answer
        if "## Documentation Sources" not in formatted_answer and sources:
            source_lines = ["\n\n## Documentation Sources"]
            for src in sources:
                source_lines.append(f"- **[{src['title']}]({src['url']})** — *{src['section']}*")
            formatted_answer += "\n" + "\n".join(source_lines)

        return {
            "answer": formatted_answer,
            "sources": sources,
            "domain": domain,
            "is_grounded": True,
            "similarity_score": max_score
        }

_PIPELINE_INSTANCE = None

def get_rag_pipeline():
    """Singleton getter for RAGPipeline."""
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        _PIPELINE_INSTANCE = RAGPipeline()
    return _PIPELINE_INSTANCE
