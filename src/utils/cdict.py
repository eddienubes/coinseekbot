"""
    This module contains the implementation of the cdict class.
    cdit stands for chainable dictionary.
    Often used in the context of API responses, where you have to access nested dictionaries.
"""
from typing import Mapping


class CDictNone:
    def __eq__(self, other):
        return other is None

    def __ne__(self, other):
        return other is not None

    def __bool__(self):
        return False

    def __str__(self):
        return 'CDict:None'

    def __repr__(self):
        return 'CDict:None'

    def __getattr__(self, item):
        return self

    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self


cdict_none = CDictNone()


# TODO: Add support for lists
class CDict(dict):
    def __init__(self, map: Mapping):
        self.__map = map

    def __getattr__(self, item):
        return self.__get(item)

    def __getitem__(self, item):
        return self.__get(item)

    def values(self):
        return self.__map.values()

    def keys(self):
        return self.__map.keys()

    def items(self):
        return self.__map.items()

    def __str__(self):
        return str(self.__map)

    def __repr__(self):
        return repr(self.__map)

    def __format__(self, format_spec):
        return format(self.__map, format_spec)

    def __get(self, key):
        item = self.__map.get(key, cdict_none)

        if isinstance(item, Mapping):
            return CDict(item)

        return item
