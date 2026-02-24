# Backend Model Design

Last Updated: 2026-02-23

Based on frontend interface spec (`docs/models.ts`). This document proposes Django models
for backend implementation, with improvements over the raw TypeScript interfaces.

---

## Table of Contents

- [Design Decisions](#design-decisions)
- [App Structure](#app-structure)
- [Models](#models)
  - [properties app](#properties-app)
  - [nand app](#nand-app)
  - [cpu app](#cpu-app)
  - [dram app](#dram-app)
  - [results app](#results-app)
- [Table Layout](#table-layout)
- [API Response Shape](#api-response-shape)
- [Migration from Current Models](#migration-from-current-models)
- [Resolved Questions](#resolved-questions)
- [Open Questions](#open-questions)

---

## Design Decisions

### 1. Abstract base instead of multi-table inheritance

**Current**: `Component` base table with multi-table inheritance (`CpuComponent`, `DramComponent`).

**Proposed**: Abstract `BaseEntity` mixin — no shared DB table.

**What is `BaseEntity`?** It's a Python-only shortcut. Every entity needs `name`,
`created_at`, `updated_at`. Instead of repeating those 3 fields in every model,
`BaseEntity` defines them once with `abstract = True`. Django copies the fields into
each child model at class definition time — no table, no JOIN, no runtime cost.

```
# Without BaseEntity — repeat in every model:
class Nand(models.Model):
    name = models.CharField(max_length=255)         # repeated
    created_at = models.DateTimeField(auto_now_add=True)  # repeated
    updated_at = models.DateTimeField(auto_now=True)      # repeated
    capacity_per_die = ...

class Cpu(models.Model):
    name = models.CharField(max_length=255)         # repeated
    created_at = models.DateTimeField(auto_now_add=True)  # repeated
    updated_at = models.DateTimeField(auto_now=True)      # repeated
    bandwidth = ...

# With BaseEntity — define once:
class Nand(BaseEntity):        # gets name, created_at, updated_at automatically
    capacity_per_die = ...

class Cpu(BaseEntity):         # gets name, created_at, updated_at automatically
    bandwidth = ...
```

Both produce identical database tables. `BaseEntity` is purely a code-level DRY shortcut.

**Why not multi-table inheritance?** The frontend spec has no unified "component" concept.
Cpu, Dram, Nand have vastly different field sets. Multi-table inheritance adds a JOIN on
every query for no benefit here.

### 2. Integer PKs (not UUIDs)

The frontend spec uses `id: number`. Integer auto-increment PKs are simpler, faster for
JOINs, and match the frontend expectation.

> If UUIDs are needed later (distributed systems, URL obfuscation), we can add a `uuid`
> field alongside the integer PK without changing the PK itself.

### 3. Single table for Nand (not decomposed)

The Nand entity has ~45 fields. Options considered:

| Approach | Pros | Cons |
|----------|------|------|
| **Single table** | No JOINs, simple queries, DB validation on all fields | Large model file |
| Separate tables (NandPhysical, NandEndurance...) | Clean separation | Always need JOINs, over-normalized |
| JSONField sub-objects | Flexible | No DB-level validation per field |

**Chosen**: Single table with **logical field grouping** in the model and **nested groups
in the API response**. Best of both worlds.

### 4. PropertyConfig: swappable sets, reusable configs

PropertyConfigs describe how the frontend renders columns (display text, unit, decimal
places, etc.). They are **standalone** — not bound to any model type directly.

Each config belongs to a model type via `ContentType`. Configs are then grouped into
**named sets** (`PropertyConfigSet`), also bound to the same model type. Frontend can:
- Pick which config set to use for rendering
- Not request configs at all
- One PropertyConfig can appear in multiple sets (of the same model type)

### 5. ExtendedProperty: dual binding, optional grouping

ExtendedProperties define computed/user-added values (formulas, constants). **Independent
of PropertyConfig** — no FK between them. Two binding modes:

- **Entity-level** (Nand, Cpu, Dram): `ExtendedProperty.content_type` is set,
  `property_set` is null. Queried directly via ContentType — same as the original design.
- **Result-level** (workloads): `ExtendedProperty.content_type` is null,
  `property_set` points to an `ExtendedPropertySet` (whose `content_type` = ResultWorkload).
  The set is referenced from `ResultProfileWorkload`, enabling different properties per
  profile-workload pair.

Entity-level properties don't need sets — they remain simple flat lookups. Sets exist
only for result-level grouping where the same workload in different profiles needs
different property values.

### 6. Channel-specific fields normalized

`pbPerDiskWhen2Ch` / `pbPerDiskWhen4Ch` replaced with a JSONField to support any channel
count without schema changes. Currently only channels 2 and 4 are used.

### 7. ResultProfile + workload-scoped properties

Renamed from `ResultCategory` to `ResultProfile`. The same workload (e.g. "GC Read") can
appear in multiple profiles (e.g. "AIPR Upper Bound", "AIPR Lower Bound") with **different**
extended properties and config sets per appearance.

This is handled via a `ResultProfileWorkload` through model that carries FKs to
`PropertyConfigSet` (nullable, pending rendering decision) and `ExtendedPropertySet`.

---

## App Structure

```
properties/           # PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership,
                      # ExtendedPropertySet, ExtendedProperty, ExtendedPropertyValue, BaseEntity
nand/                 # Nand, NandInstance, NandPerf
cpu/                  # Cpu (redesigned)
dram/                 # Dram (redesigned)
results/              # ResultProfile, ResultWorkload, ResultProfileWorkload,
                      # ResultRecord, ResultInstance
```

---

## Models

### Shared Abstract Base

```python
# properties/base.py

from django.db import models


class BaseEntity(models.Model):
    """
    Abstract base — stamps name + timestamps onto every child.
    No DB table created. Pure code-level DRY shortcut.
    """
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name
```

---

### properties app

```python
# properties/models.py

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PropertyConfig(models.Model):
    """
    Rendering/validation config for a property column in the spreadsheet.

    Bound to a model type via ContentType so that config sets for a given model
    can only include configs that belong to that model. One PropertyConfig can
    still be included in multiple sets (of the same model type).
    """

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="property_configs",
        help_text="Which model type this config belongs to (Nand, Cpu, etc.)",
    )
    name = models.CharField(max_length=255)

    # Display
    display_text = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")

    # Behavior flags
    read_only = models.BooleanField(default=False)
    is_extended = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    # Numeric formatting
    is_numeric = models.BooleanField(default=False)
    sub_type = models.CharField(
        max_length=50, blank=True, default="",
        help_text="percent, byte, etc.",
    )
    decimal_place = models.PositiveSmallIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["content_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "name"],
                name="unique_config_per_model_type",
            ),
        ]

    def __str__(self) -> str:
        return self.display_text or self.name


class PropertyConfigSet(models.Model):
    """
    A named collection of PropertyConfigs for a specific model type.

    Multiple sets can exist per model type (e.g. "Nand Full View", "Nand Compact View").
    Frontend chooses which set to use for rendering, or skips configs entirely.
    """

    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="config_sets",
        help_text="Which model type this set is for (Nand, Cpu, etc.)",
    )
    configs = models.ManyToManyField(
        PropertyConfig,
        through="PropertyConfigSetMembership",
        related_name="config_sets",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "name"],
                name="unique_config_set_per_model_type",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class PropertyConfigSetMembership(models.Model):
    """
    Through model for PropertyConfigSet ↔ PropertyConfig M2M.
    Stores the display order (index) of a config within a specific set.
    The same config can have different indices in different sets.
    """

    config_set = models.ForeignKey(
        PropertyConfigSet, on_delete=models.CASCADE, related_name="memberships",
    )
    config = models.ForeignKey(
        PropertyConfig, on_delete=models.CASCADE, related_name="memberships",
    )
    index = models.PositiveIntegerField(
        help_text="Display order of this config within the set",
    )

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["config_set", "config"],
                name="unique_config_in_set",
            ),
            models.UniqueConstraint(
                fields=["config_set", "index"],
                name="unique_index_in_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.config_set.name}[{self.index}] = {self.config.name}"


class ExtendedPropertySet(models.Model):
    """
    A named collection of ExtendedProperties for result-level grouping.

    Used by ResultProfileWorkload to give each profile-workload pair its own
    set of extended properties. Entity-level properties (Nand, Cpu, Dram) do NOT
    use sets — they bind directly via ExtendedProperty.content_type.

    content_type points to ResultWorkload's ContentType for result-level sets,
    enabling filtering and admin convenience.
    """

    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="extended_property_sets",
        help_text="Model type for the set (e.g. ResultWorkload for result-level sets).",
    )

    def __str__(self) -> str:
        return self.name


class ExtendedProperty(models.Model):
    """
    Definition of a user-defined computed/constant property.
    Independent of PropertyConfig — no FK between them.

    This is the DEFINITION only (name + formula flag). Actual per-instance
    values live in ExtendedPropertyValue, linked via GenericFK.

    Two binding modes (exactly one should be set):
    - Entity-level: content_type is set, property_set is null.
      Defines a property column for a model type (Nand, Cpu, etc.).
    - Result-level: content_type is null, property_set is set.
      Defines a property column for a specific profile-workload pair.

    If is_formula=True, values stored in ExtendedPropertyValue contain
    Excel-compatible formula strings. Frontend evaluates them.
    If is_formula=False, values are raw JSON (number or string).
    """

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="extended_properties",
        help_text="Model type binding for entity-level props. Null for result-level.",
    )
    property_set = models.ForeignKey(
        ExtendedPropertySet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="properties",
        help_text="Set binding for result-level props. Null for entity-level.",
    )
    name = models.CharField(max_length=255)
    is_formula = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # Entity-level: unique name per model type
            models.UniqueConstraint(
                fields=["content_type", "name"],
                condition=models.Q(content_type__isnull=False),
                name="unique_extended_prop_per_model_type",
            ),
            # Result-level: unique name per set
            models.UniqueConstraint(
                fields=["property_set", "name"],
                condition=models.Q(property_set__isnull=False),
                name="unique_extended_prop_per_set",
            ),
            # Exactly one binding must be set
            models.CheckConstraint(
                condition=(
                    models.Q(content_type__isnull=False, property_set__isnull=True)
                    | models.Q(content_type__isnull=True, property_set__isnull=False)
                ),
                name="extended_prop_single_binding",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ExtendedPropertyValue(models.Model):
    """
    Per-instance value for an ExtendedProperty.

    Uses GenericFK to point to any entity instance (Nand, Cpu, Dram,
    NandInstance, NandPerf) or ResultInstance. The target model type is
    implicit from extended_property.content_type (entity-level) or
    extended_property.property_set (result-level via ResultInstance).

    Examples:
    - Nand "BiCS8" has "J per PU" = "=A1*B1" (formula)
    - Nand "BiCS9" has "J per PU" = "=A1*B2" (different formula)
    - ResultInstance #1 has "Time" = "=E1*F1"
    - ResultInstance #2 has "Time" = "=E1*F2"
    """

    extended_property = models.ForeignKey(
        ExtendedProperty,
        on_delete=models.CASCADE,
        related_name="values",
    )
    # GenericFK to the owning instance
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="extended_property_values",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    value = models.JSONField(
        help_text="Formula string (when is_formula=True) or literal value",
    )

    class Meta:
        constraints = [
            # One value per property per instance
            models.UniqueConstraint(
                fields=["extended_property", "content_type", "object_id"],
                name="unique_value_per_prop_per_instance",
            ),
        ]
        indexes = [
            models.Index(
                fields=["content_type", "object_id"],
                name="idx_ext_prop_value_instance",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.extended_property.name} = {self.value}"
```

**Key points**:
- `PropertyConfig` is bound to a model type via `content_type` FK
- `PropertyConfigSet` groups configs into named sets for a model type — only configs
  with matching `content_type` should be added (enforced at application level)
- `PropertyConfigSetMembership` is the through model that stores display order (`index`)
  per set — the same config can appear at different positions in different sets
- `ExtendedProperty` is the **definition** (name + is_formula). No value stored here
- `ExtendedPropertyValue` stores **per-instance values** via GenericFK. Each entity
  instance (Nand #1, Nand #2) or ResultInstance gets its own value row
- `ExtendedProperty` has dual binding: `content_type` (entity-level) or `property_set`
  (result-level) — exactly one should be non-null (enforced by CheckConstraint)
- `ExtendedPropertySet` exists only for result-level grouping. Entity-level properties
  are queried directly via ContentType without needing a set

**Querying**:
```python
from django.contrib.contenttypes.models import ContentType

nand_ct = ContentType.objects.get_for_model(Nand)

# All config sets available for Nand
PropertyConfigSet.objects.filter(content_type=nand_ct)

# Configs in a specific set, ordered by index
config_set = PropertyConfigSet.objects.get(content_type=nand_ct, name="Full View")
config_set.configs.all()  # ordered by membership index

# Memberships with explicit index access
config_set.memberships.select_related("config").all()

# Entity-level extended property DEFINITIONS for Nand
ExtendedProperty.objects.filter(content_type=nand_ct)

# Entity-level extended property VALUES for a specific Nand instance
nand = Nand.objects.get(id=1)
ExtendedPropertyValue.objects.filter(
    content_type=nand_ct, object_id=nand.id
).select_related("extended_property")

# Result-level extended property definitions (via set)
ext_set = ExtendedPropertySet.objects.get(id=3)
ext_set.properties.all()

# Result-level values for a specific ResultInstance
ri_ct = ContentType.objects.get_for_model(ResultInstance)
ExtendedPropertyValue.objects.filter(
    content_type=ri_ct, object_id=result_instance.id
).select_related("extended_property")
```

---

### nand app

```python
# nand/models.py

from django.core.validators import MaxValueValidator
from django.db import models
from properties.base import BaseEntity


class Nand(BaseEntity):
    """
    NAND flash technology definition (e.g. BiCS8, BiCS9).
    Fields grouped logically; API response nests them under sub-objects.

    PropertyConfigSets and ExtendedProperties are looked up via ContentType,
    not stored on this model.
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

    # --- Channel-specific (normalized) ---
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

    nand = models.ForeignKey(
        Nand, on_delete=models.CASCADE, related_name="instances"
    )

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
```

**Changes from frontend TS**:
- `pbPerDiskWhen2Ch` / `pbPerDiskWhen4Ch` → `pb_per_disk_by_channel` JSONField
- `usingSlcWriteCache: number` / `usingPmd: number` → `BooleanField` (confirmed boolean)
- `NandPerf` now uses `BaseEntity` (gets `name`, `created_at`, `updated_at`)
- `d1_d2_ratio`, `data_vb_die_ratio`, `table_vb_good_die_ratio` have `MaxValueValidator(1.0)`
- `NandInstance.configId: number[]` typo from TS fixed
- No relationship fields for configs/extended_properties — looked up via ContentType

---

### cpu app

```python
# cpu/models.py

from django.db import models
from properties.base import BaseEntity


class Cpu(BaseEntity):
    """CPU component for performance calculation."""

    bandwidth = models.FloatField()
```

---

### dram app

```python
# dram/models.py

from django.db import models
from properties.base import BaseEntity


class Dram(BaseEntity):
    """DRAM component for performance calculation."""

    bandwidth = models.FloatField()
    channel = models.PositiveSmallIntegerField()
    transfer_rate = models.FloatField()
```

---

### results app

```python
# results/models.py

from django.db import models
from properties.base import BaseEntity
from properties.models import ExtendedPropertySet, PropertyConfigSet


class ResultProfile(models.Model):
    """
    A result grouping (e.g. AIPR Upper Bound, AIPR Lower Bound, Multi-plane Read).
    Renamed from ResultCategory.

    Workloads are linked via ResultProfileWorkload through model, which carries
    per-appearance config_set and extended_property_set.
    """

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Result Profiles"

    def __str__(self) -> str:
        return self.name


class ResultWorkload(models.Model):
    """
    A workload definition (e.g. Host Write, TLC Erase, GC Read).
    Shared definition — properties/configs vary per profile appearance.
    """

    name = models.CharField(max_length=255)
    type = models.IntegerField(help_text="Workload type identifier (opaque integer)")

    profiles = models.ManyToManyField(
        ResultProfile,
        through="ResultProfileWorkload",
        related_name="workloads",
    )

    def __str__(self) -> str:
        return self.name


class ResultProfileWorkload(models.Model):
    """
    Through model: a workload's appearance in a specific profile.

    Each appearance can have its own config set (rendering) and extended property set
    (computed values). This supports the requirement that "GC Read" in "AIPR Upper Bound"
    can have different properties than "GC Read" in "AIPR Lower Bound".
    """

    profile = models.ForeignKey(
        ResultProfile, on_delete=models.CASCADE, related_name="profile_workloads",
    )
    workload = models.ForeignKey(
        ResultWorkload, on_delete=models.CASCADE, related_name="profile_workloads",
    )
    config_set = models.ForeignKey(
        PropertyConfigSet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_profile_workloads",
        help_text="Rendering config for this workload in this profile",
    )
    extended_property_set = models.ForeignKey(
        ExtendedPropertySet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_profile_workloads",
        help_text="Computed properties for this workload in this profile",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "workload"],
                name="unique_workload_per_profile",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.profile.name} / {self.workload.name}"


class ResultRecord(BaseEntity):
    """
    A saved result record — captures which hardware was selected and
    groups the ResultInstances produced.

    Created on-demand when the user explicitly requests to save/record
    results. The name field (from BaseEntity) serves as a user-facing
    label, e.g. "BiCS8 + DDR5-A baseline run".

    Hardware FKs are all nullable because not every result type
    requires all hardware inputs.
    """

    nand = models.ForeignKey(
        "nand.Nand", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="result_records",
    )
    nand_instance = models.ForeignKey(
        "nand.NandInstance", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="result_records",
    )
    nand_perf = models.ForeignKey(
        "nand.NandPerf", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="result_records",
    )
    cpu = models.ForeignKey(
        "cpu.Cpu", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="result_records",
    )
    dram = models.ForeignKey(
        "dram.Dram", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="result_records",
    )

    class Meta:
        verbose_name = "Result Record"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class ResultInstance(models.Model):
    """
    A specific result entry — one per profile-workload per result record.

    Identified by the (result_record, profile_workload) pair — no name needed.
    Each instance carries its own ExtendedPropertyValues via GenericFK.
    """

    profile_workload = models.ForeignKey(
        ResultProfileWorkload,
        on_delete=models.CASCADE,
        related_name="instances",
    )
    result_record = models.ForeignKey(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name="result_instances",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Result Instance"
        constraints = [
            models.UniqueConstraint(
                fields=["result_record", "profile_workload"],
                name="unique_result_per_record_workload",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.result_record.name} / {self.profile_workload}"
```

**Key design**:
- `ResultProfile` (renamed from `ResultCategory`) is a named grouping
- `ResultWorkload` is a shared workload definition
- `ResultProfileWorkload` is the through model that carries per-appearance FKs:
  - `config_set` → reuses `PropertyConfigSet` (nullable, pending rendering decision)
  - `extended_property_set` → reuses `ExtendedPropertySet` (property definitions)
- `ResultInstance` is a specific data row within a profile-workload pair.
  Extended property **values** are stored via `ExtendedPropertyValue` (GenericFK)
- `ResultRecord` captures a saved result run — which hardware was used
  and which ResultInstances were produced. Created on user request only
- The same workload can appear in multiple profiles with different properties

**Querying**:
```python
# All workloads in a profile, with their property definitions
profile = ResultProfile.objects.get(name="AIPR Upper Bound")
for pw in profile.profile_workloads.select_related("workload", "extended_property_set"):
    print(pw.workload.name)
    if pw.extended_property_set:
        for prop in pw.extended_property_set.properties.all():
            print(f"  {prop.name} (formula={prop.is_formula})")

# All result instances for a profile-workload, with their values
pw = ResultProfileWorkload.objects.get(profile__name="AIPR Upper Bound", workload__name="GC Read")
ri_ct = ContentType.objects.get_for_model(ResultInstance)
for ri in pw.instances.all():
    values = ExtendedPropertyValue.objects.filter(
        content_type=ri_ct, object_id=ri.id
    ).select_related("extended_property")
    for v in values:
        print(f"  ri#{ri.id}: {v.extended_property.name} = {v.value}")

# All profiles a workload appears in
workload = ResultWorkload.objects.get(name="GC Read")
for pw in workload.profile_workloads.select_related("profile"):
    print(pw.profile.name)

# Load a saved result record with its hardware and results
record = ResultRecord.objects.select_related(
    "nand", "nand_instance", "nand_perf", "cpu", "dram"
).get(id=1)
print(f"Hardware: {record.nand}, {record.cpu}, {record.dram}")
for ri in record.result_instances.select_related("profile_workload__workload"):
    print(f"  {ri.profile_workload.workload.name} (ri#{ri.id})")
```

---

## Table Layout

### Actual database tables created

```
properties_propertyconfig
┌────┬─────────────────┬────────────────────┬──────────────┬─────────┬─────────────┬──────┐
│ id │ content_type_id │ name               │ display_text │ is_ext. │ is_numeric  │ unit │
├────┼─────────────────┼────────────────────┼──────────────┼─────────┼─────────────┼──────┤
│  1 │  8 (nand.nand)  │ capacity_per_die   │ Cap/Die      │ false   │ true        │ B    │
│  2 │  8 (nand.nand)  │ plane_per_die      │ Plane/Die    │ false   │ true        │      │
│ .. │             ... │                ... │          ... │     ... │         ... │  ... │
│ 45 │  8 (nand.nand)  │ journal_prog_unit  │ J.P.U.       │ false   │ true        │      │
│ 46 │  8 (nand.nand)  │ journal_per_pu     │ J/PU         │ true    │ true        │      │
│ 47 │ 10 (cpu.cpu)    │ bandwidth          │ BW           │ false   │ true        │ MB/s │
│ 48 │ 11 (dram.dram)  │ bandwidth          │ BW           │ false   │ true        │ MB/s │
│ 49 │ 11 (dram.dram)  │ channel            │ CH           │ false   │ true        │      │
│ 50 │ 11 (dram.dram)  │ transfer_rate      │ Xfer Rate    │ false   │ true        │ MT/s │
└────┴─────────────────┴────────────────────┴──────────────┴─────────┴─────────────┴──────┘
Each config belongs to a model type. "bandwidth" for Cpu (id=47) and Dram (id=48) are separate rows.
Config sets for Nand can only include configs where content_type = nand.nand.
Display order (index) is stored on the junction table, not here.

UNIQUE constraint: (content_type_id, name)


properties_propertyconfigset
┌────┬───────────────────┬─────────────────┐
│ id │ name              │ content_type_id │
├────┼───────────────────┼─────────────────┤
│  1 │ Nand Full View    │  8 (nand.nand)  │
│  2 │ Nand Compact View │  8 (nand.nand)  │
│  3 │ Cpu Default       │ 10 (cpu.cpu)    │
│  4 │ Dram Default      │ 11 (dram.dram)  │
└────┴───────────────────┴─────────────────┘
UNIQUE constraint: (content_type_id, name)


properties_propertyconfigsetmembership  (M2M through model)
┌────┬────────────────┬───────────────────┬───────┐
│ id │ config_set_id  │ config_id         │ index │
├────┼────────────────┼───────────────────┼───────┤
│  1 │ 1 (Nand Full)  │  1 (capacity/die) │     0 │
│  2 │ 1 (Nand Full)  │  2 (plane/die)    │     1 │
│  3 │ 1 (Nand Full)  │ 46 (journal/pu)   │    44 │
│  4 │ 2 (Nand Comp.) │  1 (capacity/die) │     0 │  ← same config, different index per set
│  5 │ 2 (Nand Comp.) │  2 (plane/die)    │     1 │
│  6 │ 3 (Cpu Def.)   │ 47 (cpu bw)       │     0 │
│  7 │ 4 (Dram Def.)  │ 48 (dram bw)      │     0 │
│  8 │ 4 (Dram Def.)  │ 49 (channel)      │     1 │
│  9 │ 4 (Dram Def.)  │ 50 (xfer rate)    │     2 │
└────┴────────────────┴───────────────────┴───────┘
UNIQUE constraints: (config_set_id, config_id), (config_set_id, index)


properties_extendedpropertyset
┌────┬──────────────────┬──────────────────────────────┐
│ id │ name             │ content_type_id              │
├────┼──────────────────┼──────────────────────────────┤
│  1 │ GC Read / Upper  │ 12 (results.resultworkload)  │
│  2 │ GC Read / Lower  │ 12 (results.resultworkload)  │
│  3 │ Host Write / Up  │ 12 (results.resultworkload)  │
└────┴──────────────────┴──────────────────────────────┘
content_type points to ResultWorkload. Entity-level props don't need sets.


properties_extendedproperty  (DEFINITION only — no value column)
┌────┬─────────────────┬─────────────────┬─────────────┬────────────┐
│ id │ content_type_id │ property_set_id │ name        │ is_formula │
├────┼─────────────────┼─────────────────┼─────────────┼────────────┤
│  1 │  8 (nand.nand)  │ NULL            │ J per PU    │ true       │  ← entity-level
│  2 │  8 (nand.nand)  │ NULL            │ Disk OP     │ true       │  ← entity-level
│  3 │ NULL            │ 1 (GC Rd/Up)    │ Time        │ true       │  ← result-level
│  4 │ NULL            │ 1 (GC Rd/Up)    │ Performance │ true       │  ← result-level
│  5 │ NULL            │ 2 (GC Rd/Lo)    │ Time        │ true       │  ← same name, different set
│  6 │ NULL            │ 2 (GC Rd/Lo)    │ Performance │ true       │
└────┴─────────────────┴─────────────────┴─────────────┴────────────┘
Exactly one of content_type_id / property_set_id is non-null (CHECK constraint).
Conditional UNIQUE: (content_type_id, name) WHERE content_type IS NOT NULL
Conditional UNIQUE: (property_set_id, name) WHERE property_set IS NOT NULL


properties_extendedpropertyvalue  (per-instance values via GenericFK)
┌────┬──────────────────────┬─────────────────┬───────────┬───────────┐
│ id │ extended_property_id │ content_type_id │ object_id │ value     │
├────┼──────────────────────┼─────────────────┼───────────┼───────────┤
│  1 │ 1 (J per PU)         │  8 (nand.nand)  │ 1 (BiCS8) │ "=A1*B1"  │  ← Nand #1's value
│  2 │ 1 (J per PU)         │  8 (nand.nand)  │ 2 (BiCS9) │ "=A1*B2"  │  ← Nand #2's value (different!)
│  3 │ 2 (Disk OP)          │  8 (nand.nand)  │ 1 (BiCS8) │ "=C1/D1"  │
│  4 │ 2 (Disk OP)          │  8 (nand.nand)  │ 2 (BiCS9) │ "=C1/D2"  │
│  5 │ 3 (Time)             │ 13 (ResultInst) │ 1 (ri#1)  │ "=E1*F1"  │  ← ResultInstance #1
│  6 │ 3 (Time)             │ 13 (ResultInst) │ 2 (ri#2)  │ "=E1*F2"  │  ← ResultInstance #2
│  7 │ 4 (Performance)      │ 13 (ResultInst) │ 1 (ri#1)  │ "=G1/H1"  │
│  8 │ 4 (Performance)      │ 13 (ResultInst) │ 2 (ri#2)  │ "=G1/H2"  │
└────┴──────────────────────┴─────────────────┴───────────┴───────────┘
UNIQUE constraint: (extended_property_id, content_type_id, object_id)
INDEX: (content_type_id, object_id) — fast lookup of all values for a given instance


nand_nand
┌────┬───────┬──────────────────┬───────────────┬─────┬────────────┬────────────┐
│ id │ name  │ capacity_per_die │ plane_per_die │ ... │ created_at │ updated_at │
├────┼───────┼──────────────────┼───────────────┼─────┼────────────┼────────────┤
│  1 │ BiCS8 │       1073741824 │             4 │     │ 2026-02-10 │ 2026-02-10 │
│  2 │ BiCS9 │       2147483648 │             6 │     │ 2026-02-10 │ 2026-02-10 │
└────┴───────┴──────────────────┴───────────────┴─────┴────────────┴────────────┘
Pure data — no config or extended_property columns.


nand_nandinstance
┌────┬─────────┬─────────┬─────────────────┬───────────────┬─────┬────────────┬────────────┐
│ id │ name    │ nand_id │ module_capacity │ user_capacity │ ... │ created_at │ updated_at │
├────┼─────────┼─────────┼─────────────────┼───────────────┼─────┼────────────┼────────────┤
│  1 │ 0.5T 7% │       1 │    549755813888 │  512110190592 │     │ 2026-02-10 │ 2026-02-10 │
│  2 │ 8T 28%  │       1 │   8796093022208 │ 6332740796416 │     │ 2026-02-10 │ 2026-02-10 │
└────┴─────────┴─────────┴─────────────────┴───────────────┴─────┴────────────┴────────────┘


nand_nandperf
┌────┬──────────┬─────────┬───────────┬─────────────────┬─────────┬─────────────────┬────────────┬────────────┐
│ id │ name     │ nand_id │ bandwidth │ module_capacity │ channel │ die_per_channel │ created_at │ updated_at │
├────┼──────────┼─────────┼───────────┼─────────────────┼─────────┼─────────────────┼────────────┼────────────┤
│  1 │ 4ch cfg  │       1 │    3200.0 │    549755813888 │       4 │               8 │ 2026-02-10 │ 2026-02-10 │
│  2 │ 2ch cfg  │       1 │    1600.0 │    549755813888 │       2 │              16 │ 2026-02-10 │ 2026-02-10 │
└────┴──────────┴─────────┴───────────┴─────────────────┴─────────┴─────────────────┴────────────┴────────────┘
Now uses BaseEntity — has name, created_at, updated_at.


cpu_cpu
┌────┬──────────────┬───────────┬────────────┬────────────┐
│ id │ name         │ bandwidth │ created_at │ updated_at │
├────┼──────────────┼───────────┼────────────┼────────────┤
│  1 │ Controller X │   12800.0 │ 2026-02-10 │ 2026-02-10 │
└────┴──────────────┴───────────┴────────────┴────────────┘


dram_dram
┌────┬────────┬───────────┬─────────┬───────────────┬────────────┬────────────┐
│ id │ name   │ bandwidth │ channel │ transfer_rate │ created_at │ updated_at │
├────┼────────┼───────────┼─────────┼───────────────┼────────────┼────────────┤
│  1 │ DDR5-A │   51200.0 │       2 │        6400.0 │ 2026-02-10 │ 2026-02-10 │
└────┴────────┴───────────┴─────────┴───────────────┴────────────┴────────────┘


results_resultprofile
┌────┬──────────────────┐
│ id │ name             │
├────┼──────────────────┤
│  1 │ AIPR Upper Bound │
│  2 │ AIPR Lower Bound │
│  3 │ Multi-plane Read │
└────┴──────────────────┘
UNIQUE constraint: name


results_resultworkload
┌────┬────────────┬──────┐
│ id │ name       │ type │
├────┼────────────┼──────┤
│  1 │ Host Write │    1 │
│  2 │ TLC Erase  │    3 │
│  3 │ GC Read    │    5 │
└────┴────────────┴──────┘


results_resultprofileworkload  (through model)
┌────┬────────────┬──────────────┬───────────────┬──────────────────────────┐
│ id │ profile_id │ workload_id  │ config_set_id │ extended_property_set_id │
├────┼────────────┼──────────────┼───────────────┼──────────────────────────┤
│  1 │ 1 (Upper)  │ 3 (GC Read)  │ NULL          │ 1 (GC Read / Upper)      │
│  2 │ 2 (Lower)  │ 3 (GC Read)  │ NULL          │ 2 (GC Read / Lower)      │
│  3 │ 1 (Upper)  │ 1 (Host Wr)  │ NULL          │ 3 (Host Write / Up)      │
└────┴────────────┴──────────────┴───────────────┴──────────────────────────┘
UNIQUE constraint: (profile_id, workload_id)
Same workload (GC Read) in different profiles -> different extended_property_sets.


results_resultrecord
┌────┬──────────────────────┬─────────┬──────────────────┬──────────┬─────────┬─────────┬────────────┬────────────┐
│ id │ name                 │ nand_id │ nand_instance_id │ nand_perf_id │ cpu_id  │ dram_id │ created_at │ updated_at │
├────┼──────────────────────┼─────────┼──────────────────┼──────────┼─────────┼─────────┼────────────┼────────────┤
│  1 │ BiCS8 + DDR5-A base  │       1 │                1 │        1 │       1 │       1 │ 2026-02-10 │ 2026-02-10 │
│  2 │ BiCS9 comparison     │       2 │             NULL │     NULL │       1 │       1 │ 2026-02-11 │ 2026-02-11 │
└────┴──────────────────────┴─────────┴──────────────────┴──────────┴─────────┴─────────┴────────────┴────────────┘
All hardware FKs nullable (SET_NULL on delete). Ordered by -created_at.


results_resultinstance
┌────┬──────────────────────┬─────────────────────────┬────────────┬────────────┐
│ id │ profile_workload_id  │ result_record_id   │ created_at │ updated_at │
├────┼──────────────────────┼─────────────────────────┼────────────┼────────────┤
│  1 │ 1 (GC Rd / Upper)    │ 1 (BiCS8 + DDR5-A)      │ 2026-02-10 │ 2026-02-10 │
│  2 │ 2 (GC Rd / Lower)    │ 1 (BiCS8 + DDR5-A)      │ 2026-02-10 │ 2026-02-10 │
│  3 │ 3 (Host Wr / Upper)  │ 1 (BiCS8 + DDR5-A)      │ 2026-02-10 │ 2026-02-10 │
│  4 │ 1 (GC Rd / Upper)    │ 2 (BiCS9 comparison)    │ 2026-02-11 │ 2026-02-11 │
└────┴──────────────────────┴─────────────────────────┴────────────┴────────────┘
UNIQUE constraint: (result_record_id, profile_workload_id)
No name — identified by the record + profile-workload pair.
Extended property values stored in properties_extendedpropertyvalue via GenericFK.
```

### Table summary

| Table | Rows scale with | Junction? |
|-------|----------------|-----------|
| `properties_propertyconfig` | Total unique properties across all model types | No |
| `properties_propertyconfigset` | Number of config sets (few per model type) | No |
| `properties_propertyconfigsetmembership` | Configs per set x number of sets | Yes (through) |
| `properties_extendedpropertyset` | Result profile-workload combos | No |
| `properties_extendedproperty` | Property definitions (entity + result) | No |
| `properties_extendedpropertyvalue` | Definitions x instances (heaviest table) | No |
| `nand_nand` | Number of NAND technologies | No |
| `nand_nandinstance` | Number of NAND SKUs | No |
| `nand_nandperf` | Number of perf test entries | No |
| `cpu_cpu` | Number of CPUs | No |
| `dram_dram` | Number of DRAMs | No |
| `results_resultprofile` | Number of result profiles | No |
| `results_resultworkload` | Number of workload types | No |
| `results_resultprofileworkload` | Profile x workload assignments | Yes (through) |
| `results_resultrecord` | Saved calculation runs | No |
| `results_resultinstance` | Records x profile-workloads | No |

Total junction/through tables: **2** (config set membership + profile workloads)

---

## API Response Shape

The API nests Nand fields into logical groups, even though the DB is flat.
Configs are optional — frontend requests them via query param.

### Example: `GET /api/nand/1/`

Data only — no configs, no extended properties:

```json
{
  "id": 1,
  "name": "BiCS8",
  "physical": {
    "capacity_per_die": 1073741824,
    "plane_per_die": 4,
    "block_per_plane": 2048,
    "d1_d2_ratio": 0.5,
    "page_per_block": 768,
    "slc_page_per_block": 256,
    "node_per_page": 16,
    "finger_per_wl": 4
  },
  "endurance": {
    "tlc_qlc_pe": 3000,
    "static_slc_pe": 100000,
    "table_slc_pe": 50000,
    "bad_block_ratio": 0.02
  },
  "raid": { "...": "..." },
  "mapping": { "...": "..." },
  "firmware": { "...": "..." },
  "journal": { "...": "..." },
  "pb_per_disk_by_channel": { "2": 100, "4": 200 },
  "created_at": "2026-02-10T00:00:00Z",
  "updated_at": "2026-02-10T00:00:00Z"
}
```

### Example: `GET /api/nand/1/?config_set=1&include=extended_properties`

With config set and per-instance extended property values:

```json
{
  "id": 1,
  "name": "BiCS8",
  "physical": { "...": "..." },
  "...": "...",
  "configs": {
    "set_id": 1,
    "set_name": "Nand Full View",
    "items": [
      { "id": 1, "index": 0, "name": "capacity_per_die", "display_text": "Cap/Die", "unit": "B" },
      { "id": 2, "index": 1, "name": "plane_per_die", "display_text": "Plane/Die" },
      { "id": 3, "index": 2, "name": "bandwidth", "display_text": "BW", "unit": "MB/s" }
    ]
  },
  "extended_properties": [
    { "id": 1, "name": "J per PU", "value": "=A1*B1", "is_formula": true },
    { "id": 2, "name": "Disk OP", "value": "=C1/D1", "is_formula": true }
  ]
}
```

> `extended_properties` here contains **per-instance values** for Nand #1 (BiCS8).
> Nand #2 (BiCS9) would return the same property names but potentially different values.

### Example: `GET /api/result-profiles/1/`

Result profile with workloads and result instances:

```json
{
  "id": 1,
  "name": "AIPR Upper Bound",
  "workloads": [
    {
      "id": 3,
      "name": "GC Read",
      "type": 5,
      "extended_property_definitions": [
        { "id": 3, "name": "Time", "is_formula": true },
        { "id": 4, "name": "Performance", "is_formula": true }
      ],
      "instances": [
        {
          "id": 1,
          "extended_properties": [
            { "property_id": 3, "name": "Time", "value": "=E1*F1", "is_formula": true },
            { "property_id": 4, "name": "Performance", "value": "=G1/H1", "is_formula": true }
          ]
        }
      ]
    },
    {
      "id": 1,
      "name": "Host Write",
      "type": 1,
      "extended_property_definitions": [
        { "id": 7, "name": "Time", "is_formula": true }
      ],
      "instances": [
        {
          "id": 3,
          "extended_properties": [
            { "property_id": 7, "name": "Time", "value": "=E2*F1", "is_formula": true }
          ]
        }
      ]
    }
  ]
}
```

### Config sets endpoint

```
GET /api/config-sets/?model=nand         → list all config sets for Nand
GET /api/config-sets/1/                  → get a specific set with its configs
POST /api/config-sets/                   → create a new set
```

### Serializer pattern

```python
# Example: cpu/serializers.py (entity-level — per-instance values)

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from properties.models import PropertyConfigSet, ExtendedPropertyValue
from cpu.models import Cpu


class CpuSerializer(serializers.ModelSerializer):
    configs = serializers.SerializerMethodField()
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = Cpu
        fields = "__all__"

    def get_configs(self, obj: Cpu) -> dict | None:
        config_set_id = self.context["request"].query_params.get("config_set")
        if not config_set_id:
            return None
        ct = ContentType.objects.get_for_model(Cpu)
        try:
            cs = PropertyConfigSet.objects.get(id=config_set_id, content_type=ct)
        except PropertyConfigSet.DoesNotExist:
            return None
        memberships = cs.memberships.select_related("config").all()
        return {
            "set_id": cs.id,
            "set_name": cs.name,
            "items": [
                {
                    "index": m.index,
                    **PropertyConfigSerializer(m.config).data,
                }
                for m in memberships
            ],
        }

    def get_extended_properties(self, obj: Cpu) -> list[dict] | None:
        if "extended_properties" not in self.context["request"].query_params.get("include", ""):
            return None
        # Per-instance values via GenericFK
        ct = ContentType.objects.get_for_model(Cpu)
        values = ExtendedPropertyValue.objects.filter(
            content_type=ct, object_id=obj.id
        ).select_related("extended_property")
        return [
            {
                "id": v.extended_property.id,
                "name": v.extended_property.name,
                "value": v.value,
                "is_formula": v.extended_property.is_formula,
            }
            for v in values
        ]
```

> Configs included only when `?config_set=<id>` is provided. Config definitions
> don't vary per instance — can be cached aggressively.
> Extended property **values** are per-instance, included only when
> `?include=extended_properties` is provided.

---

## Migration from Current Models

The current `Component` → `CpuComponent` / `DramComponent` multi-table hierarchy is
a sample implementation. The redesign replaces it entirely:

| Current | New | Action |
|---------|-----|--------|
| `components.Component` | `properties.base.BaseEntity` (abstract) | Drop table, use abstract mixin |
| `cpu.CpuComponent` | `cpu.Cpu` | New table, drop old |
| `dram.DramComponent` | `dram.Dram` | New table, drop old |
| _(none)_ | `properties.PropertyConfig` | New |
| _(none)_ | `properties.PropertyConfigSet` | New |
| _(none)_ | `properties.PropertyConfigSetMembership` | New (through model) |
| _(none)_ | `properties.ExtendedPropertySet` | New (result-level grouping) |
| _(none)_ | `properties.ExtendedProperty` | New (definition only, dual binding) |
| _(none)_ | `properties.ExtendedPropertyValue` | New (per-instance values via GenericFK) |
| _(none)_ | `nand.Nand` | New |
| _(none)_ | `nand.NandInstance` | New |
| _(none)_ | `nand.NandPerf` | New (uses BaseEntity) |
| _(none)_ | `results.ResultProfile` | New (renamed from ResultCategory) |
| _(none)_ | `results.ResultWorkload` | New |
| _(none)_ | `results.ResultProfileWorkload` | New (through model) |
| _(none)_ | `results.ResultRecord` | New (saved calculation runs with hardware FKs) |
| _(none)_ | `results.ResultInstance` | New (per record x profile-workload, no name) |

Since this is pre-production, a clean migration (drop old + create new) is fine.

---

## Resolved Questions

Previously open questions, now resolved:

| # | Question | Resolution |
|---|----------|------------|
| 1 | `usingSlcWriteCache` / `usingPmd` type | **Boolean** — keep `BooleanField` |
| 2 | ResultWorkload extended properties per category | **Per profile-workload** — `ResultProfileWorkload` through model with FK to `ExtendedPropertySet` |
| 3 | Integer vs UUID primary keys | **Integer** — confirmed acceptable |
| 4 | `pb_per_disk_by_channel` channel counts | **2 and 4 only** for now, JSONField keeps flexibility |
| 5 | Ratio fields range | **0-1 range** — added `MaxValueValidator(1.0)` to `d1_d2_ratio`, `data_vb_die_ratio`, `table_vb_good_die_ratio` |
| 6 | `NandPerf` without name | **Not intentional** — now uses `BaseEntity` (has name) |
| 7 | Formula evaluation | **Pure frontend** — backend stores only, no evaluation |
| 8 | ResultProfile rendering metadata | **Keep current placeholder** — `PropertyConfigSet` FK on `ResultProfileWorkload` stays as-is |

---

## Open Questions

None — all resolved.
