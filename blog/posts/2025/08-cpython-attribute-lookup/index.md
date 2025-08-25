---
draft: false
date: 2025-08-25
title: "Inside CPython's attribute lookup"
categories:
  - Post
tags:
  - cpython

---

# Inside CPython's attribute lookup

Python's attribute lookup logic seems pretty simple at a first glance: "first
look in the instance `__dict__`, then look in its type".

However, the actual logic is much more complex because it needs to take into
account the descriptor protocol, the difference between lookups on instances
vs types, and what happens in presence of metaclasses.

Recently I implemented preliminary support for the descriptor protocol in SPy,
which led me to investigate the CPython source code to get a
better grasp on the details. This is a write up on what I found, with links to
the actual C source code, to serve as a future reference.

Thanks to Hood Chatham, Siu Kwan Lam and Justin Wood for the feedback on drafts.

<!-- more -->

# A quick recap on `getattr()` logic

Consider the following example:

```python
>>> def filt(d):
...     "Filter __dunder__ keys from the given dict"
...     return {k: v for (k, v) in d.items() if not k.startswith('__')}
...
>>> class C1:
...     x = 1
...     y = 2
...
>>> class C2(C1):
...     y = 3
...     z = 4
...
>>> obj = C2()
>>> obj.z = 5
```

Each instance and class has a `__dict__` where it stores its attributes:

```python
>>> filt(obj.__dict__)
{'z': 5}

>>> filt(C2.__dict__)
{'y': 3, 'z': 4}

>>> filt(C1.__dict__)
{'x': 1, 'y': 2}
```

!!!note
    This is an oversimplification. There are cases in which objects **do not**
    have an associated `__dict__`. For the sake of simplicity, in this post we
    assume that `__dict__` is always present.

First, let's see what happens when we get attributes **on the instance**:

```python
>>> obj.z   # case 1: found in obj.__dict__ (shadows C2.z)
5

>>> obj.y   # case 2: found in C2.__dict__  (shadows C1.y)
3

>>> obj.x   # case 3: found in C1.__dict__
1
```

Then, let's look at getattr **on the type**:

```python
>>> C2.z    # case 4: found in C2.__dict__
4

>>> C2.y    # case 5: found in C2.__dict__ (shadows C1.y)
3

>>> C2.x    # case 6: found in C1.__dict__
1
```

This confirms our intuitive understanding: attributes are searched first in
the instance, then in the class, then in the superclasses.

## Descriptors

Let's see what happens in presence of methods and properties:

```python
>>> class C3:
...     attr = 1
...     @property
...     def prop(self):
...         return 2
...     def meth(self):
...         pass
...
>>> obj = C3()
```

First, let's try to lookup `attr`, `prop` and `meth` on the instance:

```python
>>> obj.attr    # case  7: found in C3.__dict__ (same as case 2)
1

>>> obj.prop    # case  8: property is executed
2

>>> obj.meth    # case  9: bound method is returned
<bound method C3.meth of <__main__.C3 object at 0x779b0fcca0f0>>
```

Then, let's do the same on the class:

```python
>>> C3.attr     # case 10: found in C3.__dict__ (same as case 4)
1

>>> C3.prop     # case 11: return property object
<property object at 0x779b0fb56390>

>>> C3.meth     # case 12: return function object
<function C3.meth at 0x779b0fb74680>
```

