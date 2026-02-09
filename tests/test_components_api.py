import pytest
from rest_framework import status
from rest_framework.test import APIClient

from components.models import Component

COMPONENTS_URL = "/api/components/"
CPU_URL = "/api/cpu/"
DRAM_URL = "/api/dram/"


def detail_url(component_id: str) -> str:
    return f"{COMPONENTS_URL}{component_id}/"


@pytest.mark.django_db
class TestComponentListAPI:
    """US1: Query components across all types."""

    def test_list_empty(self, api_client: APIClient) -> None:
        response = api_client.get(COMPONENTS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []

    def test_list_returns_paginated_results(
        self, api_client: APIClient, cpu_component: Component, dram_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_filter_by_component_type(
        self, api_client: APIClient, cpu_component: Component, dram_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL, {"component_type": "cpu"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["component_type"] == "cpu"

    def test_filter_by_unknown_type_returns_empty(
        self, api_client: APIClient, cpu_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL, {"component_type": "gpu"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_search_by_name(
        self, api_client: APIClient, cpu_component: Component, dram_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL, {"search": "Intel"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert "Intel" in response.data["results"][0]["name"]

    def test_ordering_by_name(
        self, api_client: APIClient, cpu_component: Component, dram_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL, {"ordering": "name"})
        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert names == sorted(names)

    def test_ordering_by_created_at_desc(
        self, api_client: APIClient, cpu_component: Component, dram_component: Component
    ) -> None:
        response = api_client.get(COMPONENTS_URL, {"ordering": "-created_at"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


@pytest.mark.django_db
class TestComponentDetailAPI:
    """US1: Retrieve a single component by UUID."""

    def test_retrieve_by_uuid(
        self, api_client: APIClient, cpu_component: Component
    ) -> None:
        response = api_client.get(detail_url(cpu_component.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(cpu_component.id)
        assert response.data["name"] == cpu_component.name
        assert response.data["component_type"] == cpu_component.component_type

    def test_retrieve_nonexistent_returns_404(self, api_client: APIClient) -> None:
        import uuid

        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_general_endpoint_is_read_only(
        self, api_client: APIClient, cpu_component: Component
    ) -> None:
        """POST/PUT/PATCH/DELETE should not be allowed on the general endpoint."""
        payload = {"name": "New Component", "component_type": "cpu"}
        assert (
            api_client.post(COMPONENTS_URL, payload, format="json").status_code
            == status.HTTP_405_METHOD_NOT_ALLOWED
        )
        assert (
            api_client.put(
                detail_url(cpu_component.id), payload, format="json"
            ).status_code
            == status.HTTP_405_METHOD_NOT_ALLOWED
        )
        assert (
            api_client.patch(
                detail_url(cpu_component.id), payload, format="json"
            ).status_code
            == status.HTTP_405_METHOD_NOT_ALLOWED
        )
        assert (
            api_client.delete(detail_url(cpu_component.id)).status_code
            == status.HTTP_405_METHOD_NOT_ALLOWED
        )


@pytest.mark.django_db
class TestCrossEndpointVisibility:
    """US2: Components created via type endpoints appear in general endpoint."""

    def test_cpu_created_via_type_endpoint_appears_in_general(
        self, api_client: APIClient
    ) -> None:
        cpu_data = {
            "name": "Intel Core i9-14900K",
            "cores": 24,
            "threads": 32,
            "clock_speed": "3.20",
        }
        created = api_client.post(CPU_URL, cpu_data, format="json")
        assert created.status_code == status.HTTP_201_CREATED

        response = api_client.get(COMPONENTS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == created.data["id"]
        assert response.data["results"][0]["component_type"] == "cpu"

    def test_dram_created_via_type_endpoint_appears_in_general(
        self, api_client: APIClient
    ) -> None:
        dram_data = {
            "name": "G.Skill Trident Z5",
            "capacity_gb": 32,
            "speed_mhz": 6000,
            "ddr_type": "DDR5",
        }
        created = api_client.post(DRAM_URL, dram_data, format="json")
        assert created.status_code == status.HTTP_201_CREATED

        response = api_client.get(COMPONENTS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["component_type"] == "dram"

    def test_delete_via_type_endpoint_removes_from_general(
        self, api_client: APIClient
    ) -> None:
        cpu_data = {
            "name": "Deletable CPU",
            "cores": 4,
            "threads": 8,
            "clock_speed": "2.00",
        }
        created = api_client.post(CPU_URL, cpu_data, format="json")
        assert created.status_code == status.HTTP_201_CREATED

        # Verify it appears in general endpoint
        response = api_client.get(COMPONENTS_URL)
        assert response.data["count"] == 1

        # Delete via type endpoint
        delete_response = api_client.delete(f"{CPU_URL}{created.data['id']}/")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify removed from general endpoint
        response = api_client.get(COMPONENTS_URL)
        assert response.data["count"] == 0
