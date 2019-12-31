from kink import Container


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


def test_set_class_as_service():
    class A:
        ...

    container = Container()
    container[A] = A()

    assert A in container
