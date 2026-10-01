import logging
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Conversation, Message, Feedback, Document, DocumentChunk
from .serializers import (
    ConversationSerializer, MessageSerializer, AskQuestionSerializer,
    FeedbackSerializer, DocumentSerializer
)
from rag.pipeline import get_rag_pipeline
from rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    """Renders main single-page web app template."""
    template_name = "index.html"


class AskQuestionView(APIView):
    """API endpoint to receive a user question and return a documentation-grounded answer."""

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid question input", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question'].strip()
        conv_id = serializer.validated_data.get('conversation_id')

        if not question:
            return Response({"error": "Question cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Retrieve or Create Conversation Session
            conversation = None
            if conv_id:
                try:
                    conversation = Conversation.objects.get(id=conv_id)
                except Conversation.DoesNotExist:
                    conversation = None

            if not conversation:
                # Create default conversation title from first few words of question
                title = question[:40] + ("..." if len(question) > 40 else "")
                conversation = Conversation.objects.create(title=title)
            elif conversation.messages.count() == 0:
                title = question[:40] + ("..." if len(question) > 40 else "")
                conversation.title = title
                conversation.save()

            # 2. Record User Message in Database
            user_msg = Message.objects.create(
                conversation=conversation,
                role='user',
                content=question,
                domain='user_query'
            )

            # 3. Execute RAG Pipeline
            pipeline = get_rag_pipeline()
            result = pipeline.process_question(question)

            # 4. Record Assistant Message in Database
            assistant_msg = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=result['answer'],
                sources=result['sources'],
                domain=result['domain']
            )

            # Update conversation timestamp
            conversation.save()

            return Response({
                "question": question,
                "answer": result['answer'],
                "sources": result['sources'],
                "domain": result['domain'],
                "is_grounded": result['is_grounded'],
                "similarity_score": result['similarity_score'],
                "conversation_id": str(conversation.id),
                "message_id": assistant_msg.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing RAG ask request: {e}", exc_info=True)
            return Response({
                "error": "Sorry, I couldn't process your question right now. Please try again.",
                "details": str(e) if request.GET.get('debug') else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationListView(APIView):
    """List all conversations or create a new conversation."""

    def get(self, request):
        conversations = Conversation.objects.all().order_by('-updated_at')
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        title = request.data.get('title', 'New Conversation')
        conversation = Conversation.objects.create(title=title)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    """Retrieve or delete a single conversation."""

    def get(self, request, pk):
        try:
            conversation = Conversation.objects.get(id=pk)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            conversation = Conversation.objects.get(id=pk)
            conversation.delete()
            return Response({"message": "Conversation deleted successfully"}, status=status.HTTP_200_OK)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)


class FeedbackView(APIView):
    """Record user feedback rating/comments for an AI answer."""

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Thank you for your feedback!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatusView(APIView):
    """Returns RAG System health metrics and index stats."""

    def get(self, request):
        doc_count = Document.objects.count()
        chunk_count = DocumentChunk.objects.count()
        vector_store = get_vector_store()
        vector_count = vector_store.index.ntotal if vector_store.index else 0

        return Response({
            "status": "online",
            "documents_ingested": doc_count,
            "document_chunks": chunk_count,
            "faiss_vector_count": vector_count,
            "python_docs": Document.objects.filter(category='python').count(),
            "django_docs": Document.objects.filter(category='django').count(),
        }, status=status.HTTP_200_OK)
