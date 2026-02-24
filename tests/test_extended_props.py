import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from cpu.models import Cpu
from nand.models import Nand

EXT_PROP_URL = "/api/extended-properties/"
EXT_VALUE_URL = "/api/extended-property-values/"


@pytest.fixture
def nand_ct(db) -> ContentType:
    return ContentType.objects.get_for_model(Nand)


@pytest.fixture
def cpu_ct(db) -> ContentType:
    return ContentType.objects.get_for_model(Cpu)


@pytest.mark.django_db
class TestExtendedPropertyBinding:
    """US4: CHECK constraint — exactly one binding must be set."""

    def test_entity_level_property_created(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        data = {"content_type": nand_ct.pk, "property_set": None, "name": "J per PU"}
        response = api_client.post(EXT_PROP_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_both_bindings_set_rejected(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import ExtendedPropertySet
        eps = ExtendedPropertySet.objects.create(name="Test Set")
        data = {
            "content_type": nand_ct.pk,
            "property_set": eps.pk,
            "name": "Invalid Prop",
        }
        response = api_client.post(EXT_PROP_URL, data, format="json")
        # Serializer validate() catches this before DB
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_neither_binding_set_rejected(self, api_client: APIClient) -> None:
        data = {"content_type": None, "property_set": None, "name": "No Binding"}
        response = api_client.post(EXT_PROP_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestExtendedPropertyValueScoping:
    """US4: Per-instance values are scoped to the correct instance."""

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

        # Set different values per instance
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

        # Each instance returns its own value
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
