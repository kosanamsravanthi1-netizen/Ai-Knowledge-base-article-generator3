<!-- Title: Django Documentation — Views and HTTP Request Handling -->
<!-- Category: django -->
<!-- Section: View Layer -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/http/views/ -->

# Django Views

A view function, or view for short, is a Python function (or class) that takes a Web request and returns a Web response. This response can be the HTML contents of a Web page, or a redirect, or a 404 error, or an XML document, or an image, or JSON data.

## Function-Based Views (FBVs)
Function-based views are straightforward Python functions that take an `HttpRequest` object as their first argument and return an `HttpResponse` object.

```python
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Article

def article_list(request):
    articles = Article.objects.filter(is_active=True)
    return render(request, 'articles/list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return JsonResponse({
        'id': article.id,
        'title': article.title,
        'content': article.content
    })
```

## Class-Based Views (CBVs)
Class-based views provide an alternative way to implement views as Python objects instead of functions. They provide structured reusability through inheritance and mixins.

```python
from django.views.generic import ListView, DetailView
from .models import Article

class ArticleListView(ListView):
    model = Article
    template_name = 'articles/list.html'
    context_object_name = 'articles'
    queryset = Article.objects.filter(is_active=True)
```

## Shortcuts and Utility Functions
- `render(request, template_name, context)`: Combines a template with a context dictionary and returns an `HttpResponse`.
- `redirect(to)`: Returns an `HttpResponseRedirect` to the appropriate URL.
- `get_object_or_404(klass, *args, **kwargs)`: Calls `get()` on a given model manager, but raises `Http404` instead of `DoesNotExist`.
