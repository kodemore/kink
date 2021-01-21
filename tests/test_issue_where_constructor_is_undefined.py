from typing_extensions import Protocol

from kink import di, inject


class ExampleProtocol(Protocol):
    def run(self, a: int, b: int) -> int:
        ...


def test_that_auto_wiring_works_with_constructor():
    @inject(alias=ExampleProtocol)
    class ImplementationWithConstructor(ExampleProtocol):
        def __init__(self):
            pass

        def run(self, a: int, b: int) -> int:
            return a * b

    @inject
    class CompositionExample:
        def __init__(self, example: ExampleProtocol):
            self._example: ExampleProtocol = example

        def use_it(self, a: int, b: int) -> int:
            return self._example.run(a=a, b=b)

    di[ExampleProtocol] = ImplementationWithConstructor()
    composition_example = CompositionExample()
    assert composition_example.use_it(a=2, b=3) == 6


def test_that_auto_wiring_works_without_constructor():
    @inject(alias=ExampleProtocol)
    class ImplementationNoConstructor(ExampleProtocol):
        def run(self, a: int, b: int) -> int:
            return a + b

    @inject
    class CompositionExample:
        def __init__(self, example: ExampleProtocol):
            self._example: ExampleProtocol = example

        def use_it(self, a: int, b: int) -> int:
            return self._example.run(a=a, b=b)

    di[ExampleProtocol] = ImplementationNoConstructor()
    composition_example = CompositionExample()
    assert composition_example.use_it(a=2, b=3) == 5
