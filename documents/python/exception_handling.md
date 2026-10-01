<!-- Title: Python Documentation — Exception Handling -->
<!-- Category: python -->
<!-- Section: Errors and Exceptions -->
<!-- SourceURL: https://docs.python.org/3/tutorial/errors.html -->

# Exception Handling in Python

Exceptions are errors detected during execution. Python provides structured exception handling using `try`, `except`, `else`, and `finally` blocks.

## Basic Try-Except Block
```python
try:
    number = int(input("Enter a number: "))
    result = 100 / number
except ValueError:
    print("Invalid input! Please enter an integer.")
except ZeroDivisionError:
    print("Error: Cannot divide by zero!")
```

## The Complete Try Statement Structure
- `try`: Contains code that might raise an exception.
- `except`: Catches and handles specific exception types.
- `else`: Executes if NO exceptions were raised in the try block.
- `finally`: ALWAYS executes regardless of whether an exception occurred. Ideal for cleanup tasks like closing files or database connections.

```python
file = None
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File was not found.")
else:
    print(f"File successfully read: {len(content)} bytes.")
finally:
    if file:
        file.close()
        print("File closed.")
```

## Raising Exceptions
Use the `raise` keyword to trigger custom exceptions.

```python
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative.")
    return age
```

## Custom Exception Classes
Custom exceptions inherit from Python's built-in `Exception` class.

```python
class InsufficientFundsError(Exception):
    """Raised when an account balance is lower than withdrawal amount."""
    def __init__(self, balance, amount):
        super().__init__(f"Attempted to withdraw ${amount} with balance ${balance}.")
        self.balance = balance
        self.amount = amount
```
