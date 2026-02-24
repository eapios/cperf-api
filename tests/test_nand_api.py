import pytest
from rest_framework import status
from rest_framework.test import APIClient

NAND_URL = "/api/nand/"
INSTANCE_URL = "/api/nand-instances/"
PERF_URL = "/api/nand-perf/"

VALID_NAND_DATA = {
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
    "day_per_year": 365,
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
    "pb_per_disk_by_channel": {"2": 200, "4": 400},
    "journal_insert_time": 1000,
    "journal_entry_size": 64,
    "journal_program_unit": 4,
}


@pytest.mark.django_db
class TestNandAPI:
    """US2: CRUD for NAND technology."""

    def test_create_nand(self, api_client: APIClient) -> None:
        response = api_client.post(NAND_URL, VALID_NAND_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "BiCS8"
        assert "id" in response.data
        assert "created_at" in response.data

    def test_retrieve_nand_has_grouped_fields(self, api_client: APIClient) -> None:
        created = api_client.post(NAND_URL, VALID_NAND_DATA, format="json")
        response = api_client.get(f"{NAND_URL}{created.data['id']}/")
        assert response.status_code == status.HTTP_200_OK
        assert "physical" in response.data
        assert "endurance" in response.data
        assert "raid" in response.data
        assert "mapping" in response.data
        assert "firmware" in response.data
        assert "journal" in response.data
        assert "pb_per_disk_by_channel" in response.data
        # Nested fields accessible
        assert response.data["physical"]["capacity_per_die"] == VALID_NAND_DATA["capacity_per_die"]

    def test_delete_nand_cascades_instances(self, api_client: APIClient) -> None:
        nand = api_client.post(NAND_URL, VALID_NAND_DATA, format="json").data
        inst_data = {
            "nand": nand["id"],
            "name": "0.5T 7%",
            "module_capacity": 549755813888,
            "user_capacity": 500000000000,
            "namespace_num": 1,
            "ns_remap_table_unit": 4096,
            "data_pca_width": 8,
            "l2p_width": 16,
            "data_vb_die_ratio": 0.9,
            "page_num_per_raid_tag": 4,
            "p2l_node_per_data_p2l_group": 8,
            "data_p2l_group_num": 16,
            "table_vb_good_die_ratio": 0.95,
        }
        inst = api_client.post(INSTANCE_URL, inst_data, format="json")
        assert inst.status_code == status.HTTP_201_CREATED

        # Delete parent
        api_client.delete(f"{NAND_URL}{nand['id']}/")
        # Instance should be gone
        assert api_client.get(f"{INSTANCE_URL}{inst.data['id']}/").status_code == status.HTTP_404_NOT_FOUND

    def test_ratio_above_1_rejected(self, api_client: APIClient) -> None:
        data = {**VALID_NAND_DATA, "d1_d2_ratio": 1.5}
        response = api_client.post(NAND_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nand_instance_unique_constraint(self, api_client: APIClient) -> None:
        nand = api_client.post(NAND_URL, VALID_NAND_DATA, format="json").data
        inst_base = {
            "nand": nand["id"],
            "name": "0.5T 7%",
            "module_capacity": 549755813888,
            "user_capacity": 500000000000,
            "namespace_num": 1,
            "ns_remap_table_unit": 4096,
            "data_pca_width": 8,
            "l2p_width": 16,
            "data_vb_die_ratio": 0.9,
            "page_num_per_raid_tag": 4,
            "p2l_node_per_data_p2l_group": 8,
            "data_p2l_group_num": 16,
            "table_vb_good_die_ratio": 0.95,
        }
        assert api_client.post(INSTANCE_URL, inst_base, format="json").status_code == status.HTTP_201_CREATED
        assert api_client.post(INSTANCE_URL, inst_base, format="json").status_code == status.HTTP_400_BAD_REQUEST

    def test_nand_filter_by_nand(self, api_client: APIClient) -> None:
        nand = api_client.post(NAND_URL, VALID_NAND_DATA, format="json").data
        perf_data = {
            "nand": nand["id"],
            "name": "2ch perf",
            "bandwidth": 2000.0,
            "module_capacity": 549755813888,
            "channel": 2,
            "die_per_channel": 8,
        }
        api_client.post(PERF_URL, perf_data, format="json")
        response = api_client.get(PERF_URL, {"nand": nand["id"]})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_config_set_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(NAND_URL, VALID_NAND_DATA, format="json")
        response = api_client.get(f"{NAND_URL}{created.data['id']}/")
        assert response.data["config_set"] is None

    def test_extended_properties_omitted_by_default(self, api_client: APIClient) -> None:
        created = api_client.post(NAND_URL, VALID_NAND_DATA, format="json")
        response = api_client.get(f"{NAND_URL}{created.data['id']}/")
        assert response.data["extended_properties"] is None
