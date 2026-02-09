import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

CPU_URL = "/api/cpu/"


def detail_url(cpu_id: str) -> str:
    return f"{CPU_URL}{cpu_id}/"


VALID_CPU_DATA = {
    "name": "Intel Core i9-14900K",
    "cores": 24,
    "threads": 32,
    "clock_speed": "3.20",
    "boost_clock": "6.00",
    "tdp": 253,
    "socket": "LGA1700",
}


@pytest.mark.django_db
class TestCpuComponentAPI:
    """US2: CRUD operations on CPU endpoint."""

    def test_create_cpu(self, api_client: APIClient) -> None:
        response = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == VALID_CPU_DATA["name"]
        assert response.data["cores"] == VALID_CPU_DATA["cores"]
        assert response.data["threads"] == VALID_CPU_DATA["threads"]
        assert response.data["component_type"] == "cpu"
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

    def test_update_cpu_put(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        updated_data = {**VALID_CPU_DATA, "name": "AMD Ryzen 9 7950X"}
        response = api_client.put(
            detail_url(created.data["id"]), updated_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "AMD Ryzen 9 7950X"

    def test_partial_update_cpu_patch(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.patch(
            detail_url(created.data["id"]),
            {"name": "Patched CPU"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Patched CPU"

    def test_delete_cpu(self, api_client: APIClient) -> None:
        created = api_client.post(CPU_URL, VALID_CPU_DATA, format="json")
        response = api_client.delete(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(detail_url(created.data["id"])).status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCpuValidation:
    """US2: Validation rules for CPU components."""

    def test_missing_name_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_CPU_DATA.items() if k != "name"}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_missing_cores_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_CPU_DATA.items() if k != "cores"}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cores" in response.data

    def test_missing_clock_speed_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_CPU_DATA.items() if k != "clock_speed"}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "clock_speed" in response.data

    def test_threads_less_than_cores_returns_400(self, api_client: APIClient) -> None:
        data = {**VALID_CPU_DATA, "cores": 8, "threads": 4}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_boost_clock_less_than_clock_speed_returns_400(
        self, api_client: APIClient
    ) -> None:
        data = {**VALID_CPU_DATA, "clock_speed": "5.00", "boost_clock": "3.00"}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_whitespace_name_returns_400(self, api_client: APIClient) -> None:
        data = {**VALID_CPU_DATA, "name": "   "}
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_optional_fields_can_be_null(self, api_client: APIClient) -> None:
        data = {
            "name": "Minimal CPU",
            "cores": 4,
            "threads": 8,
            "clock_speed": "2.50",
        }
        response = api_client.post(CPU_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["boost_clock"] is None
        assert response.data["tdp"] is None
        assert response.data["socket"] == ""
