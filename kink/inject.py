import asyncio
import functools
import sys
from abc import ABC
from functools import wraps
from inspect import Parameter as InspectParameter, isclass, signature
from typing import Any, Callable, Dict, NewType, Tuple, Type, TypeVar, Union, ForwardRef, Optional  # type: ignore

from typing_extensions import Protocol

from .container import di, Container
from .errors import ExecutionError

T = TypeVar("T")
S = TypeVar("S")

ServiceDefinition = Union[Type[S], Callable]
ServiceResult = Union[S, Callable]


Undefined = NewType("Undefined", int)


class _ProtocolInit(Protocol):
    pass


_no_init = _ProtocolInit.__init__


def _resolve_forward_reference(module: Any, ref: Union[str, ForwardRef]) -> Any:
    if isinstance(ref, str):
        name = ref
    else:
        name = ref.__forward_arg__

    if name in sys.modules[module].__dict__:
        return sys.modules[module].__dict__[name]

    return None


class Parameter:
    type: Any
    name: str
    default: Any

    def __init__(self, name: str, type: Any = Any, default: Any = Undefined):
        self.name = name
        self.type = type
        self.default = default


def _inspect_function_arguments(
    function: Callable,
) -> Tuple[Tuple[str, ...], Dict[str, Parameter]]:
    if isinstance(function, functools._lru_cache_wrapper):
        function = function.__wrapped__

    parameters_name: Tuple[str, ...] = tuple(signature(function).parameters.keys())
    parameters = {}

    for name, parameter in signature(function).parameters.items():

        if isinstance(parameter.annotation, (str, ForwardRef)) and hasattr(function, "__module__"):
            annotation = _resolve_forward_reference(function.__module__, parameter.annotation)
        else:
            annotation = parameter.annotation

        parameters[name] = Parameter(
            parameter.name,
            annotation,
            parameter.default if parameter.default is not InspectParameter.empty else Undefined,
        )

    return parameters_name, parameters


def _resolve_function_kwargs(
    alias_map: Dict[str, str],
    parameters_name: Tuple[str, ...],
    parameters: Dict[str, Parameter],
    container: Container,
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


def _decorate(binding: Dict[str, Any], service: ServiceDefinition, container: Container) -> ServiceResult:

    # ignore abstract class initialiser and protocol initialisers
    if service in [ABC.__init__, _no_init] or service.__name__ in [
        "_no_init",
        "_no_init_or_replace_init",
    ]:  # FIXME: fix this when typing_extensions library gets fixed
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
        if set(passed_kwargs.keys()) == set(parameters_name):
            return passed_kwargs

        # do not resolve for passed kwargs and args
        parameters_name_to_resolve = tuple(parameters_name - passed_kwargs.keys())

        resolved_kwargs = _resolve_function_kwargs(binding, parameters_name_to_resolve, parameters, container)

        all_kwargs = {**resolved_kwargs, **passed_kwargs}

        if len(all_kwargs) < len(parameters_name):
            missing_parameters = [arg for arg in parameters_name if arg not in all_kwargs]
            raise ExecutionError(
                "Cannot execute function without required parameters. "
                + f"Did you forget to bind the following parameters: `{'`, `'.join(missing_parameters)}` inside the service `{service}`?"
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
        return _async_decorated

    return _decorated


def inject(
    _service: Optional[ServiceDefinition] = None,
    alias: Optional[Any] = None,
    bind: Optional[Dict[str, Any]] = None,
    container: Container = di,
    use_factory: bool = False,
) -> Union[ServiceResult, Callable[[ServiceDefinition], ServiceResult]]:
    def _decorator(_service: ServiceDefinition) -> ServiceResult:
        if isclass(_service):
            setattr(
                _service,
                "__init__",
                _decorate(bind or {}, getattr(_service, "__init__"), container),
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
        return _decorator

    return _decorator(_service)


__all__ = ["inject"]
