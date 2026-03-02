import pytest
from rest_framework import status
from rest_framework.test import APIClient

PROFILE_URL = "/api/result-profiles/"
WORKLOAD_URL = "/api/result-workloads/"
PROFILE_WORKLOAD_URL = "/api/result-profile-workloads/"
RECORD_URL = "/api/result-records/"


@pytest.mark.django_db
class TestResultProfileWorkload:
    """Profile/workload management and unique constraint."""

    def test_create_profile_and_workload(self, api_client: APIClient) -> None:
        p = api_client.post(PROFILE_URL, {"name": "AIPR Upper Bound"}, format="json")
        w = api_client.post(WORKLOAD_URL, {"name": "GC Read", "type": 1}, format="json")
        assert p.status_code == status.HTTP_201_CREATED
        assert w.status_code == status.HTTP_201_CREATED

    def test_unique_workload_per_profile(self, api_client: APIClient) -> None:
        p = api_client.post(PROFILE_URL, {"name": "Profile A"}, format="json").data
        w = api_client.post(WORKLOAD_URL, {"name": "Host Write", "type": 2}, format="json").data
        link_data = {"profile": p["id"], "workload": w["id"]}
        assert api_client.post(PROFILE_WORKLOAD_URL, link_data, format="json").status_code == status.HTTP_201_CREATED
        assert api_client.post(PROFILE_WORKLOAD_URL, link_data, format="json").status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestResultRecord:
    """ResultRecord uses a data JSONField; no hardware FK fields."""

    def test_create_result_record_with_data(self, api_client: APIClient) -> None:
        payload = {"name": "run-001", "data": {"nand": {"name": "BiCS8"}, "cpu": {"name": "A100"}}}
        response = api_client.post(RECORD_URL, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"] == payload["data"]

    def test_create_result_record_without_data(self, api_client: APIClient) -> None:
        response = api_client.post(RECORD_URL, {"name": "empty-run"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"] is None

    def test_result_record_has_no_hardware_fk_fields(self, api_client: APIClient) -> None:
        response = api_client.post(RECORD_URL, {"name": "check-fields"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        for fk_field in ("nand", "nand_instance", "nand_perf", "cpu", "dram"):
            assert fk_field not in response.data

    def test_get_result_record_returns_data_field(self, api_client: APIClient) -> None:
        payload = {"name": "get-test", "data": {"key": "value"}}
        created = api_client.post(RECORD_URL, payload, format="json").data
        response = api_client.get(f"{RECORD_URL}{created['id']}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == {"key": "value"}

    def test_delete_result_record(self, api_client: APIClient) -> None:
        created = api_client.post(RECORD_URL, {"name": "to-delete"}, format="json").data
        response = api_client.delete(f"{RECORD_URL}{created['id']}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(f"{RECORD_URL}{created['id']}/").status_code == status.HTTP_404_NOT_FOUND
