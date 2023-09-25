from typing import Optional

from kink import di
from kink import inject


def test_can_inject_optional_support_with_present_value() -> None:

    class Message:
        def __init__(self, value: str) -> None:
            self.value = value

    di[Message] = Message("Hello world")

    @inject()
    def inject_test(message: Optional[Message] = None):
        if message:
            return message.value
        return ""

    assert inject_test() == "Hello world"


def test_can_inject_optional_support_without_present_value() -> None:
    class Message:
        def __init__(self, value: str) -> None:
            self.value = value

    @inject()
    def inject_test(message: Optional[Message] = None):
        if message:
            return message.value
        return ""

    assert inject_test() == ""
