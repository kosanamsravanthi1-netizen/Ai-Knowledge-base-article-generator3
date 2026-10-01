# AI-Powered Python & Django Knowledge Assistant (RAG)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django 5.0](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![FAISS](https://img.shields.io/badge/VectorDB-FAISS-orange.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-style, documentation-grounded **Retrieval-Augmented Generation (RAG)** web application designed to answer complex Python and Django questions using official documentation as its primary knowledge source.

---

## 1. Project Overview

This project implements a full RAG pipeline for Python and Django documentation. Unlike standard fine-tuning or zero-shot LLM queries, this application:
1. **Ingests, cleans, and chunks** official Python and Django documentation.
2. **Generates vector embeddings** using `sentence-transformers` (`all-MiniLM-L6-v2`).
3. **Indexes vectors** locally using **FAISS** (Facebook AI Similarity Search) with cosine similarity.
4. **Performs real-time semantic retrieval** on user questions.
5. **Enforces out-of-domain detection** (politely rejecting questions on Java, React, Photoshop, etc.).
6. **Constructs grounded system prompts** and queries the **Groq API** (`llama-3.3-70b-versatile`) with offline RAG fallback.
7. **Renders clean Markdown answers** complete with executable Python/Django code blocks and clickable source citations.

---

## 2. Key Features

- **Documentation-Grounded Answers:** Eliminates LLM hallucinations by passing retrieved documentation context directly into the prompt.
- **Out-of-Domain Guardrails:** Automatically detects non-Python/Django queries and responds with domain boundaries.
- **FAISS Vector Persistence:** High-performance vector database with disk index persistence (`index.faiss` and `metadata.json`).
- **Groq LLM Integration & Offline Fallback:** Configurable Groq API integration with an intelligent offline RAG synthesizer if the API key is not configured.
- **Sleek Single Page Application UI:** Built with pure HTML5, Vanilla CSS, and Vanilla JavaScript (No React/Vue/Streamlit dependency).
- **Session & History Persistence:** Full chat history saved via Django REST Framework & Django ORM.
- **Clickable Documentation Citations:** Every grounded answer attributes its exact documentation sources with direct URL links.
- **Export & Feedback Controls:** Download conversations as `.txt` files and rate answer quality.

---

## 3. Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Fetch API, Marked.js (Markdown parser), FontAwesome icons.
- **Backend:** Python 3.12, Django 5.0, Django REST Framework (DRF), Django ORM.
- **Vector Database:** FAISS (`faiss-cpu`) FlatIP Index with L2 normalized cosine similarity.
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`).
- **LLM Provider:** Groq API (`llama-3.3-70b-versatile` / OpenAI-compatible endpoint).
- **Database:** SQLite3 (development) / PostgreSQL ready.

---

## 4. Architecture Diagram

```
User Question
      ↓
[ Domain Classifier ] ──(Out of Domain)──> "Outside supported Python/Django knowledge base."
      ↓ (In Domain)
[ SentenceTransformer Embedder ]
      ↓ Query Vector
[ FAISS Vector Store ]
      ↓ Similarity Search (Top-K = 5, Threshold = 0.35)
[ Retrieved Documentation Chunks + Metadata ]
      ↓
[ Prompt Construction (System Protection + Context + User Query) ]
      ↓
[ Groq LLM Generation / Offline Synthesizer ]
      ↓
