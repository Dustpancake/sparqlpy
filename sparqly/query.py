import types
import inspect
from collections import defaultdict
import abc

from sparqly.item import Item

def query(*args, **kwargs):
    return Query(*args, **kwargs)


class InvalidQuery(Exception):
    ...
class InvalidQueryItem(Exception):
    ...
class InvalidPredicate(Exception):
    ...
class SelectTypeMistmatch(Exception):
    ...
class SelectWhereMistmatch(Exception):
    ...
class NoSuchPredicate(Exception):
    ...


class Query:

    def __init__(self):
        self._reset()

    def __getattr__(self, name: str):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(f"No attribute named '{name}'.")

    def __str__(self):
        if self._query == "":
            raise InvalidQuery
        else:
            return self._query

    def select(self, *args):
        if len(args) > 0:
            self._reset()
            for i in args:
                if not inspect.isclass(i):
                    raise NotImplementedError
                if not issubclass(i, Item):
                    raise InvalidQueryItem

            self._select(*args)
            return self
        else:
            raise TypeError

    def where(self, *args, **kwargs):
        if len(args) > 0:

            if len(args) != len(self._selections):
                raise SelectWhereMistmatch

            for item, kw in zip(self._selections, args):
                self._where_kwargs(item, **kw)

        elif kwargs and len(self._selections) == 1:

            self._where_kwargs(
                self._selections[0],
                **kwargs
            )

        else:
            raise SelectWhereMistmatch
        return self

    def all(self):
        self._assemble_query()
        return self

    def _where_kwargs(self, item, **kwargs):
        subj = self._tripples[item]
        predicates = item._predicates

        for k, v in kwargs.items():
            if k not in predicates:
                raise InvalidPredicate
            subj[k].append(v)

        self._tripples[item] = subj

    def _select(self, *args):
        for i in args:
            # implement like this for testing; TODO: neaten
            if type(i) is abc.ABCMeta or type(i) is type:
                i = i()
                if not isinstance(i, Item):
                    raise InvalidQueryItem

            self._selections.append(i)

    def _canonicalise_selection(self):
        ...

    def _assemble_query(self):
        variables   = []
        tripples    = []
        for item, doubles in self._tripples.items():
            query_item = "?" + str(item)
            variables.append(query_item)

            doubles = self._fetch_predicate_names(item, doubles)
            tripples.append(
                self._make_tripple(query_item, doubles)
            )

        query = "SELECT " + " ".join(variables)
        query += " WHERE {\n\t" + "\n\t".join(tripples) + "\n}"
        self._query = query

    def _fetch_predicate_names(self, item, doubles):
        res = {}
        for k, v in doubles.items():
            if hasattr(item, k):
                res[item[k]] = v
            else:
                raise NoSuchPredicate(k)
        return res

    def _make_tripple(self, item, tripples):
        trip = ""

        for predicate, object_list in tripples.items():
            if len(object_list) > 1:
                raise NotImplementedError
            double = f"\n\t{predicate} {str(object_list[0])} ;"
            trip += double

        trip = f"{item} " + trip[2:-1] + "."
        return trip

    def _reset(self):
        self._query         = ""
        self._selections    = []
        self._tripples      = defaultdict(
            lambda: defaultdict(list)
        )
