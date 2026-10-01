import re

class DomainClassifier:
    """Classifies user questions into Python/Django domain vs out-of-domain."""

    # Keywords strictly related to Python & Django
    PYTHON_DJANGO_KEYWORDS = [
        'python', 'django', 'pip', 'virtualenv', 'venv', 'py', 'pythons',
        'decorator', 'decorators', 'list comprehension', 'comprehensions',
        'generator', 'generators', 'docstring', 'init', 'self', 'cls', 'dunder',
        'flask', 'fastapi', 'celery', 'wsggi', 'asgi', 'manage.py', 'settings.py',
        'urls.py', 'views.py', 'models.py', 'queryset', 'querysets', 'orm',
        'db.models', 'httprequest', 'httpresponse', 'modelform', 'templatetag',
        'jinja', 'dtl', 'gunicorn', 'uvicorn', 'pytest', 'unittest', 'pydantic',
        'args', 'kwargs', 'lambda', 'try-except', 'except', 'raise', 'finally',
        'dunder', 'getattr', 'setattr', 'dataclass', 'typing'
    ]

    # Explicitly forbidden / non-domain keywords
    OUT_OF_DOMAIN_KEYWORDS = [
        'java', 'c++', 'c#', 'rust', 'golang', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'node.js', 'express',
        'photoshop', 'illustrator', 'figma', 'excel', 'powerpoint',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'kubernetes', 'docker', 'aws', 'azure', 'gcp', 'terraform',
        'reactjs', 'vuejs', 'angularjs', 'spring boot', 'laravel', 'asp.net',
        'weather', 'politics', 'sports', 'cricket', 'football', 'movie', 'recipe', 'cooking'
    ]

    @classmethod
    def classify(cls, question: str) -> dict:
        """
        Classifies question into 'python', 'django', or 'out_of_domain'.
        Returns dict with keys:
            - is_in_domain (bool)
            - domain (str: 'python', 'django', or 'out_of_domain')
            - confidence (float)
        """
        if not question or not question.strip():
            return {
                "is_in_domain": False,
                "domain": "out_of_domain",
                "confidence": 1.0,
                "reason": "Empty question"
            }

        q_lower = question.lower().strip()

        # Check explicit out-of-domain matches first
        for keyword in cls.OUT_OF_DOMAIN_KEYWORDS:
            kw = keyword.lower()
            if not kw.isalnum():
                pattern = r'(?:\b|\s|^)' + re.escape(kw) + r'(?:\b|\s|$|[^\w])'
            else:
                pattern = r'\b' + re.escape(kw) + r'\b'

            if re.search(pattern, q_lower):
                # Extra check if query explicitly combines with Python/Django (e.g., "Python vs Java")
                if not ('python' in q_lower or 'django' in q_lower):
                    return {
                        "is_in_domain": False,
                        "domain": "out_of_domain",
                        "confidence": 0.95,
                        "reason": f"Detected out-of-domain technology: '{keyword}'"
                    }

        # Check explicit Python / Django matches
        is_django = any(k in q_lower for k in ['django', 'queryset', 'models.py', 'views.py', 'urls.py', 'orm', 'manage.py', 'dtl'])
        is_python = any(k in q_lower for k in cls.PYTHON_DJANGO_KEYWORDS)

        if is_django:
            return {"is_in_domain": True, "domain": "django", "confidence": 0.95}
        if is_python:
            return {"is_in_domain": True, "domain": "python", "confidence": 0.90}

        # If question contains generic programming terms or concept questions (e.g., "what is a function?", "explain classes", "how does exception handling work?")
        generic_programming_patterns = [
            r'\bfunction\b', r'\bclass\b', r'\bclasses\b', r'\bdecorator\b',
            r'\bexception\b', r'\bloop\b', r'\bif\b', r'\bvariable\b',
            r'\bobject\b', r'\bmethod\b', r'\binheritance\b', r'\bmodule\b',
            r'\bpackage\b', r'\bfile\b', r'\bstring\b', r'\blist\b', r'\bdict\b'
        ]

        for pattern in generic_programming_patterns:
            if re.search(pattern, q_lower):
                return {"is_in_domain": True, "domain": "python", "confidence": 0.80}

        # Default fallback check
        return {"is_in_domain": True, "domain": "python", "confidence": 0.50}