Things to note:

  - `obj.attr` and `C3.attr` return the very same object

  - `C3.prop` and `C3.meth` return the unmodified "property object" and
    "function object"

  - `obj.prop` and `obj.meth` return _something different_: Python "knows"
    that to get `obj.prop` it needs to call the property getter function,
    while to get `obj.meth` it needs to create a bound method (which we can
    call later if we want, but that's not the point here).

How does Python "know"? The answer is the **descriptor protocol**: if we
find an attribute on the type (`C3`) and this attribute has a `__get__`
method, we call the `__get__` to compute the actual result. In other
words, `obj.prop` is equivalent to `C3.prop.__get__(obj, C3)`:

```python
>>> C3.prop.__get__(obj, C3)
2

>>> C3.meth.__get__(obj, C3)
<bound method C3.meth of <__main__.C3 object at 0x779b0fcca0f0>>
```


Things become interesting if we try to set those attributes on `obj`. We
already saw in "case 3" that `obj.z = 5` puts `z` inside `obj.__dict__` and
thus shadows `C2.z`. The same happens for `obj.meth`:

```python
>>> obj.meth = 'hello'
>>> obj.meth
'hello'

>>> filt(obj.__dict__)
{'meth': 'hello'}
```

What happens if we set `obj.prop` though?

```python
>>> obj.prop = 'hello'
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: property 'prop' of 'C3' object has no setter
```

This is kind of expected, because we didn't define `@prop.setter`. But how does
Python "know" that it needs to treat `prop` differently than `meth`?

Moreover, let's try to force `prop` inside `obj.__dict__`:

```python
>>> obj.__dict__['prop'] = 'hello'
>>> filt(obj.__dict__)
{'meth': 'hello', 'prop': 'hello'}
>>> obj.prop
2
```

Note that in this case, the `prop` inside `obj.__dict__` **does not shadow** the
`prop` inside `C3.__dict__` 😱. Again, this is very different than `meth`,
which can be happily shadowed by the instance dict.


## Data vs non-data descriptors

The answer is that Python has the concept of "data descriptors" and "non data
descriptors". In short:

  - non-data descriptors are objects whose type define only `__get__`

  - data descriptors are objects whose type define also `__set__` and/or
    `__delete__`.

The nuance is in the lookup order:

  - data descriptors have always the precedence over `obj.__dict__`.

  - for non-data descriptors (e.g. functions/methods), the instance `__dict__`
    has the precedence

The other nuance is that `property` objects are always data descriptors even
if we don't attach the `setter`: in that case, their `__set__` method is
called anyway, it notices that we don't have any `setter`, and it raises
`AttributeError`.

Let's double check:
```python
>>> def func():
...     pass
...
>>> @property
... def prop(self):
...     pass
...

>>> # func is a non-data descriptor
>>> hasattr(func, '__get__')
True
>>> hasattr(func, '__set__')
False

>>> # prop is a data descriptor
>>> hasattr(prop, '__get__')
True
>>> hasattr(prop, '__set__')
True
```

# Dive into CPython internals

Time to look at some actual C code to see where all this complex logic comes
from.

!!!note
    For those who are not proficient with C, I also rewrote the main bits of the
    logic in [Python pseudocode](#bonus-python-pseudocode), shown at the end of
    this post.

I am going to show the source code of **CPython 3.12.11**, even if it's a bit
old. This is because 3.13 introduced many optimizations which makes it much
harder to follow the logic, whereas 3.12 is simpler to read and understand.

Ultimately, the expression `obj.x` invokes `type(obj).__getattribute__(obj,
"x")`. Let's see how.

`obj.x` is compiled into a `LOAD_ATTR` opcode:
```python
>>> import dis
>>> def foo():
...     obj.x
...
>>> dis.dis(foo)
  1           0 RESUME                   0

  2           2 LOAD_GLOBAL              0 (obj)
             12 LOAD_ATTR                2 (x)
             32 POP_TOP
             34 RETURN_CONST             0 (None)
```

In modern CPython, individual opcodes are described by a DSL (similar to
C) in `Python/bytecodes.c`, and the main loop of the interpreter is
automatically generated from that description. Here is the full implementation
of
[LOAD_ATTR](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Python/bytecodes.c#L1760-L1806). It
contains a lot of special cases for performance, but the fallback logic is
here:

```c
    /* Classic, pushes one value. */
    res = PyObject_GetAttr(owner, name);
    DECREF_INPUTS();
    ERROR_IF(res == NULL, error);
```

So, `LOAD_ATTR` directly calls
[PyObject_GetAttr](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/object.c#L1047-L1079). Apart from
error checking and legacy code to support the old and deprecated `tp_getattr`
slot, the bulk of the logic is here:

```c
    PyTypeObject *tp = Py_TYPE(v);
    /* ... */
    PyObject* result = NULL;
    if (tp->tp_getattro != NULL) {
        result = (*tp->tp_getattro)(v, name);
    }
```

[tp_getattro](https://docs.python.org/3.12/c-api/typeobj.html#c.PyTypeObject.tp_getattro)
is a slot on the C struct `PyTypeObject`, which corresponds to
`__getattribute__`: each type can implement its own attribute lookup logic,
but most of them, including the type `object`, just set the slot to
[PyObject_GenericGetAttr](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/object.c#L1535-L1539),
which according to the docs "implements the normal way of looking for object
attributes".  This is the logic that you get when you define a new Python
`class`, unless you explicitly override `__getattribute__`.

## Attribute lookup on instances

`PyObject_GenericGetAttr` immediately delegates to
[_PyObject_GenericGetAttrWithDict](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/object.c#L1412-L1533),
which is quite complex and contains a lot of error checking code.

Let's walk over its basic logic, step by step:

`1.` Look for a data descriptor:

```c
    PyTypeObject *tp = Py_TYPE(obj);
    PyObject *descr = NULL;
    PyObject *res = NULL;
    descrgetfunc f;

    descr = _PyType_Lookup(tp, name);

    f = NULL;
    if (descr != NULL) {
        Py_INCREF(descr);
        f = Py_TYPE(descr)->tp_descr_get;
        if (f != NULL && PyDescr_IsData(descr)) {
            res = f(descr, obj, (PyObject *)Py_TYPE(obj));
            if (res == NULL && suppress &&
                    PyErr_ExceptionMatches(PyExc_AttributeError)) {
                PyErr_Clear();
            }
            goto done;
        }
    }
```

The first thing we do is to lookup `name` **on the type** of `obj`. I'm not
going to show the code for
[_PyType_Lookup](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/typeobject.c#L4722-L4775),
but what it does is to look up the given name _following the MRO_ of the type:
this is how we find attributes on base classes.

If we find something **and** it's a data descriptor, we immediately call its
`tp_get` slot (which corresponds to `__get__`). This is what happens e.g. when
we looked up `obj.prop` in "case 8" above.

It's worth noting what the values of `descr` and `f` are if we **did not** find a
data descriptor:

  - if `f != NULL` it means that we found something on the type and that **it's
    a non-data descriptor**; `f` contains its `tp_get`.

  - if `f == NULL && descr != NULL` it means that we found something on the
    type and **it's not a descriptor**; `descr` contains that object (even
    though we know by now it's not a descriptor... naming is hard 🤷‍♂️).

`2.` Look in `obj.__dict__`: if we find something, return it. This is what
happens for e.g. `obj.z` in "case 1".

```c
    if (dict == NULL) {
        /* complex logic to find the dict of the instance */
        /* ... "*/
    }
    if (dict != NULL) {
        Py_INCREF(dict);
        res = PyDict_GetItemWithError(dict, name);
        if (res != NULL) {
            Py_INCREF(res);
            Py_DECREF(dict);
            goto done;
        }
    /* ... */
    }
```

`3.` If at point (1) we found a non-data descriptor, it's now time to call its
`__get__`. This is what happens for `obj.meth` in "case 9":

```c
    if (f != NULL) {
        res = f(descr, obj, (PyObject *)Py_TYPE(obj));
        if (res == NULL && suppress &&
                PyErr_ExceptionMatches(PyExc_AttributeError)) {
            PyErr_Clear();
        }
        goto done;
    }
```

`4.` If at point (1) we found something which is not a descriptor, just return
   it. This is what happens for `obj.attr` in "case 7":

```c
    if (descr != NULL) {
        res = descr;
        descr = NULL;
        goto done;
    }
```

`5.` No attribute found, time to raise `AttributeError`:

```c
    if (!suppress) {
        PyErr_Format(PyExc_AttributeError,
                     "'%.100s' object has no attribute '%U'",
                     tp->tp_name, name);

        set_attribute_error_context(obj, name);
    }
```

## Attribute lookup on types

Look again at cases 3 and 6 (`obj.x` and `C2.x`).

There, `obj.x` and `C2.x` follow slightly different rules: in the first case we
do the recursive lookup **on the type of the obj**. In the second case we do the
recursive lookup **on the object itself** `(C2)`.

The lookup logic for `C2.x` depends on the type of C2, which is `type` itself,
and in particular on its `tp_getattro` slot. The C definition of `type` is [PyType_Type](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/typeobject.c#L5322-L5367). Here is an excerpt of it:

```c
PyTypeObject PyType_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "type",                                     /* tp_name */
    sizeof(PyHeapTypeObject),                   /* tp_basicsize */
    sizeof(PyMemberDef),                        /* tp_itemsize */
    [...]
    (getattrofunc)_Py_type_getattro,            /* tp_getattro */
    (setattrofunc)type_setattro,                /* tp_setattro */
    [...]
};
```

So, `PyType_Type.tp_getattro` is [_Py_type_getattro](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/typeobject.c#L4891-L4897). The accompanying comment is particularly interesting:

```c
/* This is similar to PyObject_GenericGetAttr(),
   but uses _PyType_Lookup() instead of just looking in type->tp_dict. */
PyObject *
_Py_type_getattro(PyTypeObject *type, PyObject *name)
{
    return _Py_type_getattro_impl(type, name, NULL);
}
```

It confirms that for types, we don't just look into the `__dict__`, but we do
a full `_PyType_Lookup` along the whole MRO.

Let's look at the interesting parts of [_Py_type_getattro_impl](https://github.com/python/cpython/blob/55fee9cf216abe4ec0d1139f94b1930fbd0c7644/Objects/typeobject.c#L4787-L4889) step by step:

`1.` Before we are allowed to look into the `__dict__`, we need to take into
   consideration the **metatype** (i.e., the type of our type). This is needed
   because if the metatype defines a data descriptor, it must take the
   precedence over our `__dict__`. This is basically the same logic as for
   normal objects, but we need to replicate it here:

```c
    PyTypeObject *metatype = Py_TYPE(type);
    PyObject *meta_attribute, *attribute;
    descrgetfunc meta_get;
    PyObject* res;

    /* No readable descriptor found yet */
    meta_get = NULL;

    /* Look for the attribute in the metatype */
    meta_attribute = _PyType_Lookup(metatype, name);

    if (meta_attribute != NULL) {
        Py_INCREF(meta_attribute);
        meta_get = Py_TYPE(meta_attribute)->tp_descr_get;

        if (meta_get != NULL && PyDescr_IsData(meta_attribute)) {
            /* Data descriptors implement tp_descr_set to intercept
             * writes. Assume the attribute is not overridden in
             * type's tp_dict (and bases): call the descriptor now.
             */
            res = meta_get(meta_attribute, (PyObject *)type,
                           (PyObject *)metatype);
            Py_DECREF(meta_attribute);
            return res;
        }
    }
```

`2.` If we didn't find a data descriptor on the metatype, we can look at the
   dict. This is where the logic differs the most from
   `PyObject_GenericGetAttr`, because we don't look only in our immediate
   `__dict__`, but also in all the `__dict__`s of our superclasses, thanks to
   `_PyType_Lookup`. Note the comment which underlines `and its bases`. Then,
   depending on whether we found a descriptor, we either call the `__get__`
   (cases 11 and 12) or return the attribute directly (cases 4, 5, 6 and 10).

```c
    /* No data descriptor found on metatype. Look in tp_dict of this
     * type and its bases */
    attribute = _PyType_Lookup(type, name);
    if (attribute != NULL) {
        /* Implement descriptor functionality, if any */
        Py_INCREF(attribute);
        descrgetfunc local_get = Py_TYPE(attribute)->tp_descr_get;

        Py_XDECREF(meta_attribute);

        if (local_get != NULL) {
            /* NULL 2nd argument indicates the descriptor was
             * found on the target object itself (or a base)  */
            res = local_get(attribute, (PyObject *)NULL,
                            (PyObject *)type);
            Py_DECREF(attribute);
            return res;
        }

        return attribute;
    }
```

`3.` We couldn't find anything in the `__dict__`. If the metaclass has a
   non-data descriptor, this is the time to call its `__get__`:

```c
    /* No attribute found in local __dict__ (or bases): use the
     * descriptor from the metatype, if any */
    if (meta_get != NULL) {
        PyObject *res;
        res = meta_get(meta_attribute, (PyObject *)type,
                       (PyObject *)metatype);
        Py_DECREF(meta_attribute);
        return res;
    }
```

`4.` If we found a non-descriptor attribute on the metatype, return it as is:

```c
    /* If an ordinary attribute was found on the metatype, return it now */
    if (meta_attribute != NULL) {
        return meta_attribute;
    }
```

`5.` We couldn't find anything, time to raise `AttributeError`:

```c
    /* Give up */
    if (suppress_missing_attribute == NULL) {
        PyErr_Format(PyExc_AttributeError,
                        "type object '%.100s' has no attribute '%U'",
                        type->tp_name, name);
    } else {
        // signal the caller we have not set an PyExc_AttributeError and gave up
        *suppress_missing_attribute = 1;
    }
    return NULL;
}
```

# Bonus: Python pseudocode

Not everyone is proficient in C, and the code is full of many details which
draw attention away from the main logic.

The following is an attempt to write the bulk of the logic in a more readable
way. The code is not meant to be run and it's not tested at all, so it's
totally possible it's broken :).

```python
NULL = object() # sentinel to indicate "not found"

def _PyType_Lookup(tp: type, name: str) -> object:
    "Lookup `name` along tp.__mro__"
    for tp2 in tp.__mro__:
        if name in tp2.__dict__:
            return tp2.__dict__[name]
    return NULL

def PyObject_GenericGetAttr(obj: object, name: str) -> object:
    "This is object.__getattribute__"
    tp = type(obj)
    descr = _PyType_Lookup(tp, name)
    f = NULL

    # 1. if we find a data descriptor on the type, call it
    if descr is not NULL:
        f = _PyType_Lookup(type(descr), "__get__")
        if f is not None and PyDescr_IsData(descr):
            return f(descr, obj, type(obj))

    # 2. if we have a dict, look inside
    mydict = obj.__dict__
    if mydict is not NULL:
        if attr in mydict:
            return mydict[attr]

    # 3. if we found a non-data descriptor on the type, call it now
    if f is not NULL:
        # call the __get__ now
        return f(descr, obj, type(obj))

    # 4. if we found a normal attribute on the type, return it
    if descr is not NULL:
        return descr

    raise AttributeError

def _Py_type_getattro(T: type, name: str) -> object:
    "This is type.__getattribute__"
    meta_T = type(T)

    # no readable descriptor found yet
    meta_get = NULL

    # look for the attribute in the metatype
    meta_attribute = _PyType_Lookup(meta_T, name)

    # if we find a data descriptor on the meta type, call it
    if meta_attribute is not NULL:
        meta_get = _PyType_Lookup(type(meta_attribute), "__get__")
        if meta_get is not NULL and PyDescr_IsData(meta_attribute):
            return meta_get(meta_attribute, T, meta_T)

    # no data descriptor found on metatype. Look in tp_dict of this type and
    # its bases
    attribute = _PyType_Lookup(T, name)
    if attribute is not NULL:
        # implement descriptor functionality, if any
        local_get = _PyType_Lookup(type(attribute), "__get__")
        if local_get:
            # NULL 2nd argument indicates the descriptor was found on the
            # target object itself (or a base)
            return local_get(attribute, None, T)

        return attribute

    # no attribute found in tp_dict: use the descriptor from the metatype, if
    # any
    if meta_get is not NULL:
        return meta_get(meta_attribute, T, meta_T)

    # if an ordinary attribute was found on the metatype, return it now
    if meta_attribute is not NULL:
        return meta_attribute

    raise AttributeError
```
