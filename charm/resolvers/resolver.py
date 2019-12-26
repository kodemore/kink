from typing import Any
from typing_extensions import Protocol, runtime


@runtime
class Resolver(Protocol):
    def __call__(self, param_name: str, param_type: type, context: type) -> Any:
        ...
