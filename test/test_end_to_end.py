import pytest

from unittest.mock import call as MockCall
from unittest.mock import MagicMock

from sparqly import query, Item
from sparqly.query import (
    InvalidQueryItem,
    InvalidQuery,
    SelectTypeMistmatch
)

class Example(Item):
    ex_predicate = "predicate"
    something_else = "PS:213989"
    other = "QMP:313"

def test_select_item():
    q = query()

    q.select(Example)
    assert isinstance(q._selections[0], Example)

    # not yet implemented
    #q.select(Example.other)
    #assert q._selections == [Example.other]

    #with pytest.raises(SelectTypeMistmatch) as e:
    #    q.select(Example, Example.ex_predicate)

    with pytest.raises(InvalidQueryItem) as e:
        q.select(MagicMock)

def test_make_query():
    q = query()

    q.select(Example).where(ex_predicate="hello").all()
    print(str(q))

    #assert False
