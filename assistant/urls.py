from django.urls import path
from .views import (
    AskQuestionView, ConversationListView, ConversationDetailView,
    FeedbackView, StatusView
)

app_name = 'assistant'

urlpatterns = [
    path('ask/', AskQuestionView.as_view(), name='ask'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<uuid:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('status/', StatusView.as_view(), name='status'),
]
