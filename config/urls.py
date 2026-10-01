from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from assistant.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assistant.urls')),
    path('', IndexView.as_view(), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
