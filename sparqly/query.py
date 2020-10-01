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
                    if type(i) is not str:
                        raise NotImplementedError
                    else:
                        continue
                if not issubclass(i, Item):
                    raise InvalidQueryItem

            self._select(*args)
            return self
        else:
            raise TypeError

    def where(self, *args, **kwargs):
        subjects = len(self._selections["subject"])
        objects = len(self._selections["object"])

        if subjects and objects:
            raise NotImplementedError

        elif subjects:
            self._where_handler(
                self._selections["subject"],
                *args,
                **kwargs
            )

        elif objects:
            self._where_handler(
                self._selections["object"],
                *args,
                **kwargs
            )

        else:
            raise SelectWhereMistmatch

        return self

    def all(self):
        self._assemble_query()
        return self

    def _where_handler(self, selections, *args, **kwargs):
        if len(args) > 0:

            if not all(type(i) == dict for i in args):
                raise TypeError

            for item, kw in zip(selections, args):
                self._where_kwargs(item, **kw)

        elif kwargs and len(selections) == 1:

            self._where_kwargs(
                selections[0],
                **kwargs
            )

        else:
            raise SelectWhereMistmatch

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
            type_of_arg = type(i)
            if type_of_arg is abc.ABCMeta or type_of_arg is type:
                i = i()
            if isinstance(i, Item):
                self._selections["subject"].append(i)
            else:
                self._selections["object"].append(i)

    def _validate_arguments(self):
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
        self._selections    = {
            "subject": [],
            "object": []
        }
        self._tripples      = defaultdict(
            lambda: defaultdict(list)
        )
