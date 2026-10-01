<!-- Title: Python Documentation — Classes and Object-Oriented Programming -->
<!-- Category: python -->
<!-- Section: Classes -->
<!-- SourceURL: https://docs.python.org/3/tutorial/classes.html -->

# Classes and Object-Oriented Programming in Python

Classes provide a means of bundling data and functionality together. Creating a new class creates a new type of object, allowing new instances of that type to be made.

## Class Definition Syntax
Classes are defined using the `class` keyword.

```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis lupus familiaris"

    def __init__(self, name, age):
        # Instance attributes (unique to each instance)
        self.name = name
        self.age = age

    def bark(self):
        """Method representing dog barking action."""
        return f"{self.name} says Woof!"
```

## The `__init__` Method
The `__init__` method is the constructor method in Python. It is automatically called when a new instance of a class is instantiated. The first parameter of instance methods is always `self`, which refers to the specific instance being operated on.

## Encapsulation & Attribute Access
Attributes in Python classes are public by default. Private attributes are conventionally prefixed with an underscore `_` (non-public) or double underscore `__` (triggers name mangling).

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance # Protected attribute

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    def get_balance(self):
        return self._balance
```

## Class Methods and Static Methods
- `@classmethod`: Receives the class (`cls`) as the first argument instead of `self`. Useful for alternative constructors.
- `@staticmethod`: Does not receive `self` or `cls`. Behaves like a plain function bound to a class namespace.