[ Grounded Answer + Clickable Sources ] ──> Django REST API ──> Modern HTML/CSS/JS UI
```

---

## 5. Directory Structure

```
AI Knowledge Base Article generator/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── README.md
│
├── config/                  # Django project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── assistant/               # Main Django application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── rag/                     # Modular RAG Engine
│   ├── __init__.py
│   ├── document_loader.py   # Markdown, HTML, TXT, PDF parser
│   ├── text_processor.py   # Text cleaner & normalization
│   ├── chunker.py          # Recursive text splitter
│   ├── embeddings.py       # SentenceTransformers wrapper
│   ├── vector_store.py     # FAISS vector store & metadata sidecar
│   ├── domain_classifier.py# Python/Django vs Out-of-Domain detector
│   ├── retriever.py        # Vector similarity search & threshold filter
│   ├── llm.py              # Groq API client & fallback synthesizer
│   ├── prompts.py          # System prompt templates
│   └── pipeline.py         # Complete RAG orchestrator
│
├── documents/               # Documentation Knowledge Base
│   ├── python/             # Python documentation files (.md, .txt, .html)
│   └── django/             # Django documentation files (.md, .txt, .html)
│
├── vector_store/            # Persisted FAISS index files (index.faiss, metadata.json)
├── templates/               # HTML5 Single Page Application template
│   └── index.html
│
└── static/                  # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## 6. Installation & Setup

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### Step 1: Clone & Setup Virtual Environment (Windows PowerShell)

```powershell
# Create virtual environment
python -m venv env

# Activate virtual environment
env\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set your Groq API Key (Optional — system works offline without it):

```env
SECRET_KEY=django-insecure-rag-assistant-key-change-in-production-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=all-MiniLM-L6-v2

VECTOR_DB_PATH=vector_store
TOP_K=5
SIMILARITY_THRESHOLD=0.35
```

---

## 7. Database Migration & Document Ingestion

### Step 1: Run Django Database Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Execute Document Ingestion Command

Run the custom management command to load documents, generate embeddings, and build the FAISS index:

```powershell
python manage.py ingest_docs
```

To filter by category:
```powershell
python manage.py ingest_docs --source python
python manage.py ingest_docs --source django
```

*Console Output:*
```
Starting Documentation Ingestion Pipeline...
Loading documentation files...
Found 14 documentation file(s).
Cleaning text and creating semantic chunks...
Created 68 text chunk(s).
Generating vector embeddings via sentence-transformers...
Building FAISS vector index...
Saved FAISS vector index with 68 vectors to vector_store
============================================================
Ingestion completed successfully! Total indexed vectors: 68
============================================================
```

---

## 8. Running the Application

Start the Django development server:

```powershell
python manage.py runserver
```

Open your browser and navigate to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 9. API Documentation

### `POST /api/ask/`
Submits a question to the RAG pipeline.

**Request:**
```json
{
  "question": "What is a Django model?",
  "conversation_id": null
}
```

**Response:**
```json
{
  "question": "What is a Django model?",
  "answer": "## Explanation\nA Django model is the single, definitive source of information about your data...\n\n## Code\n```python\nclass Article(models.Model):\n    title = models.CharField(max_length=200)\n```",
  "sources": [
    {
      "title": "Django Documentation — Models and Database Schema",
      "section": "Model Layer",
      "url": "https://docs.djangoproject.com/en/5.0/topics/db/models/"
    }
  ],
  "domain": "django",
  "is_grounded": true,
  "similarity_score": 0.7241,
  "conversation_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message_id": 1
}
```

### Additional Endpoints:
- `GET /api/conversations/` - List all chat sessions
- `GET /api/conversations/<id>/` - Retrieve conversation history
- `DELETE /api/conversations/<id>/` - Delete conversation session
- `POST /api/feedback/` - Submit feedback rating
- `GET /api/status/` - Check vector index health

---

## 10. Running Automated Tests

Run the test suite covering models, RAG retrieval, domain classification, and API endpoints:

```powershell
python manage.py test assistant
```

---

## 11. Troubleshooting

1. **`ModuleNotFoundError: No module named 'faiss'`**
   - Ensure `faiss-cpu` is installed inside your activated virtual environment: `pip install faiss-cpu`.
2. **Offline Mode / No Groq API Key**
   - If `GROQ_API_KEY` is blank in `.env`, the system automatically activates its built-in offline RAG synthesizer.
3. **No Search Results Found**
   - Re-run `python manage.py ingest_docs` to build the FAISS index.

---

## 12. License & Author

Developed for GenAI College Project Demonstration. MIT License.
