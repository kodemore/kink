
from kink import inject, di

class Repository:
   pass

@inject(alias=Repository, use_factory=True)
class PerInstanceRepository(Repository):
   pass

@inject
class Service:
   def __init__(self, repository: Repository):
      pass
   
def test_can_inject_aliased_factory_services():
   di[Service]