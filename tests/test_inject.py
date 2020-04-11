from typing import Dict, Union

from kink import di
from kink import inject

di["a"] = 1
di["b"] = "test"
di["c"] = 2
di["d"] = "test_2"
di["message"] = "Hello, Tom"


def test_can_inject_values_to_function() -> None:
    @inject()
    def inject_test(a: int, b: str):
        return {"a": a, "b": b}

    assert inject_test() == {"a": 1, "b": "test"}


def test_can_override_injected_values() -> None:
    @inject()
    def inject_test(a: int, b: str):
        return {"a": a, "b": b}

    assert inject_test(12) == {"a": 12, "b": "test"}
    assert inject_test(b="test_2") == {"a": 1, "b": "test_2"}
    assert inject_test(12, "test_2") == {"a": 12, "b": "test_2"}
    assert inject_test() == {"a": 1, "b": "test"}


def test_can_do_constructor_injection() -> None:
    @inject()
    class A:
        def __init__(self, message: str):
            self.message = message

    instance = A()
    assert instance.message == "Hello, Tom"
    instance = A("Hello, Jack")
    assert instance.message == "Hello, Jack"


def test_map_dependencies() -> None:
    @inject(alias="map_dependencies", bind={"a": "c", "b": "d"})
    def map_dependencies_test(a: int, b: str) -> Dict[str, Union[str, int]]:
        return {"a": a, "b": b}

    assert di["map_dependencies"]
    assert map_dependencies_test() == {"a": 2, "b": "test_2"}
    assert di["map_dependencies"]() == map_dependencies_test()


def test_resolve_complex_dependencies() -> None:
    @inject
    class A:
        def __init__(self, message: str):
            self.message = message

    @inject
    class B:
        def __init__(self, a: int, a_inst: A):
            self.a = a
            self.a_inst = a_inst

    @inject
    class C:
        def __init__(self, a_inst: A, b_inst: B):
            self.a_inst = a_inst
            self.b_inst = b_inst

    c_inst = C()

    assert c_inst.a_inst == di[A]
    assert c_inst.b_inst == di[B]
    assert c_inst.a_inst == c_inst.b_inst.a_inst
    assert c_inst.a_inst.message == "Hello, Tom"


def test_aliasing() -> None:
    class IX:
        ...

    @inject(alias=IX)
    class X:
        ...

    assert di[X] == di[IX]
