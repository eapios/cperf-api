from typing import Any

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from nand.models import Nand, NandInstance, NandPerf
from properties.models import ExtendedPropertyValue, PropertyConfigSet


# --- Nand field group sub-serializers (read-only, flat-to-nested mapping) ---

class NandPhysicalSerializer(serializers.Serializer):
    capacity_per_die = serializers.IntegerField()
    plane_per_die = serializers.IntegerField()
    block_per_plane = serializers.IntegerField()
    d1_d2_ratio = serializers.FloatField()
    page_per_block = serializers.IntegerField()
    slc_page_per_block = serializers.IntegerField()
    node_per_page = serializers.IntegerField()
    finger_per_wl = serializers.IntegerField()


class NandEnduranceSerializer(serializers.Serializer):
    tlc_qlc_pe = serializers.IntegerField()
    static_slc_pe = serializers.IntegerField()
    table_slc_pe = serializers.IntegerField()
    bad_block_ratio = serializers.FloatField()


class NandRaidSerializer(serializers.Serializer):
    max_data_raid_frame = serializers.IntegerField()
    max_slc_wc_raid_frame = serializers.IntegerField()
    max_table_raid_frame = serializers.IntegerField()
    data_die_raid = serializers.IntegerField()
    table_die_raid = serializers.IntegerField()


class NandMappingSerializer(serializers.Serializer):
    l2p_unit = serializers.IntegerField()
    mapping_table_size = serializers.IntegerField()
    p2l_entry = serializers.IntegerField()
    with_p2l = serializers.IntegerField()
    p2l_bitmap = serializers.IntegerField()
    l2p_ecc_data = serializers.IntegerField()
    l2p_ecc_spare = serializers.IntegerField()
    reserved_lca_number = serializers.IntegerField()


class NandFirmwareSerializer(serializers.Serializer):
    day_per_year = serializers.IntegerField()
    power_cycle_count = serializers.IntegerField()
    default_rebuild_time = serializers.IntegerField()
    drive_log_region_size = serializers.IntegerField()
    drive_log_min_op = serializers.FloatField()
    using_slc_write_cache = serializers.BooleanField()
    using_pmd = serializers.BooleanField()
    min_mapping_op_with_pmd = serializers.FloatField()
    data_open = serializers.IntegerField()
    data_open_with_slc_wc = serializers.IntegerField()
    data_gc_damper_central = serializers.FloatField()
    min_pfail_vb = serializers.IntegerField()
    small_table_vb = serializers.IntegerField()
    pfail_max_plane_count = serializers.IntegerField()
    bol_block_number = serializers.IntegerField()
    extra_table_life_for_align_spec = serializers.FloatField()


class NandJournalSerializer(serializers.Serializer):
    journal_insert_time = serializers.IntegerField()
    journal_entry_size = serializers.IntegerField()
    journal_program_unit = serializers.IntegerField()


# --- Write serializer (accepts flat field names) ---

class NandWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nand
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


# --- Read serializer (nests fields into groups) ---

class NandSerializer(serializers.ModelSerializer):
    physical = NandPhysicalSerializer(source="*", read_only=True)
    endurance = NandEnduranceSerializer(source="*", read_only=True)
    raid = NandRaidSerializer(source="*", read_only=True)
    mapping = NandMappingSerializer(source="*", read_only=True)
    firmware = NandFirmwareSerializer(source="*", read_only=True)
    journal = NandJournalSerializer(source="*", read_only=True)
    config_set = serializers.SerializerMethodField()
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = Nand
        fields = [
            "id",
            "name",
            "physical",
            "endurance",
            "raid",
            "mapping",
            "firmware",
            "journal",
            "pb_per_disk_by_channel",
            "config_set",
            "extended_properties",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_config_set(self, obj: Nand) -> Any:
        request = self.context.get("request")
        if request is None:
            return None
        config_set_id = request.query_params.get("config_set")
        if not config_set_id:
            return None
        try:
            cs = PropertyConfigSet.objects.prefetch_related(
                "memberships__config"
            ).get(pk=config_set_id)
        except PropertyConfigSet.DoesNotExist:
            return None
        memberships = cs.memberships.select_related("config").order_by("index")
        return {
            "id": cs.id,
            "name": cs.name,
            "items": [
                {
                    "index": m.index,
                    "config": {
                        "id": m.config.id,
                        "name": m.config.name,
                        "display_text": m.config.display_text,
                        "unit": m.config.unit,
                        "decimal_place": m.config.decimal_place,
                        "is_numeric": m.config.is_numeric,
                    },
                }
                for m in memberships
            ],
        }

    def get_extended_properties(self, obj: Nand) -> Any:
        request = self.context.get("request")
        if request is None:
            return None
        include = request.query_params.get("include", "")
        if "extended_properties" not in include:
            return None
        ct = ContentType.objects.get_for_model(Nand)
        values = ExtendedPropertyValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).select_related("extended_property")
        return [
            {
                "id": v.id,
                "property_id": v.extended_property_id,
                "name": v.extended_property.name,
                "is_formula": v.extended_property.is_formula,
                "value": v.value,
            }
            for v in values
        ]


