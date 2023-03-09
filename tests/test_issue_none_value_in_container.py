from kink import di


def test_allow_none_in_container_as_a_value() -> None:
    di["test"] = None

    assert di["test"] is None
