import pytest

from sparqly.item import Item

class Example(Item):
    # ?Example ex_predicate predicate
    ex_predicate = "predicate"
    something_else = "other"

def test_feature_extraction():
    ex = Example()
    assert ex._predicates.sort() is ["ex_predicate", "something_else"].sort()
    with pytest.raises(NotImplementedError) as e:
        ex._predicates = "test"

def test_repr():
    ex = Example()
    assert repr(ex) == "Example"

def test_predicate_retrieval():
    ex = Example()
    assert ex["ex_predicate"] == "predicate"
