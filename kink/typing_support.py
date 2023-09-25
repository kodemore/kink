from __future__ import annotations

from typing import List, Optional, Type, Union


def get_origin_type(type_name: Type) -> Optional[Type]:
    return getattr(type_name, "__origin__", None)


def get_type_args(type_name: Type) -> List[Type]:
    return getattr(type_name, "__args__", [])


def is_optional(type_name: Type) -> bool:
    return (
        get_origin_type(type_name) is Union
        and bool(get_type_args(type_name))
        and get_type_args(type_name)[-1] is type(None)  # noqa
    )


def unpack_optional(type_name: Type) -> Type:
    return get_type_args(type_name)[0]
