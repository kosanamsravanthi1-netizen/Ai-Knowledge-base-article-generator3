import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pypdf

class LoadedDocument:
    """Dataclass holding extracted document content and metadata."""
    def __init__(self, title, content, category, section="General", source_url="", file_path=""):
        self.title = title
        self.content = content
        self.category = category # 'python' or 'django'
        self.section = section
        self.source_url = source_url
        self.file_path = file_path

class DocumentLoader:
    """Loads HTML, Markdown, TXT, and PDF documentation files."""

    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent / "documents"
        else:
            self.base_dir = Path(base_dir)

    def load_all_documents(self, target_category=None):
        """Loads all documents from the base directory or filtered by category ('python'/'django')."""
        documents = []
        if not self.base_dir.exists():
            return documents

        search_dirs = []
        if target_category:
            cat_dir = self.base_dir / target_category
            if cat_dir.exists():
                search_dirs.append(cat_dir)
        else:
            for child in self.base_dir.iterdir():
                if child.is_dir():
                    search_dirs.append(child)

        for dir_path in search_dirs:
            category = dir_path.name.lower()
            for root, _, files in os.walk(dir_path):
                for file_name in files:
                    file_path = Path(root) / file_name
                    doc = self._load_file(file_path, category)
                    if doc and doc.content.strip():
                        documents.append(doc)

        return documents

    def _load_file(self, file_path, category):
        """Internal helper to load and parse a single file based on extension."""
        ext = file_path.suffix.lower()
        try:
            if ext in ['.md', '.txt']:
                return self._load_text_or_markdown(file_path, category)
            elif ext in ['.html', '.htm']:
                return self._load_html(file_path, category)
            elif ext == '.pdf':
                return self._load_pdf(file_path, category)
        except Exception as e:
            print(f"Error loading document {file_path}: {e}")
        return None

    def _load_text_or_markdown(self, file_path, category):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

        title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
        section = "General"
        source_url = f"https://docs.python.org/3/" if category == 'python' else "https://docs.djangoproject.com/en/5.0/"

        # Extract metadata from HTML/MD comments
        meta_title = re.search(r'<!--\s*Title:\s*(.*?)\s*-->', raw_text, re.IGNORECASE)
        meta_section = re.search(r'<!--\s*Section:\s*(.*?)\s*-->', raw_text, re.IGNORECASE)
        meta_url = re.search(r'<!--\s*SourceURL:\s*(.*?)\s*-->', raw_text, re.IGNORECASE)
        meta_category = re.search(r'<!--\s*Category:\s*(.*?)\s*-->', raw_text, re.IGNORECASE)

        if meta_title:
            title = meta_title.group(1).strip()
        if meta_section:
            section = meta_section.group(1).strip()
        if meta_url:
            source_url = meta_url.group(1).strip()
        if meta_category:
            category = meta_category.group(1).strip().lower()

        # Clean metadata header lines from content
        clean_content = re.sub(r'<!--.*?-->', '', raw_text, flags=re.DOTALL).strip()

        return LoadedDocument(
            title=title,
            content=clean_content,
            category=category,
            section=section,
            source_url=source_url,
            file_path=str(file_path)
        )

    def _load_html(self, file_path, category):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Remove script and style tags
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title else file_path.stem.title()
        text_content = soup.get_text(separator='\n')

        return LoadedDocument(
            title=title,
            content=text_content,
            category=category,
            section="HTML Documentation",
            source_url=f"local://{file_path.name}",
            file_path=str(file_path)
        )

    def _load_pdf(self, file_path, category):
        reader = pypdf.PdfReader(str(file_path))
        text_list = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_list.append(extracted)

        content = "\n".join(text_list)
        title = file_path.stem.replace('_', ' ').title()

        return LoadedDocument(
            title=title,
            content=content,
            category=category,
            section="PDF Document",
            source_url=f"local://{file_path.name}",
            file_path=str(file_path)
        )
