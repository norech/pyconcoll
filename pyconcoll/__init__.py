"""
pyconcoll.

A basic implementation of Connected Collections in Python.
"""

__version__ = "0.1.0"
__author__ = 'Alexis Cheron'

from collections.abc import Iterable
from typing import get_type_hints
from sortedcollections import OrderedSet

# custom type, it is essentially a wrapper around a set

class CCollection(OrderedSet):
    def __init__(self, iterable):
        super().__init__(iterable)

    def __len__(self):
        return super().__len__()

    def __contains__(self, key):
        return super().__contains__(key)

    def __getitem__(self, item):
        return super().__getitem__(item)
    
    def __iter__(self):
        return super().__iter__()

    def __reversed__(self):
        return super().__reversed__()

    def __setitem__(self, index, item):
        super().__setitem__(index, item)

    def insert(self, index, item):
        super().insert(index, item)

    def append(self, item):
        super().append(item)

    def extend(self, other):
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(other)

    def discard(self, item):
        super().discard(item)

# this is our connected collection logic
#
# all classes using connected collections must have this class as a metaclass
# -> these classes will then be metaconnected, which allow connected collections to work
class MetaConnected(type):
    def __new__(cls, name, bases, dct):
        cls_obj = super().__new__(cls, name, bases, dct)
        cls_attr = cls_obj.__annotations__ if hasattr(cls_obj, '__annotations__') else None
        orig_init = cls_obj.__init__
        orig_getattribute = cls_obj.__getattribute__
        orig_setattr = cls_obj.__setattr__

        ## __init__          => called when a class instance is created
        ## __setattr__       => called when an class attribute is set
        ## __getattribute__  => called when an class attribute is get

        # STEP 1. override __init__ and attach all CCollection[T] attributes before
        #
        # making sure that self.__ccollections__[B] points to a matching CCollection[B]
        #

        def __init__(self, *args, **kwargs):
            if not hasattr(self, '__ccollections__'):
                self.__ccollections__ = dict()  # we first define our attribute
 
            # we can solve some postponed references that way by using get_type_hints instead
            # once we can expect the type annotations to be solved
            nonlocal cls_attr
            try:
                cls_attr = get_type_hints(cls_obj)
            except:
                pass

            # we init the class accordingly
            # this code is ran before so we can populated collections at the end of inheritance contexts
            orig_init(self, *args, **kwargs)

            # and then we populate it accordingly
            if cls_attr != None:
                for attr_name in cls_attr:
                    attr = cls_attr[attr_name]
                    if hasattr(attr, '__origin__') and attr.__origin__ is CCollection:  # if we found an attribute which is a conn collection
                        t = attr.__args__[0]  # we get its generic type argument
                        if type(t) == str:
                            raise AttributeError(f"{cls_obj.__name__} has invalid attribute '{attr_name}': Forward references aren't supported in '{CCollection.__name__}' types. "
                                                f"Consider reorganizing your classes to avoid forward references as generic argument of '{CCollection.__name__}'. "
                                                f"From Python 3.7, you can add 'from __future__ import annotations' to your file to permit circular dependencies in type annotations")
                        if t != object and t.__class__ is not MetaConnected:
                            typename = t.__name__ if hasattr(t, '__name__') else type(t).__name__
                            raise AttributeError(f"{cls_obj.__name__} has invalid attribute '{attr_name}': '{typename}' type does not have the metaclass '{MetaConnected.__name__}'. "
                                                f"It is necessary to use the correct class type in connected collections")
                        # at this point we are sure the class is metaconnected
                        unique = str(t.__module__ + "." + t.__name__)  # we get a unique class identifier (e.g. __main__.Screw)
                        if len(attr.__args__) > 1:
                            unique = unique + ":" + str(attr.__args__[1])

                        if not unique in self.__ccollections__:
                            coll = CCollection([])                # we create our own collection
                            orig_setattr(self, attr_name, coll)   # then we overwrite the attribute with our own collection
                            self.__ccollections__[unique] = orig_getattribute(self, attr_name)
            
        # define function to detach value from any connected collection in metaconnected class
        def detach_from(metacon: MetaConnected, self, attr_name):
            collections = metacon.__ccollections__
            for cl in self.__class__.__mro__:          # lookup class and its inheritance tree
                type_unique = str(cl.__module__ + "." + cl.__name__)  # we get our unique class identifier (e.g. __main__.Screw)
                attr_unique = type_unique + ":" + attr_name
                if attr_unique in collections:              # if this class is listened by any connected collection in the other class
                    collections[attr_unique].discard(self)  # we remove the instance from the old connected collection
                    return                                  # only the first collection type is affected
                if type_unique in collections:              # if this class is listened by any connected collection in the other class
                    collections[type_unique].discard(self)  # we remove the instance from the old connected collection
                    return                                  # only the first collection type is affected

        # define function to attach value to connected collection in metaconnected class
        def attach_to(metacon: MetaConnected, self, attr_name):
            collections = metacon.__ccollections__
            for cl in self.__class__.__mro__:      # lookup class and its inheritance tree
                type_unique = str(cl.__module__ + "." + cl.__name__)  # we get our unique class identifier (e.g. __main__.Screw)
                attr_unique = type_unique + ":" + attr_name
                if attr_unique in collections:          # if this class is listened by any connected collection in the other class
                    collections[attr_unique].add(self)  # we add the instance to the new connected collection
                    return                              # only the first collection type is affected
                if type_unique in collections:          # if this class is listened by any connected collection in the other class
                    collections[type_unique].add(self)  # we add the instance to the new connected collection
                    return                              # only the first collection type is affected

        # STEP 2. override the setters

        def __getattribute__(self, name):
            # we don't really need to override getattribute, kept for a future iteration just in case
            return orig_getattribute(self, name)

        def __setattr__(self, name, value):
            # if is connected collection, we raise an error
            if cls_attr != None and name in cls_attr and hasattr(cls_attr[name], '__origin__') and cls_attr[name].__origin__ is CCollection:
                raise AttributeError(f"{self.__class__.__name__} is doing an invalid operation on '{name}' attribute: A CCollection type is read-only in a meta-connected class as it is automatically populated. "
                                     f"It can't manually be updated.")
            # STEP 3. when setting an element containing a CCollection[Self] (collection of our type)
            # we will attach to the matching connected collection on the passed value
            #
            # however first we need to detach from the previously connected collection (if any)

            # 3.1. try to detach the old value if it already has a connected collection
            try:
                old_value = orig_getattribute(self, name)
                if isinstance(old_value, Iterable):
                    for e in old_value:
                        if hasattr(e, '__ccollections__'):  # check if the old value object supports connected collections
                            detach_from(e, self, name)
                else:
                    if hasattr(old_value, '__ccollections__'):  # check if the old value object supports connected collections
                        detach_from(old_value, self, name)
            except:
                # it might fail
                pass

            # 3.2. we attach ourselves to the collection matching our type in the new value
            if isinstance(value, Iterable):
                for e in value:
                    if hasattr(e, '__ccollections__'):  # check if the new value object supports connected collections
                        attach_to(e, self, name)
            else:
                if hasattr(value, '__ccollections__'):  # check if the new value object supports connected collections
                    attach_to(value, self, name)
            
            # we then assign normally
            orig_setattr(self, name, value)

        cls_obj.__init__ = __init__
        cls_obj.__getattribute__ = __getattribute__
        cls_obj.__setattr__ = __setattr__
        return cls_obj