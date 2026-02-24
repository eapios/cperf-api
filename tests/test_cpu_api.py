import pytest
from rest_framework import status
from rest_framework.test import APIClient

CPU_URL = "/api/cpu/"


def detail_url(cpu_id: int) -> str:
    return f"{CPU_URL}{cpu_id}/"


VALID_CPU_DATA = {"name": "Intel Xeon E5-2690", "bandwidth": 51.2}


@pytest.mark.django_db
class TestCpuAPI:
    """US2: CRUD operations on CPU endpoint."""

    def test_create_cpu(self, api_client: APIClient) -> None:
        response = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == VALID_CPU_DATA["name"]
        assert response.data["bandwidth"] == VALID_CPU_DATA["bandwidth"]
        assert "id" in response.data
        assert "created_at" in response.data

    def test_list_cpu(self, api_client: APIClient) -> None:
        api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.get(CPU_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_retrieve_cpu(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == VALID_CPU_DATA["name"]

    def test_partial_update_cpu_patch_refreshes_updated_at(
        self, api_client: APIClient
    ) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.patch(
            detail_url(created.data["id"]),
            {"bandwidth": 100.0},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bandwidth"] == 100.0

    def test_delete_cpu(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.delete(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(detail_url(created.data["id"])).status_code == status.HTTP_404_NOT_FOUND

    def test_missing_name_returns_400(self, api_client: APIClient) -> None:
        response = api_client.post(CPU_URL, {"bandwidth": 51.2}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_missing_bandwidth_returns_400(self, api_client: APIClient) -> None:
        response = api_client.post(CPU_URL, {"name": "No BW"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "bandwidth" in response.data

    def test_config_set_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.data["config_set"] is None

    def test_extended_properties_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.data["extended_properties"] is None
