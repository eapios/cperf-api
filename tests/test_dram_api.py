import pytest
from rest_framework import status
from rest_framework.test import APIClient

DRAM_URL = "/api/dram/"


def detail_url(dram_id: int) -> str:
    return f"{DRAM_URL}{dram_id}/"


VALID_DRAM_DATA = {"name": "DDR5-4800 16GB", "bandwidth": 76.8, "channel": 2, "transfer_rate": 4800.0}


@pytest.mark.django_db
class TestDramAPI:
    """US2: CRUD operations on DRAM endpoint."""

    def test_create_dram(self, api_client: APIClient) -> None:
        response = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == VALID_DRAM_DATA["name"]
        assert response.data["bandwidth"] == VALID_DRAM_DATA["bandwidth"]
        assert response.data["channel"] == VALID_DRAM_DATA["channel"]
        assert response.data["transfer_rate"] == VALID_DRAM_DATA["transfer_rate"]
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

    def test_partial_update_patch(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.patch(
            detail_url(created.data["id"]), {"bandwidth": 99.9}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bandwidth"] == 99.9

    def test_delete_dram(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.delete(detail_url(created.data["id"]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(detail_url(created.data["id"])).status_code == status.HTTP_404_NOT_FOUND

    def test_missing_required_fields_returns_400(self, api_client: APIClient) -> None:
        for field in ("name", "bandwidth", "channel", "transfer_rate"):
            data = {k: v for k, v in VALID_DRAM_DATA.items() if k != field}
            response = api_client.post(DRAM_URL, data, format="json")
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400 for missing {field}"

    def test_config_set_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.data["config_set"] is None

    def test_extended_properties_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(DRAM_URL, VALID_DRAM_DATA, format="json")
        response = api_client.get(detail_url(created.data["id"]))
        assert response.data["extended_properties"] is None
