def filt(d):
    "Filter __dunder__ keys from the given dict"
    return {k: v for (k, v) in d.items() if not k.startswith('__')}

class C1:
    x = 1
    y = 2

class C2(C1):
    y = 3
    z = 4

obj = C2()
obj.z = 5

# let's examine the dicts
filt(obj.__dict__)
filt(C2.__dict__)
filt(C1.__dict__)

# getattr on the INSTANCE
obj.z   # case 1: found in obj.__dict__ (shadows C2.z)
obj.y   # case 2: found in C2.__dict__  (shadows C1.y)
obj.x   # case 3: found in C1.__dict__

# getattr on the TYPE
C2.z    # case 4: found in C2.__dict__
C2.y    # case 5: found in C2.__dict__ (shadows C1.y)
C2.x    # case 6: found in C1.__dict__
