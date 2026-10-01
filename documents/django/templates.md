<!-- Title: Django Documentation — Templates and DTL System -->
<!-- Category: django -->
<!-- Section: Template Layer -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/templates/ -->

# Django Templates

Django's template engine provides a powerful syntax for rendering dynamic HTML documents while maintaining a clean separation between business logic and visual layout.

## Template Syntax Basics
1. **Variables**: Rendered with double curly braces `{{ variable_name }}`.
2. **Tags**: Control structures, loops, and logic rendered with curly braces and percent signs `{% tag_name %}`.
3. **Filters**: Transform variable values using pipe symbol `{{ variable|filter_name }}`.

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title|title }}</title>
</head>
<body>
    <h1>Welcome, {{ user.username|default:"Guest" }}!</h1>
    
    {% if articles %}
        <ul>
        {% for article in articles %}
            <li>
                <a href="{% url 'article_detail' article.id %}">{{ article.title }}</a>
                <span>({{ article.published_date|date:"Y-m-d" }})</span>
            </li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No articles available at this time.</p>
    {% endif %}
</body>
</html>
```

## Template Inheritance
Template inheritance allows you to build a base "skeleton" template that contains all common elements of your site and defines blocks that child templates can override.

### Base Template (`base.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <header>Nav Bar</header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### Child Template (`index.html`)
```html
{% extends "base.html" %}

{% block title %}Home - AI Assistant{% endblock %}

{% block content %}
    <h2>Dashboard</h2>
    <p>Welcome to the AI Knowledge Assistant.</p>
{% endblock %}
```
