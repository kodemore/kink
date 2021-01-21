# Kink ![PyPI](https://img.shields.io/pypi/v/kink) ![Linting and Tests](https://github.com/kodemore/kink/workflows/Linting%20and%20Tests/badge.svg?branch=master) [![codecov](https://codecov.io/gh/kodemore/kink/branch/master/graph/badge.svg)](https://codecov.io/gh/kodemore/kink)
Dependency injection made for python

## Features

- Easy to use interface
- Extensible with custom dependency resolvers
- Automatic dependency injection
- Lightweight
- Support for async with asyncio


## Installation

```
pip install kink
```

# Usage

## Adding service to dependency injection container

Dependency container is a dict-like object, adding new service to dependency container is as 
simple as the following example:

```python
from kink import di
from os import getenv

di["db_name"] = getenv("DB_NAME")
di["db_password"] = getenv("DB_PASSWORD")
```

## Adding service factory to dependency injection container

Kink also supports on-demand service creation. In order to define such a service, lambda function
should be used: 

```python
from kink import di
from sqlite3 import connect

di["db_connection"] = lambda di: connect(di["db_name"])
```

In this scenario connection to database will not be established until service is requested.

## Requesting services fromm dependency injection container

```python
from kink import di
from sqlite3 import connect

# Setting services
di["db_name"] = "test_db.db"
di["db_connection"] = lambda di: connect(di["db_name"])


# Getting service

connection = di["db_connection"] # will return instance of sqlite3.Connection
assert connection == di["db_connection"] # True
```

## Autowiring dependencies

```python
from kink import di, inject
from sqlite3 import connect, Connection


di["db_name"] = "test_db.db"
di["db_connection"] = lambda di: connect(di["db_name"])

# Inject connection from di, connection is established once function is called.
@inject
def get_database(db_connection: Connection):
    ...


connection = get_database()
connection_with_passed_connection = get_database(connect("temp.db")) # will use passed connection
```

### Constructor injection
```python
from kink import inject, di
import MySQLdb

# Set dependencies
di["db_host"] = "localhost"
di["db_name"] = "test"
di["db_user"] = "user"
di["db_password"] = "password"
di["db_connection"] = lambda di: MySQLdb.connect(host=di["db_host"], user=di["db_user"], passwd=di["db_password"], db=di["db_name"])

@inject
class AbstractRepository:
    def __init__(self, db_connection):
        self.connection = db_connection


class UserRepository(AbstractRepository):
    ...


repository = UserRepository()
repository.connection # mysql db connection is resolved and available to use.
```

When class is annotated by `inject` annotation it will be automatically added to the container for future use (eg autowiring).


### Services aliasing

When you registering service with `@inject` decorator you can attach your own alias name, please consider the following example:

```python
from kink import inject
from typing import Protocol

class IUserRepository(Protocol):
    ...

@inject(alias=IUserRepository)
class UserRepository:
    ...


assert di[IUserRepository] == di[UserRepository] # returns true
```

For more examples check [tests](/tests) directory
