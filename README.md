# Kink [![Build Status](https://travis-ci.org/kodemore/kink.svg?branch=master)](https://travis-ci.org/kodemore/kink) [![codecov](https://codecov.io/gh/kodemore/kink/branch/master/graph/badge.svg)](https://codecov.io/gh/kodemore/kink)
Dependency injection made for python

## Features

- Easy to use interface
- Extensible with custom dependency resolvers
- Automatic dependency injection
- Lightweight
- Easy to test

## Installation

```
pip install kink
```

# Usage

## Simple dependency resolver

```python
from kink import inject
from os import getenv

@inject(dsn=getenv("DB_DSN"), password=getenv("DB_PASSWORD"))
def get_database(dsn: str, password: str):
    ...

connection = get_database() # Will use `dsn` and `password` from env vars
connection_with_custom_dsn = get_database("my_dsn") # Only `password` will be taken from env vars
connection_with_custom_password = get_database(password="secret")
```

### Nested dependencies resolving
```python
from kink import inject
from os import getenv

@inject(dsn=getenv("DB_DSN"), password=getenv("DB_PASSWORD"))
def get_database_settings(dsn: str, password: str):
    ...

@inject(db_settings=get_database_settings)
def get_db_connection(db_settings: dict):
    ...

# This will create partially injected function
@inject(db_connection=get_db_connection)
def get_user(user_id: int, db_connection) -> dict:
    ...

get_user(12) # will use injected connection, connection will not be established until `get_user` function is called.

mock_connection = ...
get_user(12, mock_connection) # you can easily mock connections
```

### Constructor injection
```python
from kink import inject

def get_connection():
    ...

class UserRepository:
    @inject(db_connection=get_connection)
    def __init__(self, unit_of_work, db_connection):
        ...
    
    def get(self, id: int):
        ...
```

## Setting dictionary as a resolver

```python
from kink import inject, set_resolver

set_resolver({
    "gimme_a": "a",
    "gimme_b": "b",
})

@inject()
def print_a_b_c(gimme_a: str, gimme_b: str, gimme_c: str):
    print(gimme_a, gimme_b, gimme_c)


print_a_b_c(gimme_c="c") # will print; a, b, c
```

## Defining custom dependency resolver

Kink supports two types of dependency resolvers:
- callables which accepts 3 parameters; property name, property type and context
- classes implementing `kink.resolvers.Resolver` protocol (see `simple_resolver.py` for example implementation)

```python
from kink import inject, set_resolver
from kink.errors import ResolverError


def resolve_dependency_by_type(param_name: str, param_type: type, context):
    if param_type is str:
        return "test"

    if param_type is int:
        return 1

    raise ResolverError()

set_resolver(resolve_dependency_by_type)

@inject()
def test_me(one: int, test: str):
    print(one, test)

test_me() # will print: 1, "test"
```
