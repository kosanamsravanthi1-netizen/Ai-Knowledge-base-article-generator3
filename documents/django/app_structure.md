<!-- Title: Django Documentation — Creating Apps and Project Architecture -->
<!-- Category: django -->
<!-- Section: Architecture & Structure -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/intro/tutorial01/ -->

# Creating Applications in Django

A Django project is a collection of configurations and apps for a given website. An app is a web application that does something — e.g., a blog system, a database of public records, or a simple poll app.

## Creating a Django App
To create a new app within a Django project, use the `startapp` management command:

```bash
python manage.py startapp assistant
```

## Standard App Directory Layout
```
assistant/
│── admin.py        # Django Admin registration
│── apps.py         # App configuration metadata
│── models.py       # Database models
│── serializers.py  # DRF serializers (for API representation)
│── tests.py        # Unit and integration test suites
│── urls.py         # App-specific URL routes
└── views.py        # Business logic & request handlers
```

## Registering Apps in `settings.py`
To include the app in your Django project, add its configuration class to the `INSTALLED_APPS` setting in `config/settings.py`.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party packages
    'rest_framework',
    'corsheaders',

    # Local apps
    'assistant.apps.AssistantConfig',
]
```
