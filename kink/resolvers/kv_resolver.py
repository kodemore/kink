from typing import Any

from kink.errors.resolver_error import ResolverError
from .resolver import Resolver


class KVResolver(Resolver):
    def __init__(self, services: dict):
        self.services = services

    def __call__(self, param_name: str, param_type: type, context: type) -> Any:
        if param_name in self.services:
            return self.services[param_name]

        raise ResolverError(f"Could not resolve {param_name}")
