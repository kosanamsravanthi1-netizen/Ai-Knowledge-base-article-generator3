<!-- Title: Python Documentation — Modules and Packages -->
<!-- Category: python -->
<!-- Section: Modules -->
<!-- SourceURL: https://docs.python.org/3/tutorial/modules.html -->

# Python Modules and Packages

A module is a file containing Python definitions and statements. The file name is the module name with the suffix `.py` appended.

## Importing Modules
Python supports several import styles:

```python
import math
print(math.sqrt(16)) # 4.0

from math import pi, sin
print(sin(pi / 2)) # 1.0

import numpy as np
```

## Packages
Packages are a way of structuring Python's module namespace by using "dotted module names". For example, `A.B` designates a submodule named `B` in a package named `A`.

A folder is recognized as a Python package if it contains an `__init__.py` file (though namespace packages in Python 3.3+ allow optional `__init__.py`).

```
mypackage/
│── __init__.py
│── utils.py
└── models/
    │── __init__.py
    └── user.py
```

## The `if __name__ == '__main__':` Pattern
When a Python script is run directly, `__name__` is set to `'__main__'`. When imported as a module, `__name__` is set to the filename.

```python
def main():
    print("Executing main routine")

if __name__ == "__main__":
    main()
```
