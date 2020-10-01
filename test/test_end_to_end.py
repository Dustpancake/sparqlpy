import pytest

from unittest.mock import call as MockCall
from unittest.mock import MagicMock

from sparqly import query, Item
from sparqly.query import (
    InvalidQueryItem,
    InvalidQuery,
    SelectTypeMistmatch
)

class Example1(Item):
    ex_predicate = "predicate"
    something_else = "PS:213989"
    other = "QMP:313"
class Example2(Item):
    ex_predicate = "predicate"
    something_else = "PS:213989"
    other = "QMP:313"

def test_reset():
    q = query()
    q._reset = MagicMock()
    q._select = MagicMock()

    # implicitly asserts that Example1 is of type Item
    q.select(Example1)
    q._reset.assert_called_with()

def test_select_item():
    q = query()

    q.select(Example1)
    assert isinstance(q._selections["subject"][0], Example1)

    with pytest.raises(InvalidQueryItem) as e:
        q.select(MagicMock)

def test_make_query():
    q = query()

    q.select(Example1).where(ex_predicate="hello").all()
    assert str(q) == (
        "SELECT ?Example1 WHERE {\n\t?Example1 predicate hello .\n}"
    )


    q.select(Example1).where(ex_predicate="hello", other="world").all()
    assert str(q) == (
        "SELECT ?Example1 WHERE {"
        "\n\t?Example1 predicate hello ;"
        "\n\tQMP:313 world .\n}"
    )

    q.select(Example1, Example2).where(
        {"ex_predicate": "hello"}, {"other": "world"}
    ).all()

    assert str(q) == (
        "SELECT ?Example1 ?Example2 WHERE {"
        "\n\t?Example1 predicate hello ."
        "\n\t?Example2 QMP:313 world .\n}"
    )

@pytest.mark.hare
def test_query_object():
    q = query()

    #q.select(Example1.ex_predicate).where(Example1="something")
