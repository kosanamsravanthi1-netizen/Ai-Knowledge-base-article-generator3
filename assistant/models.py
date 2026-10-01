import uuid
from django.db import models

class Document(models.Model):
    """Stores documentation source metadata."""
    CATEGORY_CHOICES = [
        ('python', 'Python Documentation'),
        ('django', 'Django Documentation'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='python')
    source_url = models.URLField(max_length=500, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_type = models.CharField(max_length=20, default='markdown')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"


class DocumentChunk(models.Model):
    """Stores text chunks extracted from documentation files."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_id = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', 'id']

    def __str__(self):
        return f"Chunk {self.chunk_id} ({self.document.title})"


class Conversation(models.Model):
    """Represents a user chat session."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({str(self.id)[:8]})"


class Message(models.Model):
    """Stores individual user questions and AI responses within a conversation."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    domain = models.CharField(max_length=50, default='python')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.upper()} message in {self.conversation.title}"


class Feedback(models.Model):
    """Stores user feedback on AI responses."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(default=5) # 1 to 5 or +1 / -1
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback {self.rating}/5 at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
