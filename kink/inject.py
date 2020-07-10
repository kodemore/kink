from abc import ABC
import asyncio
from inspect import isclass, signature
from typing import Any, Callable, Dict, Tuple, Type, TypeVar

from .container import di
from .errors import ExecutionError

T = TypeVar("T")


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


def _decorate(binding: Dict[str, Any], service: Type[T]) -> Type[T]:  # type: ignore

    # ignore abstract class initializer
    if service == ABC.__init__:
        return service

    # Add class definition to dependency injection
    argument_names, argument_types = _inspect_function_arguments(service)
    cached_kwargs: Dict[str, Any] = {}

    def _resolve_kwargs(args, kwargs) -> dict:
        nonlocal cached_kwargs

        if not cached_kwargs:
            cached_kwargs = _resolve_function_kwargs(
                binding, argument_names, argument_types
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

        return all_kwargs

    def _decorated(*args, **kwargs):
        # all arguments were passed
        if len(args) == len(argument_names):
            return service(*args)

        all_kwargs = _resolve_kwargs(args, kwargs)
        return service(**all_kwargs)

    async def _async_decorated(*args, **kwargs):
        # all arguments were passed
        if len(args) == len(argument_names):
            return await service(*args)

        all_kwargs = _resolve_kwargs(args, kwargs)
        return await service(**all_kwargs)
    
    if asyncio.iscoroutinefunction(service):
        return _async_decorated  # type: ignore

    return _decorated  # type: ignore


def inject(
    _service: Type[T] = None, alias: Any = None, bind: Dict[str, Any] = None
) -> Type[T]:
    def _decorator(_service: Type[T]) -> Type[T]:
        if isclass(_service):
            di[_service] = lambda _di: _service()
            setattr(
                _service,
                "__init__",
                _decorate(bind or {}, getattr(_service, "__init__")),
            )
            if alias:
                di[alias] = lambda _di: _di[_service]

            return _service
        service_function = _decorate(bind or {}, _service)
        if alias:
            di[alias] = service_function

        return service_function

    if _service is None:
        return _decorator  # type: ignore

    return _decorator(_service)


__all__ = ["inject"]
