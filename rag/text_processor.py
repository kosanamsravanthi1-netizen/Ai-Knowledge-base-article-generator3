import re

class TextProcessor:
    """Text cleaning and normalization utilities for RAG document processing."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Replace excessive multiple blank lines (3+ into 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Replace trailing spaces on lines
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    @staticmethod
    def extract_headings(text: str) -> list:
        """Extracts Markdown headings (#, ##, ###) for structure awareness."""
        return re.findall(r'^(#{1,6})\s+(.*)$', text, flags=re.MULTILINE)
