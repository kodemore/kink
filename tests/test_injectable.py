from kink import Injectable, inject, di


def test_injectable() -> None:
    # given
    @inject
    class A:
        def __init__(self):
            self.value = ""

        def run(self, value: str):
            self.value = value

    @inject
    class Service:
        @inject()
        def run(self, value: str, injected: Injectable[A]) -> str:
            injected.run(value)
            return injected.value

    # when
    service: Service = di[Service]
    result = service.run("test")

    # then
    assert result == "test"
    assert di[A].value == "test"
