<!-- Title: Django Documentation — Django ORM and QuerySets -->
<!-- Category: django -->
<!-- Section: Database Queries -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/db/queries/ -->

# Django ORM and QuerySets

The Django Object-Relational Mapper (ORM) allows developers to interact with database models using Python code rather than writing raw SQL queries.

## Creating and Saving Objects
```python
from assistant.models import Conversation, Message

# Option 1: Instantiate and save
conv = Conversation(title="Python Basics")
conv.save()

# Option 2: Use Manager create() method directly
conv = Conversation.objects.create(title="Django Views")
```

## Retrieving Objects (QuerySets)
QuerySets represent a collection of objects from your database. They can have zero, one, or many filters.

- `all()`: Retrieves all records.
- `filter(**kwargs)`: Returns a new QuerySet matching given lookup parameters.
- `exclude(**kwargs)`: Returns a new QuerySet excluding records matching parameters.
- `get(**kwargs)`: Returns a single object matching parameters. Raises `DoesNotExist` or `MultipleObjectsReturned`.

```python
# Filtering examples
active_convs = Conversation.objects.filter(title__icontains="Python")
recent_messages = Message.objects.filter(conversation=conv).order_by('-created_at')[:10]
```

## Field Lookups
Field lookups use double underscores `__`:
- `exact`, `iexact`: Exact matching (case-sensitive/insensitive).
- `contains`, `icontains`: Substring test.
- `gt`, `gte`, `lt`, `lte`: Greater than / less than comparisons.
- `in`: Membership test in a list.

```python
# Messages created in the last 7 days
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
recent = Message.objects.filter(created_at__gte=week_ago)
```

## Aggregation and Annotation
Django ORM supports SQL aggregations (`COUNT`, `AVG`, `SUM`, `MAX`, `MIN`).

```python
from django.db.models import Count

conversations_with_counts = Conversation.objects.annotate(msg_count=Count('messages'))
```
