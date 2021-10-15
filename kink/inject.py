import asyncio
from functools import wraps
from abc import ABC
from inspect import Parameter as InspectParameter, isclass, signature
from typing import Any, Callable, Dict, NewType, Tuple, Type, TypeVar

from typing_extensions import Protocol

from .container import di, Container
from .errors import ExecutionError

T = TypeVar("T")


Undefined = NewType("Undefined", int)


class _ProtocolInit(Protocol):
    pass


_no_init = _ProtocolInit.__init__


class Parameter:
    type: Any
    name: str
    default: Any

    def __init__(self, name: str, type: Any = Any, default: Any = Undefined):
        self.name = name
        self.type = type
        self.default = default


def _inspect_function_arguments(function: Callable,) -> Tuple[Tuple[str, ...], Dict[str, Parameter]]:
    parameters_name: Tuple[str, ...] = tuple(signature(function).parameters.keys())
    parameters = {}

    for name, parameter in signature(function).parameters.items():
        parameters[name] = Parameter(
            parameter.name,
            parameter.annotation,
            parameter.default if parameter.default is not InspectParameter.empty else Undefined,
        )

    return parameters_name, parameters


def _resolve_function_kwargs(
    alias_map: Dict[str, str], parameters_name: Tuple[str, ...], parameters: Dict[str, Parameter], container: Container,
) -> Dict[str, Any]:
    resolved_kwargs = {}
    for name in parameters_name:
        if name in alias_map and alias_map[name] in container:
            resolved_kwargs[name] = container[alias_map[name]]
            continue

        if name in container:
            resolved_kwargs[name] = container[name]
            continue

        if parameters[name].type in container:
            resolved_kwargs[name] = container[parameters[name].type]
            continue

        if parameters[name].default is not Undefined:
            resolved_kwargs[name] = parameters[name].default

    return resolved_kwargs


def _decorate(binding: Dict[str, Any], service: Type[T], container: Container) -> Type[T]:  # type: ignore

    # ignore abstract class initialiser and protocol initialisers
    if (
        service in [ABC.__init__, _no_init] or service.__name__ == "_no_init"
    ):  # FIXME: fix this when typing_extensions library gets fixed
        return service

    # Add class definition to dependency injection
    parameters_name, parameters = _inspect_function_arguments(service)

    def _resolve_kwargs(args, kwargs) -> dict:
        # attach named arguments
        passed_kwargs = {**kwargs}

        # resolve positional arguments
        if args:
            for key, value in enumerate(args):
                passed_kwargs[parameters_name[key]] = value

        # prioritise passed kwargs and args resolving
        if len(passed_kwargs) == len(parameters_name):
            return passed_kwargs

        resolved_kwargs = _resolve_function_kwargs(binding, parameters_name, parameters, container)

        all_kwargs = {**resolved_kwargs, **passed_kwargs}

        if len(all_kwargs) < len(parameters_name):
            missing_parameters = [arg for arg in parameters_name if arg not in all_kwargs]
            raise ExecutionError(
                "Cannot execute function without required parameters. "
                + f"Did you forget to bind the following parameters: `{'`, `'.join(missing_parameters)}`?"
            )

        return all_kwargs

    @wraps(service)
    def _decorated(*args, **kwargs):
        # all arguments were passed
        if len(args) == len(parameters_name):
            return service(*args, **kwargs)

        if parameters_name == tuple(kwargs.keys()):
            return service(**kwargs)

        all_kwargs = _resolve_kwargs(args, kwargs)
        return service(**all_kwargs)

    @wraps(service)
    async def _async_decorated(*args, **kwargs):
        # all arguments were passed
        if len(args) == len(parameters_name):
            return await service(*args)

        if parameters_name == tuple(kwargs.keys()):
            return await service(**kwargs)

        all_kwargs = _resolve_kwargs(args, kwargs)
        return await service(**all_kwargs)

    if asyncio.iscoroutinefunction(service):
        return _async_decorated  # type: ignore

    return _decorated  # type: ignore


def inject(
    _service: Any = None,
    alias: Any = None,
    bind: Dict[str, Any] = None,
    container: Container = di,
    use_factory: bool = False,
) -> Any:
    def _decorator(_service: Any) -> Any:
        if isclass(_service):
            setattr(
                _service, "__init__", _decorate(bind or {}, getattr(_service, "__init__"), container),
            )
            if use_factory:
                container.factories[_service] = lambda _di: _service()
                if alias:
                    container.add_alias(alias, _service)
            else:
                container[_service] = lambda _di: _service()
                if alias:
                    container.add_alias(alias, _service)

            return _service

        service_function = _decorate(bind or {}, _service, container)
        container[service_function.__name__] = service_function
        if alias:
            container.add_alias(alias, service_function.__name__)

        return service_function

    if _service is None:
        return _decorator  # type: ignore

    return _decorator(_service)


__all__ = ["inject"]
