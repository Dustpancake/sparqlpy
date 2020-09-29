import pytest

from unittest.mock import call as MockCall
from unittest.mock import MagicMock


from sparqly.query import (
    query,
    InvalidQuery,
    InvalidQueryItem,
    SelectWhereMistmatch,
    InvalidPredicate,
    NoSuchPredicate
)

def test_constructor_args():
    q = query()
    assert q._query == ""
    assert q._selections == []

def test_get_attr():
    q = query()
    assert q._query == ""
    with pytest.raises(AttributeError) as e:
        q.aabbccdd

def test_to_string():
    q = query()
    with pytest.raises(InvalidQuery) as e:
        str(q)


class MockItem():
    _predicates = ["example", "other"]
    example = "test_example"
    other = "something_else"
class MockItem2():
    _predicates = ["something"]
    something = "other"
class MockItem3:
    pred1 = "new_pred1"
    pred2 = "new_pred2"
    def __getitem__(self, i):
        return self.__getattribute__(i)

@pytest.fixture
def mockitem():
    return MockItem()

class TestSelect:

    def test_arguments(self):
        q = query()
        with pytest.raises(TypeError) as e:
            q.select()

    def test_item_instatiation(self):
        q = query()
        with pytest.raises(InvalidQueryItem) as e:
            q._select(MockItem)

    def test_valid_instances(self):
        q = query()

        with pytest.raises(TypeError) as e:
            q.select()
        with pytest.raises(InvalidQueryItem) as e:
            q.select(MagicMock)

    def test_single(self):
        q = query()
        # class
        m = MockItem()
        q._select(m)
        assert q._selections == [m]

    def test_many(self):
        q = query()
        m = MockItem()
        m2 = MockItem2()
        q._select(m, m2)
        assert q._selections == [m, m2]

    def test_non_item(self):
        q = query()
        with pytest.raises(NotImplementedError) as e:
            q.select(MockItem.example)

        with pytest.raises(InvalidQueryItem) as e:
            q.select(str)

class TestWhere:

    def test_where_kw(self):
        q = query()
        m = MockItem()

        q._where_kwargs(
            m,
            **{"example":"o1", "other":"o2"}
        )
        assert dict(q._tripples) == {m:
            {"example": ["o1"], "other": ["o2"]}
        }

        q._where_kwargs(
            m,
            **{"example":"o3"}
        )
        assert dict(q._tripples) == {m:
            {"example": ["o1", "o3"], "other": ["o2"]}
        }

        m2 = MockItem2()
        q._where_kwargs(
            m2,
            **{"something":"o4"}
        )
        assert dict(q._tripples) == {
        m:
            {"example": ["o1", "o3"], "other": ["o2"]},
        m2:
            {"something": ["o4"]}
        }

    def test_single_where(self):
        q = query()
        q._where_kwargs = MagicMock()
        m = MockItem()
        q._selections = [m]

        # mismatch
        with pytest.raises(SelectWhereMistmatch) as e:
            q.where()

        # keyword
        q.where(example="test_example")
        q._where_kwargs.assert_called_with(
            m,
            example="test_example"
        )

        # dictionary
        q.where({"example":"test_example"})
        q._where_kwargs.assert_called_with(
            m,
            example="test_example"
        )

        # dictionary
        q.where({"example":"test_example", "other":"something"})
        q._where_kwargs.assert_called_with(
            m,
            example="test_example",
            other="something"
        )

    def test_many_where(self):
        q = query()
        q._where_kwargs = MagicMock()
        q._selections = [MockItem.example, MockItem.other]

        with pytest.raises(SelectWhereMistmatch) as e:
            q.where(
                {"example": "test_example"},
                {"example2": "test_example2"},
                {"example3": "test_example3"}
            )
        with pytest.raises(SelectWhereMistmatch) as e:
            q.where(
                {"example2":"test_example2"}
            )

        q.where(
            {"example": "test_example"},
            {"other": "test_example", "example": "something"}
        )

        q._where_kwargs.assert_has_calls([
            MockCall(
                MockItem.example,
                example="test_example",
            ),
            MockCall(
                MockItem.other,
                example="something",
                other="test_example"
            )
        ])

    def test_bad_predicates(self):
        q = query()
        q._selections = [MockItem]
        with pytest.raises(InvalidPredicate) as e:
            q._where_kwargs(MockItem, aabbcc="123")

class TestMakeQuery:

    def test_make_tripple(self):
        q = query()

        m = MagicMock()
        m.__repr__ = lambda x: "MagicMock"
        res = q._make_tripple(
            m,
            {"other": ["test_example"], "example": ["something"]}
        )
        assert res == "MagicMock other test_example ;\n\texample something ."

    def test_assemble_query(self):
        q = query()

        q._fetch_predicate_names = MagicMock(
            return_value = {"something_else": ["object1"], "test_example": ["object2"]}
        )

        q._make_tripple = MagicMock(
            return_value = "?MagicMock something_else object1 ;\n\ttest_example object2 ."
        )

        q._tripples = {"MagicMock" : {"other": ["object1"], "example": ["object2"]}}
        q._assemble_query()
        q._make_tripple.assert_called_with(
            "?MagicMock",
            {"something_else": ["object1"], "test_example": ["object2"]}
        )
        print(q._query)
        assert q._query == (
            "SELECT ?MagicMock WHERE {"
            "\n\t?MagicMock something_else object1 ;"
            "\n\ttest_example object2 ."
            "\n}"
        )

    def test_fetch_predicate_names(self):
        q = query()
        m = MockItem3()
        doubles = {"pred1": ["object1"], "pred2": ["object2"]}

        res = q._fetch_predicate_names(m, doubles)
        assert res == {"new_pred1": ["object1"], "new_pred2": ["object2"]}

        with pytest.raises(NoSuchPredicate) as e:
            res = q._fetch_predicate_names(m, {"bad_predicate": "object1"})
