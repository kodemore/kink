from kink import di


def test_resolve_kwargs_and_ignore_default_parameters() -> None:
    class Name:
        def __init__(self, name: str):
            self.name = name

    di[Name] = lambda _di: Name("Bob")

    assert di[Name].name == "Bob"

    di[Name] = lambda _id: Name("Jay")

    assert di[Name].name == "Jay"
