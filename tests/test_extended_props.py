import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from cpu.models import Cpu
from nand.models import Nand
from results.models import ResultWorkload

EXT_PROP_URL = "/api/extended-properties/"
EXT_VALUE_URL = "/api/extended-property-values/"
EXT_SET_URL = "/api/extended-property-sets/"
EXT_MEMBERSHIP_URL = "/api/extended-property-set-memberships/"


@pytest.fixture
def nand_ct(db) -> ContentType:
    return ContentType.objects.get_for_model(Nand)


@pytest.fixture
def cpu_ct(db) -> ContentType:
    return ContentType.objects.get_for_model(Cpu)


@pytest.fixture
def cpu_prop(db, cpu_ct: ContentType):
    """An entity-level ExtendedProperty bound to Cpu with default_value=65."""
    from properties.models import ExtendedProperty
    return ExtendedProperty.objects.create(content_type=cpu_ct, name="TDP", default_value=65)


@pytest.fixture
def cpu_instance(db) -> Cpu:
    return Cpu.objects.create(name="Test CPU", bandwidth=50.0)


# ---------------------------------------------------------------------------
# US1 — Default Value CRUD (T005, T006)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDefaultValueCRUD:
    """T005, T006: default_value persisted and updatable via POST/PATCH."""

    def test_post_with_default_value_persists(self, api_client: APIClient, cpu_ct: ContentType) -> None:
        # T005
        data = {"content_type": cpu_ct.pk, "name": "Power", "is_formula": False, "default_value": 65}
        resp = api_client.post(EXT_PROP_URL, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["default_value"] == 65

    def test_get_returns_default_value(self, api_client: APIClient, cpu_prop) -> None:
        # T005 read-back
        resp = api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["default_value"] == 65

    def test_patch_updates_default_value(self, api_client: APIClient, cpu_prop) -> None:
        # T006
        resp = api_client.patch(f"{EXT_PROP_URL}{cpu_prop.pk}/", {"default_value": 0}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["default_value"] == 0
        assert api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/").data["default_value"] == 0


# ---------------------------------------------------------------------------
# US1 — Resolve endpoint (T007, T008, T009, T010)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestResolveEndpoint:
    """T007–T010: resolve action returns effective value."""

    def test_resolve_returns_default_when_no_per_instance_record(
        self, api_client: APIClient, cpu_prop, cpu_ct: ContentType
    ) -> None:
        url = f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=cpu&model_name=cpu&object_id=99999"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] == 65
        assert resp.data["is_default"] is True
        assert resp.data["property_id"] == cpu_prop.pk

    def test_resolve_returns_null_when_default_value_is_null(
        self, api_client: APIClient, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty
        prop = ExtendedProperty.objects.create(content_type=cpu_ct, name="Nullable Prop", default_value=None)
        url = f"{EXT_PROP_URL}{prop.pk}/resolve/?model=cpu&model_name=cpu&object_id=99999"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] is None
        assert resp.data["is_default"] is True

    def test_resolve_returns_400_when_model_missing(self, api_client: APIClient, cpu_prop) -> None:
        resp = api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?object_id=1")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_resolve_returns_400_when_object_id_missing(self, api_client: APIClient, cpu_prop) -> None:
        resp = api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=cpu&model_name=cpu")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_resolve_returns_404_for_unknown_model(self, api_client: APIClient, cpu_prop) -> None:
        resp = api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=nonexistent&object_id=1")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_resolve_returns_400_for_ambiguous_app_label(
        self, api_client: APIClient, cpu_prop
    ) -> None:
        resp = api_client.get(f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=results&object_id=1")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "model_name" in resp.data["detail"]


# ---------------------------------------------------------------------------
# US2 — Per-instance override precedence (T011, T012, T013)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPerInstanceOverride:
    """T011–T013: per-instance value overrides default_value."""

    def test_per_instance_value_overrides_default(
        self, api_client: APIClient, cpu_prop, cpu_instance: Cpu, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedPropertyValue
        ExtendedPropertyValue.objects.create(
            extended_property=cpu_prop, content_type=cpu_ct,
            object_id=cpu_instance.pk, value=125,
        )
        url = f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=cpu&model_name=cpu&object_id={cpu_instance.pk}"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] == 125
        assert resp.data["is_default"] is False

    def test_instance_without_record_gets_default(
        self, api_client: APIClient, cpu_prop, cpu_instance: Cpu, cpu_ct: ContentType
    ) -> None:
        url = f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=cpu&model_name=cpu&object_id=99998"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] == 65
        assert resp.data["is_default"] is True

    def test_updating_default_does_not_affect_per_instance_value(
        self, api_client: APIClient, cpu_prop, cpu_instance: Cpu, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedPropertyValue
        ExtendedPropertyValue.objects.create(
            extended_property=cpu_prop, content_type=cpu_ct,
            object_id=cpu_instance.pk, value=125,
        )
        api_client.patch(f"{EXT_PROP_URL}{cpu_prop.pk}/", {"default_value": 999}, format="json")
        url = f"{EXT_PROP_URL}{cpu_prop.pk}/resolve/?model=cpu&model_name=cpu&object_id={cpu_instance.pk}"
        resp = api_client.get(url)
        assert resp.data["value"] == 125
        assert resp.data["is_default"] is False


# ---------------------------------------------------------------------------
# US3 — Formula properties support default_value (T014, T015)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestFormulaDefaultValue:
    """T014–T015: formula properties accept and return default_value as-is."""

    def test_formula_property_returns_formula_string_as_default(
        self, api_client: APIClient, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty
        prop = ExtendedProperty.objects.create(
            content_type=cpu_ct, name="Formula Prop", is_formula=True, default_value="A / B"
        )
        url = f"{EXT_PROP_URL}{prop.pk}/resolve/?model=cpu&model_name=cpu&object_id=99999"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] == "A / B"
        assert resp.data["is_default"] is True

    def test_formula_property_null_default_returns_null(
        self, api_client: APIClient, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty
        prop = ExtendedProperty.objects.create(
            content_type=cpu_ct, name="Formula Null Prop", is_formula=True, default_value=None
        )
        url = f"{EXT_PROP_URL}{prop.pk}/resolve/?model=cpu&model_name=cpu&object_id=99999"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] is None
        assert resp.data["is_default"] is True


# ---------------------------------------------------------------------------
# Result-level property resolve — now uses content_type binding
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestResultLevelPropertyResolve:
    """Result-level ExtendedProperty uses content_type (ResultWorkload) binding."""

    def test_result_level_property_resolve_returns_default(self, api_client: APIClient) -> None:
        from properties.models import ExtendedProperty
        workload_ct = ContentType.objects.get_for_model(ResultWorkload)
        prop = ExtendedProperty.objects.create(
            content_type=workload_ct, name="Result Default Prop", default_value="result-default"
        )
        workload = ResultWorkload.objects.create(name="Host Write", type=1)
        url = (
            f"{EXT_PROP_URL}{prop.pk}/resolve/"
            f"?model=results&model_name=resultworkload&object_id={workload.pk}"
        )
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["value"] == "result-default"
        assert resp.data["is_default"] is True


# ---------------------------------------------------------------------------
# ExtendedProperty binding — content_type is now always required
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestExtendedPropertyBinding:
    """content_type is required; property_set field no longer exists."""

    def test_entity_level_property_created(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        data = {"content_type": nand_ct.pk, "name": "J per PU"}
        response = api_client.post(EXT_PROP_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_missing_content_type_rejected(self, api_client: APIClient) -> None:
        data = {"name": "No Content Type"}
        response = api_client.post(EXT_PROP_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_null_content_type_rejected(self, api_client: APIClient) -> None:
        data = {"content_type": None, "name": "Null Content Type"}
        response = api_client.post(EXT_PROP_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_property_set_field_not_in_response(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        resp = api_client.post(EXT_PROP_URL, {"content_type": nand_ct.pk, "name": "NoSet"}, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert "property_set" not in resp.data


# ---------------------------------------------------------------------------
# ExtendedPropertySetMembership — one property can belong to multiple sets
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestExtendedPropertySetMembership:
    """A single ExtendedProperty can belong to multiple ExtendedPropertySets."""

    def test_property_in_two_sets(self, api_client: APIClient, cpu_ct: ContentType) -> None:
        from properties.models import ExtendedProperty, ExtendedPropertySet
        set_a = ExtendedPropertySet.objects.create(name="Set A")
        set_b = ExtendedPropertySet.objects.create(name="Set B")
        prop = ExtendedProperty.objects.create(content_type=cpu_ct, name="SharedProp")

        r1 = api_client.post(EXT_MEMBERSHIP_URL, {
            "property_set_id": set_a.pk, "extended_property_id": prop.pk, "index": 0,
        }, format="json")
        r2 = api_client.post(EXT_MEMBERSHIP_URL, {
            "property_set_id": set_b.pk, "extended_property_id": prop.pk, "index": 0,
        }, format="json")
        assert r1.status_code == status.HTTP_201_CREATED
        assert r2.status_code == status.HTTP_201_CREATED

        resp_a = api_client.get(f"{EXT_SET_URL}{set_a.pk}/")
        resp_b = api_client.get(f"{EXT_SET_URL}{set_b.pk}/")
        prop_ids_a = [item["extended_property"]["id"] for item in resp_a.data["items"]]
        prop_ids_b = [item["extended_property"]["id"] for item in resp_b.data["items"]]
        assert prop.pk in prop_ids_a
        assert prop.pk in prop_ids_b

    def test_duplicate_membership_rejected(self, api_client: APIClient, cpu_ct: ContentType) -> None:
        from properties.models import ExtendedProperty, ExtendedPropertySet
        eps = ExtendedPropertySet.objects.create(name="Dup Set")
        prop = ExtendedProperty.objects.create(content_type=cpu_ct, name="DupProp")
        data = {"property_set_id": eps.pk, "extended_property_id": prop.pk, "index": 0}
        assert api_client.post(EXT_MEMBERSHIP_URL, data, format="json").status_code == status.HTTP_201_CREATED
        assert api_client.post(EXT_MEMBERSHIP_URL, data, format="json").status_code == status.HTTP_400_BAD_REQUEST

    def test_set_filter_returns_only_matching_properties(
        self, api_client: APIClient, cpu_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty, ExtendedPropertySet
        eps = ExtendedPropertySet.objects.create(name="Filter Set")
        p1 = ExtendedProperty.objects.create(content_type=cpu_ct, name="InSet")
        p2 = ExtendedProperty.objects.create(content_type=cpu_ct, name="NotInSet")
        api_client.post(EXT_MEMBERSHIP_URL, {
            "property_set_id": eps.pk, "extended_property_id": p1.pk, "index": 0,
        }, format="json")

        resp = api_client.get(f"{EXT_PROP_URL}?set={eps.pk}")
        ids = [p["id"] for p in resp.data["results"]]
        assert p1.pk in ids
        assert p2.pk not in ids

    def test_delete_membership(self, api_client: APIClient, cpu_ct: ContentType) -> None:
        from properties.models import ExtendedProperty, ExtendedPropertySet
        eps = ExtendedPropertySet.objects.create(name="Del Set")
        prop = ExtendedProperty.objects.create(content_type=cpu_ct, name="DelProp")
        created = api_client.post(EXT_MEMBERSHIP_URL, {
            "property_set_id": eps.pk, "extended_property_id": prop.pk, "index": 0,
        }, format="json").data
        resp = api_client.delete(f"{EXT_MEMBERSHIP_URL}{created['id']}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------------
# ExtendedPropertyValueScoping — unchanged behaviour
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestExtendedPropertyValueScoping:
    """Per-instance values are scoped to the correct instance."""

    def _make_nand(self) -> Nand:
        return Nand.objects.create(**{
            "name": f"BiCS-{Nand.objects.count()}",
            "capacity_per_die": 1099511627776,
            "plane_per_die": 4,
            "block_per_plane": 2048,
            "d1_d2_ratio": 0.5,
            "page_per_block": 256,
            "slc_page_per_block": 64,
            "node_per_page": 16,
            "finger_per_wl": 2,
            "tlc_qlc_pe": 3000,
            "static_slc_pe": 100000,
            "table_slc_pe": 60000,
            "bad_block_ratio": 0.02,
            "max_data_raid_frame": 4,
            "max_slc_wc_raid_frame": 2,
            "max_table_raid_frame": 2,
            "data_die_raid": 16,
            "table_die_raid": 4,
            "l2p_unit": 4096,
            "mapping_table_size": 536870912,
            "p2l_entry": 512,
            "with_p2l": 1,
            "p2l_bitmap": 256,
            "l2p_ecc_data": 8,
            "l2p_ecc_spare": 2,
            "reserved_lca_number": 256,
            "power_cycle_count": 1000,
            "default_rebuild_time": 86400,
            "drive_log_region_size": 1048576,
            "drive_log_min_op": 0.07,
            "using_slc_write_cache": True,
            "using_pmd": False,
            "min_mapping_op_with_pmd": 0.0,
            "data_open": 2,
            "data_open_with_slc_wc": 4,
            "data_gc_damper_central": 1.0,
            "min_pfail_vb": 10,
            "small_table_vb": 5,
            "pfail_max_plane_count": 2,
            "bol_block_number": 100,
            "extra_table_life_for_align_spec": 1.1,
            "journal_insert_time": 1000,
            "journal_entry_size": 64,
            "journal_program_unit": 4,
        })

    def test_per_instance_values_scoped(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty

        nand1 = self._make_nand()
        nand2 = self._make_nand()
        prop = ExtendedProperty.objects.create(content_type=nand_ct, name="J per PU")

        api_client.post(EXT_VALUE_URL, {
            "extended_property": prop.pk,
            "content_type": nand_ct.pk,
            "object_id": nand1.pk,
            "value": "=A1*B1",
        }, format="json")
        api_client.post(EXT_VALUE_URL, {
            "extended_property": prop.pk,
            "content_type": nand_ct.pk,
            "object_id": nand2.pk,
            "value": "=A1*B2",
        }, format="json")

        r1 = api_client.get(f"/api/nand/{nand1.pk}/?include=extended_properties")
        r2 = api_client.get(f"/api/nand/{nand2.pk}/?include=extended_properties")
        values1 = [v["value"] for v in r1.data["extended_properties"]]
        values2 = [v["value"] for v in r2.data["extended_properties"]]
        assert "=A1*B1" in values1
        assert "=A1*B2" in values2
        assert values1 != values2

    def test_unique_value_per_prop_per_instance(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty

        nand = self._make_nand()
        prop = ExtendedProperty.objects.create(content_type=nand_ct, name="Unique Test")
        data = {
            "extended_property": prop.pk,
            "content_type": nand_ct.pk,
            "object_id": nand.pk,
            "value": "42",
        }
        assert api_client.post(EXT_VALUE_URL, data, format="json").status_code == status.HTTP_201_CREATED
        assert api_client.post(EXT_VALUE_URL, data, format="json").status_code == status.HTTP_400_BAD_REQUEST

    def test_extended_properties_included_when_requested(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import ExtendedProperty

        nand = self._make_nand()
        prop = ExtendedProperty.objects.create(content_type=nand_ct, name="My Prop")
        api_client.post(EXT_VALUE_URL, {
            "extended_property": prop.pk,
            "content_type": nand_ct.pk,
            "object_id": nand.pk,
            "value": 99,
        }, format="json")

        response = api_client.get(f"/api/nand/{nand.pk}/?include=extended_properties")
        assert response.data["extended_properties"] is not None
        assert len(response.data["extended_properties"]) == 1
        assert response.data["extended_properties"][0]["value"] == 99
