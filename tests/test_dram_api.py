import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

DRAM_URL = "/api/dram/"


def detail_url(dram_id: str) -> str:
    return f"{DRAM_URL}{dram_id}/"


VALID_DRAM_DATA = {
    "name": "G.Skill Trident Z5 RGB",
    "capacity_gb": 32,
    "speed_mhz": 6000,
    "ddr_type": "DDR5",
    "modules": 2,
    "cas_latency": 30,
}


@pytest.mark.django_db
class TestDramComponentAPI:
    """US2: CRUD operations on DRAM endpoint."""

    def test_create_dram(self, api_client: APIClient) -> None:
        response = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == VALID_DRAM_DATA["name"]
        assert response.data["capacity_gb"] == VALID_DRAM_DATA["capacity_gb"]
        assert response.data["speed_mhz"] == VALID_DRAM_DATA["speed_mhz"]
        assert response.data["ddr_type"] == VALID_DRAM_DATA["ddr_type"]
        assert response.data["component_type"] == "dram"
        assert "id" in response.data
        assert "created_at" in response.data

    def test_list_dram(self, api_client: APIClient) -> None:
        api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.get(DRAM_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_retrieve_dram(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == VALID_DRAM_DATA["name"]

    def test_update_dram_put(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        updated_data = {**VALID_DRAM_DATA, "name": "Corsair Dominator Platinum"}
        response = api_client.put(
            detail_url(created.data["id"]), updated_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Corsair Dominator Platinum"

    def test_partial_update_dram_patch(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.patch(
            detail_url(created.data["id"]),
            {"name": "Patched DRAM"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Patched DRAM"

    def test_delete_dram(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.delete(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(detail_url(created.data["id"])).status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_nonexistent_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDramValidation:
    """US2: Validation rules for DRAM components."""

    def test_missing_name_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_DRAM_DATA.items() if k != "name"}
        response = api_client.post(DRAM_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_missing_capacity_gb_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_DRAM_DATA.items() if k != "capacity_gb"}
        response = api_client.post(DRAM_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "capacity_gb" in response.data

    def test_missing_ddr_type_returns_400(self, api_client: APIClient) -> None:
        data = {k: v for k, v in VALID_DRAM_DATA.items() if k != "ddr_type"}
        response = api_client.post(DRAM_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ddr_type" in response.data

    def test_whitespace_name_returns_400(self, api_client: APIClient) -> None:
        data = {**VALID_DRAM_DATA, "name": "   "}
        response = api_client.post(DRAM_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_optional_fields_default(self, api_client: APIClient) -> None:
        data = {
            "name": "Minimal DRAM",
            "capacity_gb": 16,
            "speed_mhz": 3200,
            "ddr_type": "DDR4",
        }
        response = api_client.post(DRAM_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["modules"] == 1
        assert response.data["cas_latency"] is None
        assert response.data["voltage"] is None
