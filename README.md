# Kink ![PyPI](https://img.shields.io/pypi/v/kink) ![Linting and Tests](https://github.com/kodemore/kink/workflows/Linting%20and%20Tests/badge.svg?branch=master) [![codecov](https://codecov.io/gh/kodemore/kink/branch/master/graph/badge.svg)](https://codecov.io/gh/kodemore/kink) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
Dependency injection container made for python

## Features

- Easy to use interface
- Extensible with custom dependency resolvers
- Automatic dependency injection (Autowiring)
- Lightweight
- Support for async with asyncio


## Installation

### Pip

```shell
pip install kink
```

### Poetry
If you don't know poetry, I highly recommend visiting their [webpage](https://python-poetry.org)

```shell
poetry add kink
```

# Why using dependency injection in python?

## Short story 

Because python is a multi paradigm language and this should encourage 
you to use best OOP practices improving your workflow and your code and have more time
for your hobbies and families instead monkey-patching entire world.

## Long story

Dependency happens when one component (component might be a class, or a function) `A` uses other component 
`B`. We say than that `A` depends on `B`.

Instead hardcoding dependency inside your components and making your code tightly coupled
you are loosing it by providing(injecting) required behaviour either by subclassing or
plugging additional code. This is called `Inversion of Control` which keeps your code
oriented around behaviour rather than control. There are many benefits coming out of it:
- increased modularity
- better extensibility and flexibility
- it helps you understand higher concepts like event driven programming

This is where dependency injection comes in place. Dependency injection is a specific
style of inversion of control, which generally says instead hardcoding dependency pass
dependant object as a parameter to a method rather than having method creating it itself.
( who would thought it is so easy :)? ). It can go even further than that; when you pass
a dependency don't rely on a particular implementation rely on an abstraction (`Dependency Inversion Principle`).

So you might ask why do I need it? Here is couple reasons:

### Relying on the global state is evil

Coding is hard enough ( business requirements are changing all the time, deadlines are
shortening, clients wants more, there are so many unknowns you have to figure out), 
relying on unpredictable state makes it even harder:
- it might introduce potential bugs
- makes code harder to maintain
- concurrency becomes harder to achieve
- balancing mokey-patching well is a hard task

### Great, but now I have additional work I have to manage now all my dependencies write more code and deadlines are coming even closer!

True, that is why you should pick up Dependency Injection Container to do all this work 
for you. Kink gives you one decorator and simple `dict-like` object to bootstrap and manipulate
your container.
No need for manual work and manual dependency management. Give it a try and you will love it!

# Usage

To fully utilise the potential of kink it is recommended to bootstrap your initial dependencies
(config values, or instances of classes that are standalone, requires no other dependencies than themselves).
Some people prefer to keep it in `__init__.py` in the top module of your application, other
create separate `bootstra.py` file for this purpose. Once all is setup the only step left 
is to decorate your classes/functions with `@inject` decorator.

## Bootstrapping/Adding services manually

### Adding *service* to di container

Dependency container is a dict-like object, adding new service to dependency container is as 
simple as the following example:

```python
from kink import di
from os import getenv

di["db_name"] = getenv("DB_NAME")
di["db_password"] = getenv("DB_PASSWORD")
```

### Adding *on-demand service* to dependency injection container

Kink also supports on-demand service creation. In order to define such a service, 
lambda function should be used: 

```python
from kink import di
from sqlite3 import connect

di["db_connection"] = lambda di: connect(di["db_name"])
```

In this scenario connection to database will not be established until service is requested.

### Adding factorised services to dependency injection

Factorised services are services that are instantiated every time they are requested.

```python
from kink import di
from sqlite3 import connect

di.factories["db_connection"] = lambda di: connect(di["db_name"])

connection_1 = di["db_connection"]
connection_2 = di["db_connection"]

connection_1 != connection_2
```

In the above example we defined factorised service `db_connection`, and below by accessing the service from di we created
two separate connection to database.


## Requesting services from dependency injection container

To access given service just reference it inside `di` like you would do this with
a normal dictionary, full example below:

```python
from kink import di
from sqlite3 import connect

# Bootstrapping
di["db_name"] = "test_db.db"
di["db_connection"] = lambda di: connect(di["db_name"])


# Getting a service
connection = di["db_connection"] # will return instance of sqlite3.Connection
assert connection == di["db_connection"] # True
```


## Autowiring dependencies

Autowiring is the ability of the container to automatically create and inject dependencies.
It detects dependencies of the component tries to search for references in the container
and if all references are present an instance of requested service is returned.

Autowiring system in kink works in two ways:
- matching argument's names
- matching argument's type annotation

### How dependencies are prioritised by autowiring mechanism

Autowiring mechanism priorities dependencies automatically, so when multiple
matches are found for the service this is how it works;
Firstly passed arguments are prioritied - if you pass arguments manually to the service
they will take precendence over anything else. Next argument's names are taken into
consideration and last but not least argument's type annotations.

### Matching argument's names

If you don't like type annotations or would like to take advantage of autowiring's 
precedence mechanism use this style.

This is a very simple mechanism we have already seen in previous examples. 
Autowiring system checks function argument's names and tries to search for 
services with the same names inside the container. 

### Matching argument's type annotations

If you are like me and like type annotations and use static analysis tools this is
a preferred way working with DI container. 

In this scenario names are ignored instead argument's type annotations are inspected
and looked up inside di container. This requires aliases when bootstrapping 
your services in DI container or simply adding them to container in the way that
its type is the key by which service is accessed. Please consider the following example:

```python
from kink import di, inject
from sqlite3 import connect, Connection


di["db_name"] = "test_db.db"
di[Connection] = lambda di: connect(di["db_name"])  # sqlite connection can be accessed by its type

@inject # Constructor injection will happen here
class UserRepository:
  def __init__(self, db: Connection): # `db` argument will be resolved because `Connection` instance is present in the container. 
    self.db = db

repo = di[UserRepository]
assert repo.db == di[Connection] # True
```

## Constructor injection
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


## Services aliasing

When you register a service with `@inject` decorator you can attach your own alias name, please consider the following example:

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

### Retrieving all instances with the same alias
Aliases in `kink` do not have to be unique, but by default when autowiring mechnism is called the service that
was registered first within given alias will be returned. If for some reason you would like to retrieve all
services that alias to the same name (eg implementing strategy pattern), `kink` provides a useful functionality
for doing so. Please consider the following example:

```python
from kink import inject
from typing import Protocol, List

class IUserRepository(Protocol):
    ...

@inject(alias=IUserRepository)
class MongoUserRepository:
    ...

@inject(alias=IUserRepository)
class MySQLUserRepository:
    ...

@inject()
class UserRepository:
    def __init__(self, repos: List[IUserRepository]) -> None: # all services that alias to IUserRepository will be passed here
        self._repos = repos
        
    def store_to_mysql(self, user: ...):
        self._repos[1].store(user)
    
    def store_to_mongo(self, user: ...):
        self._repos[0].store(user)
```

## Clearing di cache

Sometimes it might come handy to clear cached services in di container. Simple way of 
doing this is calling `di.clear_cache()` method like in the following example.

```python
from kink import inject, di

... # set and accesss your services

di.clear_cache() # this will clear cache of all services inside di container that are not factorised services
```

# Articles on Kink

[https://www.netguru.com/codestories/dependency-injection-with-python-make-it-easy](https://www.netguru.com/codestories/dependency-injection-with-python-make-it-easy)
