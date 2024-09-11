# pyconcoll


Connected Collections' implementation in Python.

> https://github.com/norech/pyconcoll


## How to install

```bash
git clone https://github.com/norech/pyconcoll
cd pyconcoll
pip install .

```

## How to use

Import the following:

```py
from __future__ import annotations  # optional: to support circular type hints
from pyconcoll import MetaConnected, CCollection
```

All classes interacting with connected collections should be meta-connected classes.
It can be done by using `MetaConnected` as metaclass, such as:

```py
class A(metaclass=MetaConnected):
    pass
    
class B(metaclass=MetaConnected):
    pass
```

### One-to-Many: Object Reference and Collected Collection

You can declare your fields, for example `b` and `ca`:

```py
class A(metaclass=MetaConnected):
    b: B = None
    
class B(metaclass=MetaConnected):
    ca: CCollection[A]
```

> Please note that **manually updating values in connected collections is unsupported** and will break now or in a future release!

You can then use your newly defined classes the following way:

```py
b = B()
a = A()

a.b = b

print(b.ca)
# [a]

a.b = None

print(b.ca)
# []

```

Once `a.b` is set to `b`, you can see `b.ca` automatically containing the `a` object.

This can be done with as many classes as you wish. You can find below a more complex example:

```py
b0 = B()
b1 = B()
a0 = A()
a1 = A()

a0.b = b0
a1.b = b0

print(b0.ca)
# [a0, a1]
print(b1.ca)
# []

a0.b = b1

print(b0.ca)
# [a1]
print(b1.ca)
# [a0]
```

### Many-to-Many: Lists of References and Connected Collections

You can declare your fields, for example `lb` and `ca`:

```py
class A(metaclass=MetaConnected):
    lb: list[B] = []
    
class B(metaclass=MetaConnected):
    ca: CCollection[A]
```

> Please note that **manually updating values in connected collections is unsupported** and will break now or in a future release!

You can then use your newly defined classes the following way:

```py
b = B()
a = A()

a.lb = [b0]

print(b.ca)
# [a]

a.lb = []

print(b.ca)
# []

```

Once `a.b` is set to `b`, you can see `b.ca` automatically containing the `a` object.

This can be done with as many classes as you wish. You can find below a more complex example:

```py
b0 = B()
b1 = B()
b2 = B()
a0 = A()
a1 = A()

a0.lb = [b0, b1]
a1.lb = [b0, b1]

print(b0.ca)
# [a0, a1]
print(b1.ca)
# [a0, a1]

a0.lb = [b1, b2]

print(b0.ca)
# [a1]
print(b1.ca)
# [a0, a1]
print(b2.ca)
# [a0]
```
