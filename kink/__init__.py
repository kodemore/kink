from inspect import isclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import Tuple
from typing import Type
from typing import Union

from .errors import DependencyError
from .errors import ExecutionError
from .errors import ResolverError
from .resolvers.kv_resolver import KVResolver
from .resolvers.resolver import Resolver
from .resolvers.simple_resolver import SimpleResolver

RESOLVER: Union[Callable, Type[Resolver]] = SimpleResolver


def set_resolver(resolver: Union[Type[Resolver], dict, Callable]):
    global RESOLVER
    if isinstance(resolver, dict):
        resolver = KVResolver(resolver)
    elif not callable(resolver) and not issubclass(resolver, Resolver):
        raise DependencyError(
            "Invalid resolver passed to inject decorator, expected: callable, Resolver or dict."
        )

    RESOLVER = resolver


def _inspect_function_arguments(
    function: Callable,
) -> Tuple[Tuple[str, ...], Dict[str, type]]:
    argument_names: Tuple[str, ...] = function.__code__.co_varnames
    argument_types = {}
    for name in argument_names:
        if name in function.__annotations__:
            argument_types[name] = function.__annotations__[name]
        else:
            argument_types[name] = Any

    return argument_names, argument_types


def _instantiate_resolver(
    function: Callable, resolver: Union[Type[Resolver], Callable], resolver_args
) -> Callable:
    if isclass(resolver):
        return resolver(function, **resolver_args)  # type: ignore

    return resolver


def inject(**resolver_args):
    global RESOLVER

    def _decorate(function: Callable):
        argument_names, argument_types = _inspect_function_arguments(function)
        resolve = _instantiate_resolver(function, RESOLVER, resolver_args)

        def _decorated(*args, **kwargs):
            # all arguments were passed
            if len(args) == len(argument_names):
                return function(*args)

            # attach named arguments
            resolved_arguments = {**kwargs}

            # resolve positional arguments
            if args:
                for key, value in enumerate(args):
                    resolved_arguments[argument_names[key]] = value

            missing_arguments = argument_names - resolved_arguments.keys()

            for name in missing_arguments:
                try:
                    resolved_arguments[name] = resolve(
                        name, argument_types[name], function
                    )
                except ResolverError:
                    continue

            if len(resolved_arguments) < len(argument_names):
                raise ExecutionError(
                    "Cannot execute function without required parameters. Did you forget to bind required parameters?"
                )

            return function(**resolved_arguments)

        return _decorated

    return _decorate


__all__ = ["inject", "set_resolver"]
