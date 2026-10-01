<!-- Title: Python Documentation — Inheritance and Polymorphism -->
<!-- Category: python -->
<!-- Section: Classes & Object Oriented Programming -->
<!-- SourceURL: https://docs.python.org/3/tutorial/classes.html#inheritance -->

# Inheritance in Python

Inheritance allows a class (child/derived class) to inherit attributes and methods from another class (parent/base class).

## Basic Single Inheritance
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Generic animal sound"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

cat = Cat("Whiskers")
print(cat.speak()) # Output: Whiskers says Meow!
```

## Using `super()`
The `super()` function allows access to parent class methods, especially constructor initializations.

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

class Developer(Employee):
    def __init__(self, name, salary, programming_language):
        super().__init__(name, salary)
        self.programming_language = programming_language
```

## Multiple Inheritance & Method Resolution Order (MRO)
Python supports multiple inheritance, where a child class inherits from multiple base classes. Method lookup order follows C3 Linearization (Method Resolution Order - MRO), which can be checked via `ClassName.__mro__`.

```python
class A:
    def process(self):
        print("A process")

class B(A):
    def process(self):
        print("B process")

class C(A):
    def process(self):
        print("C process")

class D(B, C):
    pass

d = D()
d.process() # Calls B process based on MRO (D -> B -> C -> A)
```
