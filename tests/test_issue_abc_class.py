from abc import ABC

from kink import di, inject


class BaseClass(ABC):
    pass


@inject()
class ConcreteClass(BaseClass):
    pass


def test_can_register_abstract_class():
    instance = di[ConcreteClass]

    assert isinstance(instance, ConcreteClass)
