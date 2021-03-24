from kink import Container
import time


def test_instantiate_simple_container():
    container = Container()
    assert isinstance(container, Container)


def test_set_value():
    container = Container()
    container["item"] = "value"

    assert "item" in container


def test_get_value():
    container = Container()
    container["item"] = "value"

    assert container["item"] == "value"


def test_get_factored_service():
    container = Container()
    container["parent_item"] = "value"
    container["item"] = lambda di: di["parent_item"]

    assert container["item"] == "value"


def test_get_callable_service():
    def test_1():
        return 1

    container = Container()
    container["test_1"] = test_1
    container["test_2"] = lambda di: 12

    assert container["test_1"]() == 1
    assert container["test_2"] == 12


def test_set_class_as_service() -> None:
    class A:
        ...

    container = Container()
    container[A] = A()

    assert A in container
    assert container[A] == container[A]
    assert isinstance(container[A], A)


def test_set_factored_service() -> None:
    class A:
        ...
    container = Container()
    container.factories[A] = lambda di: A()

    assert A in container
    assert container[A] != container[A]
    assert isinstance(container[A], A)


def test_clear_cache() -> None:
    container = Container()
    container['time'] = lambda di: time.time_ns()

    time_a = container['time']
    time_b = container['time']

    assert time_a == time_b

    container.clear_cache()
    time_c = container['time']
    time_d = container['time']

    assert time_c != time_a
    assert time_c == time_d
