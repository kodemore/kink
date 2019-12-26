from inspect import signature
from typing import Any

from kink.errors.binding_error import BindingError
from kink.errors.resolver_error import ResolverError
from .resolver import Resolver


class SimpleResolver(Resolver):
    def __init__(self, function: object, memoize=True, **params):
        self.memoize = memoize
        self.params = params
        self.object = function
        self.memoized_values = {}
        arguments = tuple(signature(function).parameters.keys())  # type: ignore
        for param in params.keys():
            if param not in arguments:
                raise BindingError(
                    f"Tried to bind unknown argument `{param}` to {object.__module__}.{object.__class__}.{object.__name__}."
                )

    def __call__(self, param_name: str, param_type: type, context: type) -> Any:
        if param_name in self.params:
            if self.memoize:
                if param_name in self.memoized_values:
                    return self.memoized_values[param_name]
                if callable(self.params[param_name]):
                    self.memoized_values[param_name] = self.params[param_name]()
                    return self.memoized_values[param_name]

            return self.params[param_name]

        raise ResolverError(f"Could not resolve {param_name}")
