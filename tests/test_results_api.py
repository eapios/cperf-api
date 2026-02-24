import pytest
from rest_framework import status
from rest_framework.test import APIClient

PROFILE_URL = "/api/result-profiles/"
WORKLOAD_URL = "/api/result-workloads/"
PROFILE_WORKLOAD_URL = "/api/result-profile-workloads/"
RECORD_URL = "/api/result-records/"
INSTANCE_URL = "/api/result-instances/"


@pytest.mark.django_db
class TestResultProfileWorkload:
    """US5: Profile/workload management and unique constraint."""

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
    """US5: ResultRecord with nullable hardware FKs (SET_NULL on delete)."""

    def test_create_result_record(self, api_client: APIClient) -> None:
        response = api_client.post(RECORD_URL, {"name": "BiCS8 baseline"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["nand"] is None
        assert response.data["cpu"] is None
        assert response.data["dram"] is None

    def test_hardware_fk_set_null_on_delete(self, api_client: APIClient) -> None:
        from cpu.models import Cpu

        cpu = Cpu.objects.create(name="Test CPU", bandwidth=50.0)
        record = api_client.post(RECORD_URL, {
            "name": "Run with CPU",
            "cpu": cpu.pk,
        }, format="json")
        assert record.status_code == status.HTTP_201_CREATED
        assert record.data["cpu"] == cpu.pk

        # Delete CPU — record should remain with cpu=null
        cpu.delete()
        response = api_client.get(f"{RECORD_URL}{record.data['id']}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["cpu"] is None


@pytest.mark.django_db
class TestResultInstance:
    """US5: ResultInstance uniqueness and per-instance extended property values."""

    def _setup(self, api_client: APIClient) -> tuple:
        p = api_client.post(PROFILE_URL, {"name": "Profile"}, format="json").data
        w = api_client.post(WORKLOAD_URL, {"name": "Workload", "type": 1}, format="json").data
        pw = api_client.post(PROFILE_WORKLOAD_URL, {"profile": p["id"], "workload": w["id"]}, format="json").data
        rec = api_client.post(RECORD_URL, {"name": "Record"}, format="json").data
        return pw, rec

    def test_unique_result_instance_per_record_workload(self, api_client: APIClient) -> None:
        pw, rec = self._setup(api_client)
        data = {"profile_workload": pw["id"], "result_record": rec["id"]}
        assert api_client.post(INSTANCE_URL, data, format="json").status_code == status.HTTP_201_CREATED
        assert api_client.post(INSTANCE_URL, data, format="json").status_code == status.HTTP_400_BAD_REQUEST

    def test_result_instance_extended_properties_independent(
        self, api_client: APIClient
    ) -> None:
        from django.contrib.contenttypes.models import ContentType
        from results.models import ResultInstance
        from properties.models import ExtendedProperty, ExtendedPropertyValue

        pw, rec = self._setup(api_client)
        inst1 = api_client.post(INSTANCE_URL, {"profile_workload": pw["id"], "result_record": rec["id"]}, format="json").data

        # Create a second record + instance
        rec2 = api_client.post(RECORD_URL, {"name": "Record 2"}, format="json").data
        p2 = api_client.post(PROFILE_URL, {"name": "P2"}, format="json").data
        w2 = api_client.post(WORKLOAD_URL, {"name": "W2", "type": 2}, format="json").data
        pw2 = api_client.post(PROFILE_WORKLOAD_URL, {"profile": p2["id"], "workload": w2["id"]}, format="json").data
        inst2 = api_client.post(INSTANCE_URL, {"profile_workload": pw2["id"], "result_record": rec2["id"]}, format="json").data

        ri_ct = ContentType.objects.get_for_model(ResultInstance)
        from properties.models import ExtendedPropertySet
        eps = ExtendedPropertySet.objects.create(name="Result Props")
        prop = ExtendedProperty.objects.create(property_set=eps, name="Time")

        # Different values per instance
        ExtendedPropertyValue.objects.create(
            extended_property=prop, content_type=ri_ct, object_id=inst1["id"], value="=E1*F1"
        )
        ExtendedPropertyValue.objects.create(
            extended_property=prop, content_type=ri_ct, object_id=inst2["id"], value="=E1*F2"
        )

        r1 = api_client.get(f"{INSTANCE_URL}{inst1['id']}/?include=extended_properties")
        r2 = api_client.get(f"{INSTANCE_URL}{inst2['id']}/?include=extended_properties")
        v1 = [v["value"] for v in r1.data["extended_properties"]]
        v2 = [v["value"] for v in r2.data["extended_properties"]]
        assert "=E1*F1" in v1
        assert "=E1*F2" in v2
        assert v1 != v2
