import sys
from django.core.management.base import BaseCommand
from assistant.models import Document, DocumentChunk
from rag.document_loader import DocumentLoader
from rag.text_processor import TextProcessor
from rag.chunker import RecursiveTextSplitter
from rag.embeddings import get_embedding_service
from rag.vector_store import get_vector_store

class Command(BaseCommand):
    help = 'Ingests documentation files, creates chunks, computes embeddings, and builds FAISS vector index.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Filter ingestion source: "python" or "django"',
            default=None
        )

    def handle(self, *args, **options):
        source = options.get('source')

        self.stdout.write(self.style.MIGRATE_HEADING("Starting Documentation Ingestion Pipeline..."))

        if source:
            source = source.lower()
            self.stdout.write(f"Target category filter: {source}")

        # Step 1: Load Documents
        self.stdout.write("Loading documentation files...")
        loader = DocumentLoader()
        loaded_docs = loader.load_all_documents(target_category=source)

        if not loaded_docs:
            self.stdout.write(self.style.WARNING("No documentation files found in documents/ directory."))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(loaded_docs)} documentation file(s)."))

        # Step 2: Clean & Chunk Documents
        self.stdout.write("Cleaning text and creating semantic chunks...")
        splitter = RecursiveTextSplitter(chunk_size=600, chunk_overlap=120)
        all_chunks = []
        doc_records = []

        # Clear existing DB models if ingesting full set
        if not source:
            DocumentChunk.objects.all().delete()
            Document.objects.all().delete()
            vector_store = get_vector_store()
            vector_store.clear()
        else:
            Document.objects.filter(category=source).delete()

        vector_store = get_vector_store()

        for loaded_doc in loaded_docs:
            # Clean content
            cleaned_text = TextProcessor.clean_text(loaded_doc.content)
            loaded_doc.content = cleaned_text

            # Create DB Document record
            doc_obj = Document.objects.create(
                title=loaded_doc.title,
                category=loaded_doc.category,
                source_url=loaded_doc.source_url,
                file_path=loaded_doc.file_path,
                file_type=loaded_doc.file_path.split('.')[-1] if '.' in loaded_doc.file_path else 'markdown'
            )

            # Chunk document
            chunks = splitter.split_document(loaded_doc)

            for chunk in chunks:
                all_chunks.append(chunk)
                # Store chunk in DB
                DocumentChunk.objects.create(
                    document=doc_obj,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    metadata=chunk.metadata
                )

        self.stdout.write(self.style.SUCCESS(f"Created {len(all_chunks)} text chunk(s)."))

        if not all_chunks:
            self.stdout.write(self.style.WARNING("No valid chunks created."))
            return

        # Step 3: Generate Embeddings
        self.stdout.write("Generating vector embeddings via sentence-transformers...")
        embedder = get_embedding_service()
        chunk_texts = [c.content for c in all_chunks]
        embeddings = embedder.generate_embeddings(chunk_texts)

        # Step 4: Index in FAISS
        self.stdout.write("Building FAISS vector index...")
        vector_store.add_chunks(all_chunks, embeddings)
        vector_store.save()

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"Ingestion completed successfully! Total indexed vectors: {vector_store.index.ntotal}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
