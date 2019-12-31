from .conainer_error import ContainerError


class ServiceError(ContainerError, KeyError):
    pass
