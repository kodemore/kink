from charm import inject
from charm import set_resolver
from charm.errors import ResolverError


def resolve_dependency(param_name: str, param_type: type, context):
    if param_type is str:
        return "test"

    if param_type is int:
        return 1

    raise ResolverError()


def test_use_custom_resolver():
    set_resolver(resolve_dependency)

    @inject()
    def test_unit(one: int, test: str):
        return [one, test]

    assert test_unit() == [1, "test"]
    assert test_unit(2) == [2, "test"]


def test_use_custom_resolver_partially():
    set_resolver(resolve_dependency)

    @inject()
    def test_unit(one: int, unknown: dict):
        return [one, unknown]

    assert test_unit(unknown="test") == [1, "test"]
