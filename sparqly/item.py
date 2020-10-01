import abc

class Item(abc.ABC):

    def __init__(self):
        pass

    @property
    def _predicates(self):
        """ returns the defined features in the subclass instance
        """
        items = set(dir(self)) - set(dir(Item))
        return list(filter(lambda i: "__" != i[0:2], items))

    @_predicates.setter
    def _predicates(self, *args):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, name):
        return self.__getattribute__(name)

    @staticmethod
    def _inheritors():
        return Item.__subclasses__