# --- NandInstance ---

class NandInstanceSerializer(serializers.ModelSerializer):
    config_set = serializers.SerializerMethodField()
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = NandInstance
        fields = [
            "id",
            "name",
            "nand",
            "module_capacity",
            "user_capacity",
            "namespace_num",
            "ns_remap_table_unit",
            "data_pca_width",
            "l2p_width",
            "data_vb_die_ratio",
            "page_num_per_raid_tag",
            "p2l_node_per_data_p2l_group",
            "data_p2l_group_num",
            "table_vb_good_die_ratio",
            "config_set",
            "extended_properties",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_config_set(self, obj: NandInstance) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        config_set_id = request.query_params.get("config_set")
        if not config_set_id:
            return None
        try:
            cs = PropertyConfigSet.objects.prefetch_related(
                "memberships__config"
            ).get(pk=config_set_id)
        except PropertyConfigSet.DoesNotExist:
            return None
        memberships = cs.memberships.select_related("config").order_by("index")
        return {
            "id": cs.id,
            "name": cs.name,
            "items": [
                {
                    "index": m.index,
                    "config": {
                        "id": m.config.id,
                        "name": m.config.name,
                        "display_text": m.config.display_text,
                        "unit": m.config.unit,
                        "decimal_place": m.config.decimal_place,
                        "is_numeric": m.config.is_numeric,
                    },
                }
                for m in memberships
            ],
        }

    def get_extended_properties(self, obj: NandInstance) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        include = request.query_params.get("include", "")
        if "extended_properties" not in include:
            return None
        ct = ContentType.objects.get_for_model(NandInstance)
        values = ExtendedPropertyValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).select_related("extended_property")
        return [
            {
                "id": v.id,
                "property_id": v.extended_property_id,
                "name": v.extended_property.name,
                "is_formula": v.extended_property.is_formula,
                "value": v.value,
            }
            for v in values
        ]


# --- NandPerf ---

class NandPerfSerializer(serializers.ModelSerializer):
    config_set = serializers.SerializerMethodField()
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = NandPerf
        fields = [
            "id",
            "name",
            "nand",
            "bandwidth",
            "module_capacity",
            "channel",
            "die_per_channel",
            "config_set",
            "extended_properties",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_config_set(self, obj: NandPerf) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        config_set_id = request.query_params.get("config_set")
        if not config_set_id:
            return None
        try:
            cs = PropertyConfigSet.objects.prefetch_related(
                "memberships__config"
            ).get(pk=config_set_id)
        except PropertyConfigSet.DoesNotExist:
            return None
        memberships = cs.memberships.select_related("config").order_by("index")
        return {
            "id": cs.id,
            "name": cs.name,
            "items": [
                {
                    "index": m.index,
                    "config": {
                        "id": m.config.id,
                        "name": m.config.name,
                        "display_text": m.config.display_text,
                        "unit": m.config.unit,
                        "decimal_place": m.config.decimal_place,
                        "is_numeric": m.config.is_numeric,
                    },
                }
                for m in memberships
            ],
        }

    def get_extended_properties(self, obj: NandPerf) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        include = request.query_params.get("include", "")
        if "extended_properties" not in include:
            return None
        ct = ContentType.objects.get_for_model(NandPerf)
        values = ExtendedPropertyValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).select_related("extended_property")
        return [
            {
                "id": v.id,
                "property_id": v.extended_property_id,
                "name": v.extended_property.name,
                "is_formula": v.extended_property.is_formula,
                "value": v.value,
            }
            for v in values
        ]
