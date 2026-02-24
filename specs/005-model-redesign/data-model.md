# Data Model: Backend Model Redesign

**Feature**: 005-model-redesign
**Date**: 2026-02-23
**Source**: `docs/005-model-redesign/model-design.md` (canonical reference for all field definitions)

This document summarizes entities, relationships, and constraints. For full field lists and code, see `docs/005-model-redesign/model-design.md`.

## Entity Relationship Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────────┐
│  PropertyConfig  │────┤ PropertyConfigSet  │────┤ PropertyConfigSetMembership│
│  (content_type)  │    │  (content_type)    │    │  (config_set, config, idx) │
└─────────────────┘     └──────────────────┘     └──────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────────┐
│ExtendedPropertySet│────┤ ExtendedProperty   │────┤  ExtendedPropertyValue    │
│  (content_type)   │    │ (ct OR prop_set)   │    │  (ext_prop, ct, obj_id)   │
└──────────────────┘     └──────────────────┘     └──────────────────────────┘
                                                         │ GenericFK to:
                              ┌───────────────────────────┤
                              ▼           ▼         ▼     ▼          ▼           ▼
                           ┌─────┐  ┌──────────┐ ┌────┐ ┌────┐ ┌────────┐ ┌──────────────┐
                           │Nand │  │NandInst. │ │Nand│ │Cpu │ │ Dram   │ │ResultInstance│
                           │     │  │          │ │Perf│ │    │ │        │ │              │
                           └─────┘  └──────────┘ └────┘ └────┘ └────────┘ └──────────────┘
                              │          │           │                           │
                              │ FK       │ FK        │ FK                        │ FK
                              ▼          ▼           ▼                           ▼
                           ┌─────┐                                    ┌──────────────────┐
                           │Nand │                                    │ResultProfileWkld │
                           └─────┘                                    │(profile, wkld)   │
                                                                      └──────────────────┘
                                                                         │ FK        │ FK
                                                                         ▼            ▼
                                                                  ┌───────────┐ ┌──────────┐
                                                                  │ResultProf.│ │ResultWkld│
                                                                  └───────────┘ └──────────┘

┌──────────────┐ ──FK(SET_NULL)──▶ Nand, NandInstance, NandPerf, Cpu, Dram
│ ResultRecord  │
│  (BaseEntity) │ ◀──FK── ResultInstance (result_record)
└──────────────┘
```

## Entities Summary

| Entity | App | Base | Key Fields | Constraints |
|--------|-----|------|------------|-------------|
| BaseEntity | properties | abstract | name, created_at, updated_at | — |
| PropertyConfig | properties | Model | content_type, name, display_text, unit, ... | UNIQUE(content_type, name) |
| PropertyConfigSet | properties | Model | content_type, name | UNIQUE(content_type, name) |
| PropertyConfigSetMembership | properties | Model | config_set, config, index | UNIQUE(set,config), UNIQUE(set,index) |
| ExtendedPropertySet | properties | Model | name, content_type(nullable) | — |
| ExtendedProperty | properties | Model | content_type OR property_set, name, is_formula | UNIQUE(ct,name) WHERE ct, UNIQUE(set,name) WHERE set, CHECK(exactly one binding) |
| ExtendedPropertyValue | properties | Model | extended_property, content_type, object_id, value | UNIQUE(prop,ct,obj_id), INDEX(ct,obj_id) |
| Nand | nand | BaseEntity | ~45 fields (physical, endurance, raid, mapping, firmware, journal, channel JSON) | — |
| NandInstance | nand | BaseEntity | nand(FK), module_capacity, user_capacity, ... | UNIQUE(nand, name) |
| NandPerf | nand | BaseEntity | nand(FK), bandwidth, module_capacity, channel, die_per_channel | — |
| Cpu | cpu | BaseEntity | bandwidth | — |
| Dram | dram | BaseEntity | bandwidth, channel, transfer_rate | — |
| ResultProfile | results | Model | name | UNIQUE(name) |
| ResultWorkload | results | Model | name, type | — |
| ResultProfileWorkload | results | Model | profile(FK), workload(FK), config_set(FK null), ext_prop_set(FK null) | UNIQUE(profile, workload) |
| ResultRecord | results | BaseEntity | nand(FK null), nand_instance(FK null), nand_perf(FK null), cpu(FK null), dram(FK null) | ordering: -created_at |
| ResultInstance | results | Model | profile_workload(FK), result_record(FK), created_at, updated_at | UNIQUE(result_record, profile_workload) |

## Key Relationships

1. **Nand → NandInstance** (1:N, CASCADE)
2. **Nand → NandPerf** (1:N, CASCADE)
3. **ResultProfile ↔ ResultWorkload** (M:N via ResultProfileWorkload)
4. **ResultRecord → hardware** (nullable FKs, SET_NULL)
5. **ResultRecord → ResultInstance** (1:N, CASCADE)
6. **ExtendedProperty → ExtendedPropertyValue** (1:N, CASCADE)
7. **ExtendedPropertyValue → any entity** (GenericFK, no DB cascade)

## Validation Rules

- Ratio fields (d1_d2_ratio, data_vb_die_ratio, table_vb_good_die_ratio): MaxValueValidator(1.0)
- usingSlcWriteCache, usingPmd: BooleanField (not integer)
- pb_per_disk_by_channel: JSONField, application-level validation for numeric values
- ExtendedProperty: CHECK constraint ensures exactly one of content_type/property_set is non-null
- PropertyConfigSetMembership: unique (set, config) AND unique (set, index)
