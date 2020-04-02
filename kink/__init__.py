from inspect import isclass
from inspect import signature
from types import LambdaType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Tuple
from typing import Type
from typing import Union
from abc import ABC

from kink.errors.resolver_error import ResolverError
from kink.errors.service_error import ServiceError
from .errors import ContainerError
from .errors import ExecutionError
from .errors import ResolverError


class Container:
    def __init__(self, memoize: bool = True):
        self.memoize = memoize
        self._memoized_services: Dict[Union[str, Type], Any] = {}
        self._services: Dict[Union[str, Type], Any] = {}

    def __setitem__(self, key: Any, value: Any) -> None:
        self._services[key] = value

    def __getitem__(self, key: Any) -> Any:
        if key in self._memoized_services:
            return self._memoized_services[key]

        if key not in self:
            raise ServiceError(f"Service {key} is not registered.")

        value = self._services[key]

        if isinstance(value, LambdaType) and value.__name__ == "<lambda>":
            self._memoized_services[key] = value(self)
            return self._memoized_services[key]

        return value

    def __contains__(self, key) -> bool:
        return key in self._services


di: Container = Container()


def _inspect_function_arguments(
    function: Callable,
) -> Tuple[Tuple[str, ...], Dict[str, type]]:
    argument_names: Tuple[str, ...] = tuple(signature(function).parameters.keys())
    argument_types = {}

    for name in argument_names:
        if name in function.__annotations__:
            argument_types[name] = function.__annotations__[name]
        else:
            argument_types[name] = Any

    return argument_names, argument_types


def _resolve_function_kwargs(
    alias_map: Dict[str, str],
    argument_names: Tuple[str, ...],
    argument_types: Dict[str, type],
) -> Dict[str, Any]:
    resolved_kwargs = {}
    for name in argument_names:
        if name in alias_map and alias_map[name] in di:
            resolved_kwargs[name] = di[alias_map[name]]
            continue

        if name in di:
            resolved_kwargs[name] = di[name]
            continue

        if argument_types[name] in di:
            resolved_kwargs[name] = di[argument_types[name]]
            continue

    return resolved_kwargs


def _decorate(alias_map: Dict[str, str], function: type):  # type: ignore

    # ignore abstract class initializer
    if function == ABC.__init__:
        return function

    # Add class definition to dependency injection
    argument_names, argument_types = _inspect_function_arguments(function)
    cached_kwargs: Dict[str, Any] = {}

    def _decorated(*args, **kwargs):
        nonlocal cached_kwargs

        # all arguments were passed
        if len(args) == len(argument_names):
            return function(*args)

        if not cached_kwargs:
            cached_kwargs = _resolve_function_kwargs(
                alias_map, argument_names, argument_types
            )

        # attach named arguments
        passed_kwargs = {**kwargs}

        # resolve positional arguments
        if args:
            for key, value in enumerate(args):
                passed_kwargs[argument_names[key]] = value

        all_kwargs = {**cached_kwargs, **passed_kwargs}

        if len(all_kwargs) < len(argument_names):
            raise ExecutionError(
                "Cannot execute function without required parameters. Did you forget to bind required parameters?"
            )

        return function(**all_kwargs)

    return _decorated


def inject(**alias_map: str):
    def _decorator(obj: type):
        if isclass(obj):
            di[obj] = lambda di: obj()
            setattr(obj, "__init__", _decorate(alias_map, getattr(obj, "__init__")))
            return obj

        return _decorate(alias_map, obj)

    return _decorator


__all__ = ["inject", "Container", "di"]
