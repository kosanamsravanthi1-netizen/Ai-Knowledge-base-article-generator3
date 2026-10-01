from rest_framework import serializers
from .models import Document, DocumentChunk, Conversation, Message, Feedback

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_id', 'content', 'metadata', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.IntegerField(source='chunks.count', read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'category', 'source_url', 'file_type', 'chunk_count', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'sources', 'domain', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(source='messages.count', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'messages']


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=True)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'conversation', 'message', 'rating', 'comment', 'created_at']
