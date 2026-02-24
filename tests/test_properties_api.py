import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from nand.models import Nand

CONFIG_URL = "/api/property-configs/"
CONFIG_SET_URL = "/api/config-sets/"


@pytest.fixture
def nand_ct(db) -> ContentType:
    return ContentType.objects.get_for_model(Nand)


@pytest.mark.django_db
class TestPropertyConfigAPI:
    """US3: PropertyConfig CRUD and unique constraint."""

    def test_create_config(self, api_client: APIClient, nand_ct: ContentType) -> None:
        data = {"content_type": nand_ct.pk, "name": "capacity_per_die", "is_numeric": True}
        response = api_client.post(CONFIG_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "capacity_per_die"

    def test_unique_content_type_name_enforced(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        data = {"content_type": nand_ct.pk, "name": "capacity_per_die"}
        api_client.post(CONFIG_URL, data, format="json")
        response = api_client.post(CONFIG_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPropertyConfigSetAPI:
    """US3: PropertyConfigSet with ordered memberships."""

    def test_create_set(self, api_client: APIClient, nand_ct: ContentType) -> None:
        data = {"content_type": nand_ct.pk, "name": "Nand Full View"}
        response = api_client.post(CONFIG_SET_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Nand Full View"

    def test_unique_set_per_content_type(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        data = {"content_type": nand_ct.pk, "name": "Nand Full View"}
        api_client.post(CONFIG_SET_URL, data, format="json")
        response = api_client.post(CONFIG_SET_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_config_set_items_ordered_by_index(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership

        c1 = PropertyConfig.objects.create(content_type=nand_ct, name="field_a")
        c2 = PropertyConfig.objects.create(content_type=nand_ct, name="field_b")
        cs = PropertyConfigSet.objects.create(content_type=nand_ct, name="Ordered Set")
        PropertyConfigSetMembership.objects.create(config_set=cs, config=c2, index=0)
        PropertyConfigSetMembership.objects.create(config_set=cs, config=c1, index=1)

        response = api_client.get(f"{CONFIG_SET_URL}{cs.pk}/")
        assert response.status_code == status.HTTP_200_OK
        indices = [item["index"] for item in response.data["items"]]
        assert indices == sorted(indices)

    def test_unique_index_in_set_enforced(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from properties.models import PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership

        c1 = PropertyConfig.objects.create(content_type=nand_ct, name="f1")
        c2 = PropertyConfig.objects.create(content_type=nand_ct, name="f2")
        cs = PropertyConfigSet.objects.create(content_type=nand_ct, name="CS1")
        PropertyConfigSetMembership.objects.create(config_set=cs, config=c1, index=0)
        with pytest.raises(Exception):
            PropertyConfigSetMembership.objects.create(config_set=cs, config=c2, index=0)

    def test_config_set_param_returns_configs(
        self, api_client: APIClient, nand_ct: ContentType
    ) -> None:
        from nand.models import Nand as NandModel
        from properties.models import PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership

        nand = NandModel.objects.create(**{
            "name": "BiCS8",
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
        c = PropertyConfig.objects.create(content_type=nand_ct, name="capacity_per_die")
        cs = PropertyConfigSet.objects.create(content_type=nand_ct, name="View")
        PropertyConfigSetMembership.objects.create(config_set=cs, config=c, index=0)

        # Without param — config_set is None
        response = api_client.get(f"/api/nand/{nand.pk}/")
        assert response.data["config_set"] is None

        # With param — config_set included
        response = api_client.get(f"/api/nand/{nand.pk}/?config_set={cs.pk}")
        assert response.data["config_set"] is not None
        assert response.data["config_set"]["id"] == cs.pk
        assert len(response.data["config_set"]["items"]) == 1
