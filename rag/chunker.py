import uuid

class Chunk:
    """Represents a text chunk extracted from a document with associated metadata."""
    def __init__(self, chunk_id, content, metadata):
        self.chunk_id = chunk_id
        self.content = content
        self.metadata = metadata # Dict: title, section, source_url, category, doc_id

class RecursiveTextSplitter:
    """
    Splits text into chunks by attempting to break on paragraph boundaries,
    sentence boundaries, and words while observing chunk_size and chunk_overlap.
    """

    def __init__(self, chunk_size=600, chunk_overlap=120, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_document(self, loaded_doc):
        """Splits a LoadedDocument into a list of Chunk objects."""
        raw_chunks = self._split_text(loaded_doc.content)
        doc_chunks = []

        for idx, text in enumerate(raw_chunks):
            if not text.strip():
                continue

            chunk_id = f"{loaded_doc.category}_{uuid.uuid4().hex[:8]}_{idx}"
            metadata = {
                "chunk_id": chunk_id,
                "title": loaded_doc.title,
                "section": loaded_doc.section,
                "source_url": loaded_doc.source_url,
                "category": loaded_doc.category,
                "file_path": loaded_doc.file_path,
                "chunk_index": idx
            }

            doc_chunks.append(Chunk(
                chunk_id=chunk_id,
                content=text.strip(),
                metadata=metadata
            ))

        return doc_chunks

    def _split_text(self, text):
        """Recursive splitting implementation."""
        if len(text) <= self.chunk_size:
            return [text]

        # Determine best separator
        separator = self.separators[-1]
        for s in self.separators:
            if s == "":
                separator = ""
                break
            if s in text:
                separator = s
                break

        splits = text.split(separator) if separator != "" else list(text)
        final_chunks = []
        current_chunk = []
        current_len = 0

        for split in splits:
            split_len = len(split) + len(separator)
            if current_len + split_len > self.chunk_size and current_chunk:
                joined = separator.join(current_chunk)
                final_chunks.append(joined)

                # Maintain overlap
                overlap_len = 0
                overlap_chunk = []
                for item in reversed(current_chunk):
                    if overlap_len + len(item) <= self.chunk_overlap:
                        overlap_chunk.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break
                current_chunk = overlap_chunk
                current_len = sum(len(x) for x in current_chunk)

            current_chunk.append(split)
            current_len += split_len

        if current_chunk:
            final_chunks.append(separator.join(current_chunk))

        return final_chunks
