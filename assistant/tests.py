import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assistant.models import Conversation, Message, Document, DocumentChunk, Feedback
from rag.domain_classifier import DomainClassifier
from rag.chunker import RecursiveTextSplitter, Chunk
from rag.document_loader import LoadedDocument
from rag.retriever import Retriever

class ModelTests(TestCase):
    """Test suite for Django Database Models."""

    def test_create_document_and_chunk(self):
        doc = Document.objects.create(
            title="Python Tutorial",
            category="python",
            source_url="https://docs.python.org/3/",
            file_path="documents/python/functions.md"
        )
        self.assertEqual(doc.category, "python")
        self.assertIn("Python Tutorial", str(doc))

        chunk = DocumentChunk.objects.create(
            document=doc,
            chunk_id="py_12345",
            content="def greet(): pass",
            metadata={"title": doc.title}
        )
        self.assertEqual(chunk.document, doc)
        self.assertEqual(doc.chunks.count(), 1)

    def test_conversation_and_messages(self):
        conv = Conversation.objects.create(title="Django Routing Test")
        self.assertTrue(isinstance(conv.id, uuid.UUID))

        msg_user = Message.objects.create(
            conversation=conv,
            role="user",
            content="How does URL routing work in Django?"
        )
        msg_assistant = Message.objects.create(
            conversation=conv,
            role="assistant",
            content="Django uses URLconfs.",
            domain="django",
            sources=[{"title": "Django Docs", "url": "https://docs.djangoproject.com/"}]
        )

        self.assertEqual(conv.messages.count(), 2)
        self.assertEqual(msg_user.role, "user")
        self.assertEqual(msg_assistant.domain, "django")


class DomainClassifierTests(TestCase):
    """Test suite for Out-of-Domain Detection."""

    def test_python_questions(self):
        questions = [
            "What is a Python function?",
            "Explain Python decorators.",
            "What is exception handling in Python?",
            "What is a Python class?",
            "Explain list comprehensions."
        ]
        for q in questions:
            res = DomainClassifier.classify(q)
            self.assertTrue(res["is_in_domain"], f"Failed on question: {q}")
            self.assertEqual(res["domain"], "python")

    def test_django_questions(self):
        questions = [
            "What is a Django model?",
            "What is Django ORM?",
            "How do Django views work?",
            "How does URL routing work in Django?",
            "What are Django templates?"
        ]
        for q in questions:
            res = DomainClassifier.classify(q)
            self.assertTrue(res["is_in_domain"], f"Failed on question: {q}")
            self.assertEqual(res["domain"], "django")

    def test_out_of_domain_questions(self):
        questions = [
            "How do I use React useState hook?",
            "Explain Java garbage collection.",
            "How do I create a layer in Photoshop?",
            "What is C++ pointer arithmetic?",
            "How do I install Node.js?"
        ]
        for q in questions:
            res = DomainClassifier.classify(q)
            self.assertFalse(res["is_in_domain"], f"Failed to reject out-of-domain question: {q}")
            self.assertEqual(res["domain"], "out_of_domain")


class RAGChunkerTests(TestCase):
    """Test suite for RAG Chunker."""

    def test_text_splitting(self):
        doc = LoadedDocument(
            title="Sample Doc",
            content="Line 1\n\nLine 2\n\nLine 3\n\n" * 20,
            category="python",
            section="Core",
            source_url="http://example.com"
        )
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_document(doc)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0].metadata['category'], 'python')


class APIEndpointTests(APITestCase):
    """Integration test suite for REST API endpoints."""

    def test_ask_valid_question(self):
        url = reverse('assistant:ask')
        payload = {"question": "What is a Python function?"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)
        self.assertIn("domain", response.data)
        self.assertIn("conversation_id", response.data)

    def test_ask_out_of_domain_question(self):
        url = reverse('assistant:ask')
        payload = {"question": "How do React hooks work?"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["domain"], "out_of_domain")
        self.assertIn("outside the supported Python and Django knowledge base", response.data["answer"])

    def test_ask_empty_question(self):
        url = reverse('assistant:ask')
        payload = {"question": "   "}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversations_api(self):
        list_url = reverse('assistant:conversation_list')
        res = self.client.get(list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        conv = Conversation.objects.create(title="Test Conv")
        detail_url = reverse('assistant:conversation_detail', kwargs={'pk': conv.id})
        res_detail = self.client.get(detail_url)
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data['title'], "Test Conv")

        res_delete = self.client.delete(detail_url)
        self.assertEqual(res_delete.status_code, status.HTTP_200_OK)
        self.assertFalse(Conversation.objects.filter(id=conv.id).exists())

    def test_status_api(self):
        url = reverse('assistant:status')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("status", res.data)
        self.assertEqual(res.data["status"], "online")
