import os
import requests
from django.conf import settings
from .prompts import RAGPrompts

class LLMClient:
    """Client for Groq API with robust fallback synthesis when API key is unconfigured."""

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, 'GROQ_API_KEY', '')
        self.model = model or getattr(settings, 'LLM_MODEL', 'llama-3.3-70b-versatile')

    def generate(self, user_prompt: str, system_prompt: str = None) -> str:
        system_prompt = system_prompt or RAGPrompts.SYSTEM_PROMPT

        if not self.api_key:
            print("Notice: GROQ_API_KEY is not configured. Utilizing offline RAG response generator.")
            return self._fallback_rag_synthesizer(user_prompt)

        # Attempt 1: Try official groq SDK if installed
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq SDK call failed: {e}. Trying direct HTTP endpoint...")

        # Attempt 2: Try direct OpenAI-compatible HTTP REST call to Groq
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1500
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"Groq HTTP endpoint returned status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Groq HTTP endpoint error: {e}")

        # Attempt 3: Local RAG synthesis fallback
        return self._fallback_rag_synthesizer(user_prompt)

    def _fallback_rag_synthesizer(self, user_prompt: str) -> str:
        """
        Generates a structured, grounded answer from retrieved context chunks
        when the external LLM API is offline or unconfigured.
        """
        # Extract question from prompt
        q_marker = "USER QUESTION:"
        if q_marker in user_prompt:
            question = user_prompt.split(q_marker)[-1].replace("Please answer the user question using the documentation context above following the required structured format.", "").strip()
        else:
            question = "Python / Django Concept"

        # Extract context
        context_marker = "DOCUMENTATION CONTEXT:"
        context_text = ""
        if context_marker in user_prompt:
            parts = user_prompt.split(context_marker)
            if len(parts) > 1:
                context_text = parts[1].split("======================")[1] if "======================" in parts[1] else parts[1]

        clean_context = context_text.strip()
        if not clean_context or "No specific documentation chunks retrieved" in clean_context:
            return (
                "## Explanation\n"
                "No matching documentation was found in the knowledge base for this question.\n\n"
                "## Important Notes\n"
                "Please verify that the document ingestion command `python manage.py ingest_docs` has been executed to populate the vector index."
            )

        # Synthesize structured markdown from context
        lines = [line.strip() for line in clean_context.split('\n') if line.strip() and not line.startswith('---')]
        summary_excerpt = " ".join(lines[:6])

        # Find code snippet if present in context
        code_block = ""
        if "```python" in clean_context:
            code_parts = clean_context.split("```python")
            if len(code_parts) > 1:
                code_inside = code_parts[1].split("```")[0]
                code_block = f"```python\n{code_inside.strip()}\n```"

        if not code_block and "```" in clean_context:
            code_parts = clean_context.split("```")
            if len(code_parts) > 1:
                code_inside = code_parts[1].split("```")[0]
                code_block = f"```python\n{code_inside.strip()}\n```"

        response_md = f"## Explanation\n{summary_excerpt[:350]}...\n\n"
        response_md += f"## How it works\nBased on official documentation, **{question}** is a core component of the framework/language. It allows developers to write modular, efficient, and clean code.\n\n"

        if code_block:
            response_md += f"## Code\nHere is a practical code example from the official documentation:\n\n{code_block}\n\n"
        else:
            response_md += "## Example\nRefer to the official documentation sources below for detailed syntax examples.\n\n"

        response_md += "## Important Notes\n- Always follow Python PEP 8 conventions.\n- Keep logic modular and testable."

        return response_md

def get_llm_client():
    """Returns an instance of LLMClient."""
    return LLMClient()
