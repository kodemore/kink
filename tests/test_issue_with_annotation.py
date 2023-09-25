from __future__ import annotations

from kink import inject


@inject
class ClassB(object):
    def __init__(self) -> None:
        pass


@inject
class ClassA(object):
    def __init__(self, class_b: ClassB):
        self._class_b = class_b


def test_can_inject_with_annotations() -> None:
    assert isinstance(ClassA(), ClassA)
