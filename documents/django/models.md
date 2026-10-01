<!-- Title: Django Documentation — Models and Database Schema -->
<!-- Category: django -->
<!-- Section: Model Layer -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/db/models/ -->

# Django Models

A Django model is the single, definitive source of information about your data. It contains the essential fields and behaviors of the data you're storing. Generally, each model maps to a single database table.

## Defining a Django Model
Each model is a Python class that subclasses `django.db.models.Model`. Each attribute of the model represents a database column/field.

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
```

## Field Types
Django comes with dozens of built-in field types, including:
- `CharField`: Small to medium-sized strings. Requires `max_length`.
- `TextField`: Large text areas.
- `IntegerField`, `FloatField`, `DecimalField`: Numerical data.
- `DateTimeField`, `DateField`: Date and time handling.
- `BooleanField`: True/False flags.
- `EmailField`, `URLField`: Validated format fields.

## Model Relationships
1. **ForeignKey (Many-to-One)**: Requires `on_delete` parameter (e.g., `models.CASCADE`, `models.SET_NULL`).
2. **ManyToManyField (Many-to-Many)**: Used for symmetrical or multi-association datasets.
3. **OneToOneField (One-to-One)**: Conceptual inheritance or user profiles.

```python
class Category(models.Model):
    name = models.CharField(max_length=100)

class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField('Tag')
```

## Django Migrations
Migrations are Django's way of propagating changes you make to your models into your database schema.
- `python manage.py makemigrations`: Creates new migrations based on detected model changes.
- `python manage.py migrate`: Applies and unapplies migrations to update database tables.
