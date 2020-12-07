from kink import di, inject


def test_dont_resolve_parameters_on_named_parameters() -> None:
    di["name"] = "Bob"

    @inject()
    def greet(name: str, greeting: str) -> str:
        return greeting % name

    assert greet(name="", greeting="Hello %s") == "Hello "
