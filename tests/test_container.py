from typing import List

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
    container['time'] = lambda di: time.time()

    time_a = container['time']
    time_b = container['time']

    assert time_a == time_b

    container.clear_cache()
    time_c = container['time']
    time_d = container['time']

    assert time_c != time_a
    assert time_c == time_d


def test_add_alias() -> None:
    # given
    class A:
        ...

    class B:
        ...

    class T:
        ...

    class T2:
        ...

    container = Container()

    # when
    container[A] = A()
    container[B] = B()
    container.add_alias(T, A)
    container.add_alias(T2, A)
    container.add_alias(T2, B)
    container.add_alias(T, B)

    # then
    assert container[T] == container[A]
    assert container[T2] == container[A]


def test_retrieve_all_aliased_items() -> None:
    # given
    class A:
        ...

    class B:
        ...

    class C:
        ...

    class T:
        ...

    container = Container()

    # when
    container[A] = A()
    container[B] = B()
    container[C] = C()
    container.add_alias(T, A)
    container.add_alias(T, B)
    container.add_alias(T, C)

    all_items = container[List[T]]
    all_items_cached = container[List[T]]

    # then
    assert len(all_items) == 3
    assert all_items[0] == container[A]
    assert all_items[1] == container[B]
    assert all_items[2] == container[C]
    assert id(all_items) == id(all_items_cached)
    assert List[T] in container

