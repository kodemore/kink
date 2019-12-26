from inspect import isclass
from typing import Any
from typing import Callable
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


def inject(**resolver_config):
    global RESOLVER
    resolver = RESOLVER

    def _decorate(func):
        argument_names = func.__code__.co_varnames
        argument_types = {}
        for name in argument_names:
            if name in func.__annotations__:
                argument_types[name] = func.__annotations__[name]
            else:
                argument_types[name] = Any

        if isclass(resolver):
            resolve = resolver(func, **resolver_config)
        else:
            resolve = resolver

        def _decorated(*args, **kwargs):
            # all arguments were passed
            if len(args) == len(argument_names):
                return func(*args)

            # attach named arguments
            resolved_arguments = {**kwargs}

            # resolve positional arguments
            if args:
                for key, value in enumerate(args):
                    resolved_arguments[argument_names[key]] = value

            missing_arguments = argument_names - resolved_arguments.keys()

            for name in missing_arguments:
                try:
                    resolved_arguments[name] = resolve(name, argument_types[name], func)
                except ResolverError:
                    continue

            if len(resolved_arguments) < len(argument_names):
                raise ExecutionError(
                    "Cannot execute function without required parameters. Did you forget to bind required parameters?"
                )

            return func(**resolved_arguments)

        setattr(_decorated, "__origin__", func)
        return _decorated

    return _decorate


__all__ = ["inject", "set_resolver"]
