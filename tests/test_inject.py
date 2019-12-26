import pytest

from kink import inject
from kink import set_resolver
from kink.errors import BindingError
from kink.errors import ExecutionError
from kink.resolvers import SimpleResolver


def test_can_call_bound_function():
    set_resolver(SimpleResolver)

    @inject(a=1, b="test")
    def test_unit(a: int, b: str):
        return {"a": a, "b": b}

    assert test_unit() == {"a": 1, "b": "test"}
    assert test_unit(2, "test_2") == {"a": 2, "b": "test_2"}
    assert test_unit(b="test_3") == {"a": 1, "b": "test_3"}
    assert test_unit(a=3) == {"a": 3, "b": "test"}


def test_can_resolve_bound_function():
    set_resolver(SimpleResolver)

    def get_config():
        return {"a": 1, "b": 2}

    @inject(config=get_config)
    def test_unit(config: dict):
        return [config["a"], config["b"]]

    assert test_unit() == [1, 2]
    assert test_unit({"a": 2, "b": 4}) == [2, 4]


def test_can_resolve_nested_bound_function():
    set_resolver(SimpleResolver)

    def get_config():
        return {"a": 1, "b": 2}

    @inject(config=get_config)
    def get_b(config: dict):
        return config["b"]

    @inject(config=get_config)
    def get_a(config: dict):
        return config["a"]

    @inject(a=get_a, b=get_b)
    def test_unit(a: int, b: int):
        return [a, b]

    assert test_unit() == [1, 2]
    assert get_a() == 1
    assert get_b() == 2
    assert test_unit(2) == [2, 2]


def test_fail_on_invalid_bind():
    set_resolver(SimpleResolver)

    with pytest.raises(BindingError):

        @inject(b=2)
        def test_unit(a: int):
            ...


def test_fail_on_calling_incomplete_bind():
    set_resolver(SimpleResolver)

    @inject(b=2)
    def test_unit(a: int, b: int):
        return [a, b]

    with pytest.raises(ExecutionError):
        test_unit()


def test_bind_initialiser():
    set_resolver(SimpleResolver)

    class ConstructorInjection:
        @inject(a=1, b=2)
        def __init__(self, a: int, b: int):
            self.a = a
            self.b = b

    instance = ConstructorInjection()
    assert instance.a == 1
    assert instance.b == 2

    instance = ConstructorInjection(2)
    assert instance.a == 2
    assert instance.b == 2

    instance = ConstructorInjection(b=3)
    assert instance.a == 1
    assert instance.b == 3

    instance = ConstructorInjection(a=3)
    assert instance.a == 3
    assert instance.b == 2

    instance = ConstructorInjection(0, 0)
    assert instance.a == 0
    assert instance.b == 0


def test_inject_factory_which_returns_callable():
    set_resolver(SimpleResolver)

    def resolve_a():
        def _inner_a():
            return "a"

        return _inner_a

    class A:
        @inject(a=resolve_a)
        def get_a(self, a):
            return a()

    instance = A()

    assert instance.get_a() == "a"
    assert instance.get_a() == "a"
