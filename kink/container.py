from types import LambdaType
from typing import Any, Dict, Type, Union, Callable

from kink.errors.service_error import ServiceError


class Container:
    def __init__(self):
        self._memoized_services: Dict[Union[str, Type], Any] = {}
        self._services: Dict[Union[str, Type], Any] = {}
        self._factories: Dict[Union[str, Type], Callable[[Container], Any]] = {}

    def __setitem__(self, key: Union[str, Type], value: Any) -> None:
        self._services[key] = value

        if key in self._memoized_services:
            del(self._memoized_services[key])

    def __getitem__(self, key: Union[str, Type]) -> Any:
        if key in self._factories:
            return self._factories[key](self)

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
        return key in self._services or key in self._factories

    @property
    def factories(self) -> Dict[Union[str, Type], Callable[['Container'], Any]]:
        return self._factories

    def clear_cache(self) -> None:
        self._memoized_services = {}


di: Container = Container()


__all__ = ["Container", "di"]
