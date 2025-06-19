from unittest.mock import MagicMock

from kink import di, inject

def test_do_not_resolve_passed_kwargs() -> None:
    di["name"] = "Bob"
    @inject
    class ExpensiveObject:
        def __init__(self, name: str):
            self.name = name
            raise Exception("Constructing expensive object")

    @inject
    def greet(namer: ExpensiveObject, greeting: str = "Hello %s") -> str:
        return greeting % namer.name

    mock_expensive_object = MagicMock(spec=ExpensiveObject)
    mock_expensive_object.name = "Bill"

    assert greet(namer=mock_expensive_object) == "Hello Bill"

def test_do_not_resolve_passed_args() -> None:
    di["name"] = "Bob"
    @inject
    class ExpensiveObject:
        def __init__(self, name: str):
            self.name = name
            raise Exception("Constructing expensive object")

    @inject
    def greet(namer: ExpensiveObject, greeting: str = "Hello %s") -> str:
        return greeting % namer.name

    mock_expensive_object = MagicMock(spec=ExpensiveObject)
    mock_expensive_object.name = "Bill"

    assert greet(mock_expensive_object) == "Hello Bill"
