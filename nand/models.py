from django.core.validators import MaxValueValidator
from django.db import models

from properties.base import BaseEntity


class Nand(BaseEntity):
    """
    NAND flash technology definition (e.g. BiCS8, BiCS9).
    Fields stored flat; API response nests them into logical groups.
    """

    # --- Die Physical Properties ---
    capacity_per_die = models.PositiveBigIntegerField()
    plane_per_die = models.PositiveSmallIntegerField()
    block_per_plane = models.PositiveIntegerField()
    d1_d2_ratio = models.FloatField(validators=[MaxValueValidator(1.0)])
    page_per_block = models.PositiveIntegerField()
    slc_page_per_block = models.PositiveIntegerField()
    node_per_page = models.PositiveIntegerField()
    finger_per_wl = models.PositiveSmallIntegerField()

    # --- Endurance ---
    tlc_qlc_pe = models.PositiveIntegerField(help_text="TLC/QLC P/E cycles")
    static_slc_pe = models.PositiveIntegerField()
    table_slc_pe = models.PositiveIntegerField()
    bad_block_ratio = models.FloatField()

    # --- RAID ---
    max_data_raid_frame = models.PositiveIntegerField()
    max_slc_wc_raid_frame = models.PositiveIntegerField()
    max_table_raid_frame = models.PositiveIntegerField()
    data_die_raid = models.PositiveIntegerField()
    table_die_raid = models.PositiveIntegerField()

    # --- Mapping / L2P / P2L ---
    l2p_unit = models.PositiveIntegerField()
    mapping_table_size = models.PositiveBigIntegerField()
    p2l_entry = models.PositiveIntegerField()
    with_p2l = models.PositiveSmallIntegerField()
    p2l_bitmap = models.PositiveIntegerField()
    l2p_ecc_data = models.PositiveIntegerField()
    l2p_ecc_spare = models.PositiveIntegerField()
    reserved_lca_number = models.PositiveIntegerField()

    # --- Firmware Configuration ---
    day_per_year = models.PositiveSmallIntegerField(default=365)
    power_cycle_count = models.PositiveIntegerField()
    default_rebuild_time = models.PositiveIntegerField()
    drive_log_region_size = models.PositiveIntegerField()
    drive_log_min_op = models.FloatField()
    using_slc_write_cache = models.BooleanField()
    using_pmd = models.BooleanField()
    min_mapping_op_with_pmd = models.FloatField()
    data_open = models.PositiveSmallIntegerField()
    data_open_with_slc_wc = models.PositiveSmallIntegerField()
    data_gc_damper_central = models.FloatField()
    min_pfail_vb = models.PositiveIntegerField()
    small_table_vb = models.PositiveIntegerField()
    pfail_max_plane_count = models.PositiveSmallIntegerField()
    bol_block_number = models.PositiveIntegerField()
    extra_table_life_for_align_spec = models.FloatField()

    # --- Channel-specific (JSON) ---
    pb_per_disk_by_channel = models.JSONField(
        default=dict,
        help_text='Channel count to value map, e.g. {"2": 100, "4": 200}',
    )

    # --- Journal ---
    journal_insert_time = models.PositiveIntegerField()
    journal_entry_size = models.PositiveIntegerField()
    journal_program_unit = models.PositiveIntegerField()

    class Meta:
        verbose_name = "NAND Technology"
        verbose_name_plural = "NAND Technologies"


class NandInstance(BaseEntity):
    """
    A specific NAND configuration/SKU (e.g. '0.5T 7%', '8T 28%').
    Represents a capacity + OP point on a given NAND technology.
    """

    nand = models.ForeignKey(Nand, on_delete=models.CASCADE, related_name="instances")

    module_capacity = models.PositiveBigIntegerField()
    user_capacity = models.PositiveBigIntegerField()
    namespace_num = models.PositiveSmallIntegerField()
    ns_remap_table_unit = models.PositiveIntegerField()
    data_pca_width = models.PositiveSmallIntegerField()
    l2p_width = models.PositiveSmallIntegerField()
    data_vb_die_ratio = models.FloatField(validators=[MaxValueValidator(1.0)])
    page_num_per_raid_tag = models.PositiveIntegerField()
    p2l_node_per_data_p2l_group = models.PositiveIntegerField()
    data_p2l_group_num = models.PositiveIntegerField()
    table_vb_good_die_ratio = models.FloatField(validators=[MaxValueValidator(1.0)])

    class Meta:
        verbose_name = "NAND Instance"
        constraints = [
            models.UniqueConstraint(
                fields=["nand", "name"],
                name="unique_nand_instance_name",
            ),
        ]


class NandPerf(BaseEntity):
    """NAND performance data for a given technology + channel configuration."""

    nand = models.ForeignKey(
        Nand, on_delete=models.CASCADE, related_name="perf_entries"
    )

    bandwidth = models.FloatField()
    module_capacity = models.PositiveBigIntegerField()
    channel = models.PositiveSmallIntegerField()
    die_per_channel = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "NAND Performance"
        verbose_name_plural = "NAND Performance Entries"
