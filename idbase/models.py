from __future__ import unicode_literals
import inspect
from idbase.util import get_class


class BaseModel(object):
    """
    A base class which, when inherited, can serialize to and deserialize
    from a dictionary. The _specials dictionary is a mapping of attribute
    name to another BaseModel for embedding other objects.
    """
    _specials = {}

    def __init__(self, **kwargs):
        """
        Initialize instance attributes to those of the class attributes
        unless overridden in kwargs. _specials is a dictionary of
        attribute name to BaseModel class.
        """
        bad_keys = (set(kwargs.keys()) - set(self.get_class_attributes()) or
                    [x for x in kwargs.keys() if x.startswith('_')])
        if bad_keys:
            raise ValueError('Bad value in dictionary: {}'.format(bad_keys))
        for key in self.get_class_attributes():
            if key in self._specials and key in kwargs:
                subobj = get_class(self._specials[key])(**kwargs[key])
                setattr(self, key, subobj)
            elif key in kwargs:
                setattr(self, key, kwargs[key])

    def to_dict(self):
        """Return a dictionary representation of a model object."""
        ret = {}
        for att in self.get_class_attributes():
            specials = self.__class__._specials
            if att in specials and getattr(self, att):
                ret[att] = getattr(self, att).to_dict()
            else:
                ret[att] = getattr(self, att)
        return ret

    @classmethod
    def get_class_attributes(cls):
        keys = (x for x in vars(cls).keys() if not x.startswith('_'))
        return [x for x in keys
                if not inspect.isfunction(getattr(cls, x)) and
                not inspect.ismethod(getattr(cls, x))]
