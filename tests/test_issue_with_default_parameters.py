from kink import di, inject


def test_resolve_kwargs_and_ignore_default_parameters() -> None:
    di["name"] = "Bob"

    @inject()
    def greet(name: str, greeting: str = "Hello %s") -> str:
        return greeting % name

    assert greet() == "Hello Bob"
    assert greet(greeting="Hiya %s") == "Hiya Bob"
    assert greet(greeting="Aloha %s") == "Aloha Bob"
