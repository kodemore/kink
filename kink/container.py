from types import LambdaType
from typing import Any, Dict, Type, Union, Callable, List, Generic

from kink.errors.service_error import ServiceError


class Container:
    def __init__(self):
        self._memoized_services: Dict[Union[str, Type], Any] = {}
        self._services: Dict[Union[str, Type], Any] = {}
        self._factories: Dict[Union[str, Type], Callable[[Container], Any]] = {}
        self._aliases: Dict[Union[str, Type], List[Union[str, Type]]] = {}

    def __setitem__(self, key: Union[str, Type], value: Any) -> None:
        self._services[key] = value

        if key in self._memoized_services:
            del self._memoized_services[key]

    def add_alias(self, name: Union[str, Type], target: Union[str, Type]):
        if List[target] in self._memoized_services:  # type: ignore
            del self._memoized_services[List[target]]  # type: ignore

        if name not in self._aliases:
            self._aliases[name] = []
        self._aliases[name].append(target)

    def __getitem__(self, key: Union[str, Type]) -> Any:
        if key in self._factories:
            return self._factories[key](self)

        service = self._get(key)

        if service is not None:
            return service

        if key in self._aliases:
            service = self._get(self._aliases[key][0])  # By default return first aliased service

        if service is not None:
            return service

        # Support aliasing
        if self._has_alias_list_for(key):
            result = [self._get(alias) for alias in self._aliases[key.__args__[0]]]  # type: ignore
            self._memoized_services[key] = result
            return result

        raise ServiceError(f"Service {key} is not registered.")

    def _get(self, key: Union[str, Type]) -> Any:
        if key in self._memoized_services:
            return self._memoized_services[key]

        if key not in self._services:
            return None

        value = self._services[key]

        if isinstance(value, LambdaType) and value.__name__ == "<lambda>":
            self._memoized_services[key] = value(self)
            return self._memoized_services[key]

        return value

    def __contains__(self, key) -> bool:
        contains = key in self._services or key in self._factories or key in self._aliases

        if contains:
            return contains

        if self._has_alias_list_for(key):
            return True

        return False

    def _has_alias_list_for(self, key: Union[str, Type]) -> bool:
        return hasattr(key, "__origin__") and hasattr(key, "__args__") and key.__origin__ == list and key.__args__[0] in self._aliases  # type: ignore

    @property
    def factories(self) -> Dict[Union[str, Type], Callable[["Container"], Any]]:
        return self._factories

    def clear_cache(self) -> None:
        self._memoized_services = {}


di: Container = Container()


__all__ = ["Container", "di"]
