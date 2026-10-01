<!-- Title: Python Documentation — List Comprehensions -->
<!-- Category: python -->
<!-- Section: Data Structures -->
<!-- SourceURL: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions -->

# List Comprehensions in Python

List comprehensions provide a concise way to create lists. Common applications are to make new lists where each element is the result of operations applied to each member of another sequence, or to create a subsequence of elements that satisfy a given condition.

## Basic Syntax
`[expression for item in iterable if condition]`

## Examples

### 1. Basic Transformation
```python
# Traditional loop
squares = []
for x in range(10):
    squares.append(x**2)

# List comprehension equivalent
squares = [x**2 for x in range(10)]
```

### 2. Filtering with Condition
```python
# Extract even numbers
evens = [x for x in range(20) if x % 2 == 0]
```

### 3. Nested Comprehensions
```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [val for row in matrix for val in row]
# Result: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

## Dictionary and Set Comprehensions
Similar syntax can be used to generate dictionaries and sets:

```python
# Dict comprehension
square_map = {x: x**2 for x in range(5)} # {0:0, 1:1, 2:4, 3:9, 4:16}

# Set comprehension (removes duplicates)
unique_lengths = {len(word) for word in ["apple", "banana", "apple", "cherry"]}
```
