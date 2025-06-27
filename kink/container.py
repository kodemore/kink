from types import LambdaType
from typing import Any, Dict, Type, Union, Callable, List, overload, TypeVar

from kink.errors.service_error import ServiceError
from kink.typing_support import is_optional, unpack_optional

_MISSING_SERVICE = object()


T = TypeVar("T")


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

    def __delitem__(self, key: Union[str, Type]) -> None:
        """Remove a service from the container."""
        service_exists = False

        # Remove from services
        if key in self._services:
            del self._services[key]
            service_exists = True

        # Remove from factories
        if key in self._factories:
            del self._factories[key]
            service_exists = True

        # Remove from memoized services
        if key in self._memoized_services:
            del self._memoized_services[key]

        # Remove from aliases (if key is used as an alias target)
        aliases_to_remove = []
        for alias_name, targets in self._aliases.items():
            if key in targets:
                targets.remove(key)
                if not targets:  # Remove empty alias lists
                    aliases_to_remove.append(alias_name)

        for alias_name in aliases_to_remove:
            del self._aliases[alias_name]

        # Remove if key is an alias itself
        if key in self._aliases:
            del self._aliases[key]

        # Clear any List[key] memoized services
        if List[key] in self._memoized_services:  # type: ignore
            del self._memoized_services[List[key]]  # type: ignore

        if not service_exists:
            raise KeyError(f"Service {key} is not registered.")

    def add_alias(self, name: Union[str, Type], target: Union[str, Type]):
        if List[target] in self._memoized_services:  # type: ignore
            del self._memoized_services[List[target]]  # type: ignore

        if name not in self._aliases:
            self._aliases[name] = []
        self._aliases[name].append(target)

    @overload
    def __getitem__(self, key: str) -> Any: ...

    @overload
    def __getitem__(self, key: Type[T]) -> T: ...

    def __getitem__(self, key):
        if key in self._factories:
            return self._factories[key](self)

        if is_optional(key):
            return self[unpack_optional(key)]

        service = self._get(key)

        if service is not _MISSING_SERVICE:
            return service

        if key in self._aliases:
            unaliased_key = self._aliases[key][0]  # By default return first aliased service
            if unaliased_key in self._factories:
                return self._factories[unaliased_key](self)
            service = self._get(unaliased_key)

        if service is not _MISSING_SERVICE:
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
            return _MISSING_SERVICE

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

        if is_optional(key):
            return unpack_optional(key) in self

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
