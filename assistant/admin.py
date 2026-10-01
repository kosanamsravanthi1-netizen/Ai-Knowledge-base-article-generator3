from django.contrib import admin
from .models import Document, DocumentChunk, Conversation, Message, Feedback

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'file_type', 'source_url', 'created_at')
    list_filter = ('category', 'file_type', 'created_at')
    search_fields = ('title', 'source_url', 'file_path')


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('chunk_id', 'document', 'short_content', 'created_at')
    list_filter = ('document__category', 'created_at')
    search_fields = ('chunk_id', 'content', 'document__title')

    def short_content(self, obj):
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content
    short_content.short_description = "Content Preview"


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content', 'sources', 'domain', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title', 'id')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'domain', 'created_at')
    list_filter = ('role', 'domain', 'created_at')
    search_fields = ('content', 'conversation__title')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating', 'comment', 'conversation', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)
