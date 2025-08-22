def filt(d):
    "Filter __dunder__ keys from the given dict"
    return {k: v for (k, v) in d.items() if not k.startswith('__')}

class C3:
    attr = 1
    @property
    def prop(self):
        return 2
    def meth(self):
        pass

obj = C3()

obj.attr    # case  7: found in C3.__dict__ (same as case 2)
obj.prop    # case  8: property is executed
obj.meth    # case  9: bound method is returned

C3.attr     # case 10: found in C3.__dict__ (same as case 4)
C3.prop     # case 11: return property object
C3.meth     # case 12: return function object


C3.prop.__get__(obj, C3)
C3.meth.__get__(obj, C3)

obj.meth = 'hello'
obj.meth
filt(obj.__dict__)

obj.prop = 'hello'

obj.__dict__['prop'] = 'hello'
filt(obj.__dict__)
obj.prop
