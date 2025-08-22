def func():
    pass

@property
def prop(self):
    pass

# func is a non-data descriptor
hasattr(func, '__get__')
hasattr(func, '__set__')

# prop is a data descriptor
hasattr(prop, '__get__')
hasattr(prop, '__set__')
