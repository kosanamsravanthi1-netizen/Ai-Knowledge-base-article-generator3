<!-- Title: Django Documentation — URL Routing and Dispatcher -->
<!-- Category: django -->
<!-- Section: URL Dispatcher -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/http/urls/ -->

# Django URL Routing

A clean, elegant URL scheme is an important detail in a high-quality web application. Django lets you design URLs however you want, with no framework limitations.

## URLconf Configuration
To route URLs to views, Django uses Python modules called `URLconfs` (URL configurations). The main configuration is specified in `ROOT_URLCONF` in `settings.py`.

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assistant.urls')),
    path('', include('web.urls')),
]
```

## Path Converters
Django URL patterns can capture parameters from URLs using path converters:
- `<int:pk>`: Matches zero or any positive integer.
- `<str:name>`: Matches any non-empty string, excluding the path separator `'/'`.
- `<slug:slug>`: Matches any slug string consisting of ASCII letters, numbers, hyphens, or underscores.
- `<uuid:id>`: Matches a formatted UUID.

```python
from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
]
```

## Reverse URL Resolution
Django provides tools to generate URLs based on the view function name and parameters, eliminating hardcoded URLs in templates and views.
- In Python code: `reverse('articles:article_detail', kwargs={'pk': 5})`
- In HTML Templates: `{% url 'articles:article_detail' article.id %}`
