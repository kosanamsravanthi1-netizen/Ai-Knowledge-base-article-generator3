<!-- Title: Python Documentation — Decorators -->
<!-- Category: python -->
<!-- Section: Advanced Functions & Metaprogramming -->
<!-- SourceURL: https://docs.python.org/3/glossary.html#term-decorator -->

# Python Decorators

A decorator is a function that takes another function as an argument, extends or alters its behavior without modifying the original function code, and returns a new wrapper function.

## Basic Decorator Syntax
Decorators are applied using the `@decorator_name` syntax above a function definition.

```python
import functools
import time

def my_timer_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds.")
        return result
    return wrapper

@my_timer_decorator
def compute_sum(n):
    return sum(range(n))

# Usage
compute_sum(1000000)
```

## How Decorators Work Under the Hood
The `@` syntax is syntactic sugar. Writing `@my_decorator` above `def my_func(): ...` is identical to:
`my_func = my_decorator(my_func)`

## Decorators with Arguments
To pass arguments to a decorator itself, you must write a decorator factory (a function that returns a decorator).

```python
def repeat(num_times):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                value = func(*args, **kwargs)
            return value
        return wrapper
    return decorator_repeat

@repeat(num_times=3)
def greet(name):
    print(f"Hello {name}")
```

## Using `functools.wraps`
Always use `@functools.wraps(func)` on the inner wrapper function. This preserves the original function's metadata, such as `__name__` and `__doc__`.
