<!-- Title: Python Documentation — Defining Functions -->
<!-- Category: python -->
<!-- Section: Control Flow Tools -->
<!-- SourceURL: https://docs.python.org/3/tutorial/controlflow.html#defining-functions -->

# Defining Functions in Python

A function in Python is a reusable block of code that performs a specific task. Functions allow developers to write modular, readable, and DRY (Don't Repeat Yourself) code.

## Defining a Function
In Python, functions are defined using the `def` keyword followed by the function name, parentheses `()`, and a colon `:`. The code block within every function is indented.

```python
def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"
```

## Function Arguments and Parameters
Python functions support positional arguments, keyword arguments, default parameter values, and arbitrary argument lists.

- **Positional Arguments**: Passed to function parameters in order.
- **Keyword Arguments**: Passed using `kwarg=value` format.
- **Default Arguments**: Parameter default values assigned in the definition.
- **Arbitrary Arguments (`*args`)**: Accepts a tuple of positional arguments.
- **Arbitrary Keyword Arguments (`**kwargs`)**: Accepts a dictionary of keyword arguments.

```python
def calculate_total(price, tax_rate=0.05, *discounts, **extra_fees):
    subtotal = price * (1 + tax_rate)
    for d in discounts:
        subtotal -= d
    for fee_name, fee_val in extra_fees.items():
        subtotal += fee_val
    return subtotal
```

## Lambda Functions (Anonymous Functions)
Small anonymous functions can be created with the `lambda` keyword. Lambda functions can take any number of arguments, but can only have a single expression.

```python
double = lambda x: x * 2
print(double(5)) # Outputs: 10
```

## Docstrings and Return Values
Functions return `None` by default unless an explicit `return` statement is executed. Docstrings `"""Docstring text"""` provide immediate documentation accessible via `help(func)` or `func.__doc__`.
