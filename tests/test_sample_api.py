import pytest
from rest_framework import status
from rest_framework.test import APIClient

from sample.models import SampleItem

ITEMS_URL = "/api/items/"


def detail_url(item_id: str) -> str:
    return f"{ITEMS_URL}{item_id}/"


@pytest.mark.django_db
class TestSampleItemAPI:
    def test_list_empty(self, api_client: APIClient) -> None:
        response = api_client.get(ITEMS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []

    def test_create_item(self, api_client: APIClient) -> None:
        payload = {"name": "New Item", "description": "A description"}
        response = api_client.post(ITEMS_URL, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Item"
        assert response.data["description"] == "A description"
        assert "id" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_retrieve_item(
        self, api_client: APIClient, sample_item: SampleItem
    ) -> None:
        response = api_client.get(detail_url(sample_item.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == sample_item.name
        assert response.data["id"] == str(sample_item.id)

    def test_update_item(
        self, api_client: APIClient, sample_item: SampleItem
    ) -> None:
        payload = {"name": "Updated Name", "description": "Updated desc"}
        response = api_client.put(
            detail_url(sample_item.id), payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        assert response.data["description"] == "Updated desc"

    def test_partial_update_item(
        self, api_client: APIClient, sample_item: SampleItem
    ) -> None:
        payload = {"name": "Patched Name"}
        response = api_client.patch(
            detail_url(sample_item.id), payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Patched Name"

    def test_delete_item(
        self, api_client: APIClient, sample_item: SampleItem
    ) -> None:
        response = api_client.delete(detail_url(sample_item.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not SampleItem.objects.filter(id=sample_item.id).exists()

    def test_create_missing_name_returns_400(self, api_client: APIClient) -> None:
        payload = {"description": "Missing name field"}
        response = api_client.post(ITEMS_URL, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_whitespace_name_returns_400(self, api_client: APIClient) -> None:
        payload = {"name": "   ", "description": "Whitespace name"}
        response = api_client.post(ITEMS_URL, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_nonexistent_returns_404(
        self, api_client: APIClient
    ) -> None:
        import uuid

        fake_id = uuid.uuid4()
        response = api_client.get(detail_url(fake_id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
