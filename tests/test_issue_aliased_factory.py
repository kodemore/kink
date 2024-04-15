from abc import ABC
from typing import Protocol, List

from kink import inject, di


class Repository(Protocol):
    def __init__(self) -> None:
        pass


@inject(alias=Repository, use_factory=True)
class PerInstanceRepository(Repository):
    pass


@inject(alias=Repository)
class Repository1(Repository):
    pass


@inject(alias=Repository)
class Repository2(Repository):
    repo: Repository1 = di[Repository1]


@inject
class Service:
    def __init__(self, repositories: List[Repository]):
        self._repositories = repositories


def test_can_inject_aliased_factory_services():
    service: Service = di[Service]
    assert service is not None
    assert service._repositories is not None
    assert len(service._repositories) == 3
    repository: Repository = di[Repository2]
    assert repository.repo is not None
    repositories: List[Repository] = di[List[Repository]]
    assert repositories is not None
    assert len(repositories) == 3
