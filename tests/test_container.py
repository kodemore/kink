from typing import List

from kink import Container
import time


def test_instantiate_simple_container():
    container = Container()
    assert isinstance(container, Container)


def test_set_value():
    container = Container()
    container["item"] = "value"

    assert "item" in container


def test_get_value():
    container = Container()
    container["item"] = "value"

    assert container["item"] == "value"


def test_get_factored_service():
    container = Container()
    container["parent_item"] = "value"
    container["item"] = lambda di: di["parent_item"]

    assert container["item"] == "value"


def test_get_callable_service():
    def test_1():
        return 1

    container = Container()
    container["test_1"] = test_1
    container["test_2"] = lambda di: 12

    assert container["test_1"]() == 1
    assert container["test_2"] == 12


def test_set_class_as_service() -> None:
    class A:
        ...

    container = Container()
    container[A] = A()

    assert A in container
    assert container[A] == container[A]
    assert isinstance(container[A], A)


def test_set_factored_service() -> None:
    class A:
        ...

    container = Container()
    container.factories[A] = lambda di: A()

    assert A in container
    assert container[A] != container[A]
    assert isinstance(container[A], A)


def test_clear_cache() -> None:
    container = Container()
    container["time"] = lambda di: time.time()

    time_a = container["time"]
    time_b = container["time"]

    assert time_a == time_b

    container.clear_cache()
    time_c = container["time"]
    time_d = container["time"]

    assert time_c != time_a
    assert time_c == time_d


def test_add_alias() -> None:
    # given
    class A:
        ...

    class B:
        ...

    class T:
        ...

    class T2:
        ...

    container = Container()

    # when
    container[A] = A()
    container[B] = B()
    container.add_alias(T, A)
    container.add_alias(T2, A)
    container.add_alias(T2, B)
    container.add_alias(T, B)

    # then
    assert container[T] == container[A]
    assert container[T2] == container[A]


def test_retrieve_all_aliased_items() -> None:
    # given
    class A:
        ...

    class B:
        ...

    class C:
        ...

    class T:
        ...

    container = Container()

    # when
    container[A] = A()
    container[B] = B()
    container[C] = C()
    container.add_alias(T, A)
    container.add_alias(T, B)
    container.add_alias(T, C)

    all_items = container[List[T]]
    all_items_cached = container[List[T]]

    # then
    assert len(all_items) == 3
    assert all_items[0] == container[A]
    assert all_items[1] == container[B]
    assert all_items[2] == container[C]
    assert id(all_items) == id(all_items_cached)
    assert List[T] in container


def test_delete_service():
    container = Container()
    container["test_service"] = "test_value"
    
    assert "test_service" in container
    assert container["test_service"] == "test_value"
    
    del container["test_service"]
    
    assert "test_service" not in container


def test_delete_lambda_service():
    container = Container()
    container["parent"] = "parent_value"
    container["child"] = lambda di: di["parent"] + "_processed"
    
    # Access to ensure it's memoized
    assert container["child"] == "parent_value_processed"
    
    del container["child"]
    
    assert "child" not in container
    assert "parent" in container  # Parent should remain


def test_delete_factory_service():
    container = Container()
    container.factories["factory_service"] = lambda di: {"id": time.time()}
    
    assert "factory_service" in container
    
    del container["factory_service"]
    
    assert "factory_service" not in container


def test_delete_service_with_alias():
    container = Container()
    
    class TestService:
        pass
    
    container[TestService] = TestService()
    container.add_alias("service_alias", TestService)
    
    assert "service_alias" in container
    assert TestService in container
    
    # Delete the actual service
    del container[TestService]
    
    assert TestService not in container
    assert "service_alias" not in container  # Alias should be removed too


def test_delete_alias_with_multiple_targets():
    container = Container()
    
    class ServiceA:
        pass
    
    class ServiceB:
        pass
    
    container[ServiceA] = ServiceA()
    container[ServiceB] = ServiceB()
    container.add_alias("multi_alias", ServiceA)
    container.add_alias("multi_alias", ServiceB)
    
    assert "multi_alias" in container
    
    # Delete one service
    del container[ServiceA]
    
    assert ServiceA not in container
    assert ServiceB in container
    assert "multi_alias" in container  # Alias should still exist with ServiceB


def test_delete_all_aliased_services():
    container = Container()
    
    class ServiceA:
        pass
    
    class ServiceB:
        pass
    
    container[ServiceA] = ServiceA()
    container[ServiceB] = ServiceB()
    container.add_alias("multi_alias", ServiceA)
    container.add_alias("multi_alias", ServiceB)
    
    # Delete both services
    del container[ServiceA]
    del container[ServiceB]
    
    assert ServiceA not in container
    assert ServiceB not in container
    assert "multi_alias" not in container  # Alias should be removed when no targets remain


def test_delete_service_clears_memoized_cache():
    container = Container()
    container["expensive_service"] = lambda di: "computed_value"
    
    # Access to memoize
    value = container["expensive_service"]
    assert value == "computed_value"
    
    del container["expensive_service"]
    
    # Re-add the service with different lambda
    container["expensive_service"] = lambda di: "new_computed_value"
    assert container["expensive_service"] == "new_computed_value"


def test_delete_service_clears_list_cache():
    from typing import Protocol
    
    class IService(Protocol):
        pass
    
    class ServiceImpl:
        pass
    
    container = Container()
    container[ServiceImpl] = ServiceImpl()
    container.add_alias(IService, ServiceImpl)
    
    # Access List to memoize
    services_list = container[List[IService]]
    assert len(services_list) == 1
    
    del container[ServiceImpl]
    
    # List cache should be cleared, so accessing it should fail
    assert List[IService] not in container


def test_delete_nonexistent_service_raises_keyerror():
    container = Container()
    
    try:
        del container["nonexistent_service"]
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "nonexistent_service" in str(e)


def test_delete_service_multiple_times_raises_keyerror():
    container = Container()
    container["test_service"] = "test_value"
    
    del container["test_service"]
    
    try:
        del container["test_service"]
        assert False, "Should have raised KeyError"
    except KeyError:
        pass  # Expected


def test_delete_service_from_both_services_and_factories():
    container = Container()
    
    # This shouldn't happen in normal usage, but let's test edge case
    container._services["edge_case"] = "service_value"
    container._factories["edge_case"] = lambda di: "factory_value"
    
    assert "edge_case" in container
    
    del container["edge_case"]
    
    assert "edge_case" not in container
