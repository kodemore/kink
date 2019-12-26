from kink import inject
from kink import set_resolver

SERVICES = {
    "test": "test",
    "password": "secret",
    "one": 1,
    "two": 2,
}


def test_use_kv_resolver():
    set_resolver(SERVICES)

    @inject()
    def test_unit(one: int, test: str):
        return [one, test]

    assert test_unit() == [1, "test"]
    assert test_unit(2) == [2, "test"]


def test_use_kv_resolver_partially():
    set_resolver(SERVICES)

    @inject()
    def test_unit(one: int, unknown: str):
        return [one, unknown]

    assert test_unit(unknown="test") == [1, "test"]
