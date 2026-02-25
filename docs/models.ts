// ===================================================================
// ORIGINAL INTERFACES (kept for reference)
// ===================================================================

// // ----- Data models ----- //
//
// // Frontend use Cpu/Nand/Dram to generate performance result and show on a spreadsheet
//
// // This config helps frontend to handle rendering and contraint checking
// export interface PropertyConfig {
//     id: number;
//     index: number;
//     name: string;
//
//     displayText?: string;
//     description?: string;
//     readOnly?: boolean;
//     isExtended?: boolean;
//     isPrimary?: boolean;
//
//     isNumeric?: boolean;
//     subType?: string; // percent, byte, etc.
//     decimalPlace?: number;
//     unit?: string;
// }
//
// // For user to extend property without modify models.
// // All properties can be assigned as an Excel-compatible formula, for example:
// //   "=MIN([cpu.bandwidth],[nand-perf.seqWriteTlc])"
// // Frontend will link & evaluate these formulas and show proper result.
// export interface ExtendedProperty {
//     id: number;
//     name: string;
//     value: string | number;
//     isFormula: boolean;
//
//     configId: number;
//     config: PropertyConfig;
// }
//
// // BiCS8, BiCS9, etc.
// export interface Nand {
//     id: number;
//     name: string;
//
//     capacityPerDie: number;
//     planePerDie: number;
//     blockPerPlane: number;
//     d1D2Ratio: number;
//     pagePerBlock: number;
//     slcPagePerBlock: number;
//     nodePerPage: number;
//     tlcQlcPe: number;
//     staticSlcPe: number;
//     tableSlcPe: number;
//     badBlockRatio: number;
//     fingerPerWl: number;
//     dayPerYear: number;
//     powerCycleCount: number;
//     l2pUnit: number;
//     mappingTableSize: number;
//     p2lEntry: number;
//     maxDataRaidFrame: number;
//     maxSlcWcRaidFrame: number;
//     maxTableRaidFrame: number;
//     dataDieRaid: number;
//     tableDieRaid: number;
//     withP2l: number;
//     p2lBitmap: number;
//     defaultRebuildTime: number;
//     journalInsertTime: number;
//     driveLogRegionSize: number;
//     pbPerDiskWhen2Ch: number;
//     pbPerDiskWhen4Ch: number;
//     pfailMaxPlaneCount: number;
//     bolBlockNumber: number;
//     extraTableLifeForAlignSpec: number;
//     usingSlcWriteCache: number;
//     usingPmd: number;
//     minMappingOpWithPmd: number;
//     dataOpen: number;
//     dataOpenWithSlcWc: number;
//     dataGcDamperCentral: number;
//     driveLogMinOp: number;
//     minPfailVb: number;
//     smallTableVb: number;
//     journalEntrySize: number;
//     journalProgramUnit: number;
//     l2pEccData: number;
//     l2pEccSpare: number;
//     reservedLcaNumber: number;
//
//     configIds: number[];
//     configs: PropertyConfig[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }
//
// // 0.5T 7%, 8T 28%, etc.
// export interface NandInstance {
//     id: number;
//     name: string;
//
//     moduleCapacity: number;
//     userCapacity: number;
//     namespaceNum: number;
//     nsRemapTableUnit: number;
//     dataPcaWidth: number;
//     l2pWidth: number;
//     dataVbDieRatio: number;
//     pageNumPerRaidTag: number;
//     p2lNodePerDataP2lGroup: number;
//     dataP2lGroupNum: number;
//     tableVbGoodDieRatio: number;
//
//     nandId: number;
//     nand: Nand;
//     configsId: number[];
//     configs: PropertyConfig[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }
//
// export interface NandPerf {
//     id: number;
//     bandwidth: number;
//     moduleCapacity: number;
//
//     channel: number;
//     diePerChannel: number;
//
//     nandId: number;
//     nand: Nand;
//     configIds: number[];
//     configs: PropertyConfig[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }
//
// export interface Dram {
//     id: number;
//     name: string;
//
//     bandwidth: number;
//     channel: number;
//     transferRate: number;
//
//     configIds: number[];
//     configs: PropertyConfig[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }
//
// export interface Cpu {
//     id: number;
//     name: string;
//
//     bandwidth: number;
//
//     configIds: number[];
//     configs: PropertyConfig[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }
//
// export interface ResultCategory {
//     id: number;
//     name: string;
//
//     configId: number;
//     config: PropertyConfig;
// }
//
// export interface ResultWorkload {
//     id: number;
//     name: string;
//     type: number;
//
//     categoryIds: number[];
//     categories: ResultCategory[];
//     extendedPropertyIds: number[];
//     extendedProperties: ExtendedProperty[];
// }

// ===================================================================
// REDESIGNED INTERFACES (matches backend model-design.md)
// ===================================================================
//
// Key changes from original:
// - PropertyConfig: index removed (lives on PropertyConfigSetMembership)
// - ExtendedProperty: configId/config FK removed (linked by name convention)
// - Entity interfaces: configs/extendedProperties removed from model fields
//   — fetched via ContentType, returned as optional API response sections
// - pb_per_disk channels normalized to Record instead of separate fields
// - usingSlcWriteCache/usingPmd changed to boolean
// - ResultCategory renamed to ResultProfile
// - ResultWorkload: properties are per profile-workload pair, not per workload

// ----- Properties ----- //

export interface PropertyConfig {
    id: number;
    name: string;

    displayText?: string;
    description?: string;
    readOnly?: boolean;
    isExtended?: boolean;
    isPrimary?: boolean;

    isNumeric?: boolean;
    subType?: string; // percent, byte, etc.
    decimalPlace?: number;
    unit?: string;
}

/** A config with its display order within a specific set. */
export interface PropertyConfigWithIndex extends PropertyConfig {
    index: number;
}

/** Named collection of PropertyConfigs for a model type. */
export interface PropertyConfigSet {
    setId: number;
    setName: string;
    items: PropertyConfigWithIndex[];
}

/** Definition of an extended property (no value — values are per-instance). */
export interface ExtendedPropertyDefinition {
    id: number;
    name: string;
    isFormula: boolean;
    /** Fallback value for instances with no per-instance value record. null = no default defined. */
    defaultValue: unknown | null;
}

/** A per-instance value for an extended property. */
export interface ExtendedPropertyValue {
    propertyId: number; // FK to ExtendedPropertyDefinition.id
    name: string;
    value: string | number;
    isFormula: boolean;
}

export interface ExtendedPropertySet {
    setId: number;
    setName: string;
    definitions: ExtendedPropertyDefinition[];
}

// ----- Nand ----- //

/** Nand fields grouped logically for API response. */
export interface NandPhysical {
    capacityPerDie: number;
    planePerDie: number;
    blockPerPlane: number;
    d1D2Ratio: number;
    pagePerBlock: number;
    slcPagePerBlock: number;
    nodePerPage: number;
    fingerPerWl: number;
}

export interface NandEndurance {
    tlcQlcPe: number;
    staticSlcPe: number;
    tableSlcPe: number;
    badBlockRatio: number;
}

export interface NandRaid {
    maxDataRaidFrame: number;
    maxSlcWcRaidFrame: number;
    maxTableRaidFrame: number;
    dataDieRaid: number;
    tableDieRaid: number;
}

export interface NandMapping {
    l2pUnit: number;
    mappingTableSize: number;
    p2lEntry: number;
    withP2l: number;
    p2lBitmap: number;
    l2pEccData: number;
    l2pEccSpare: number;
    reservedLcaNumber: number;
}

export interface NandFirmware {
    dayPerYear: number;
    powerCycleCount: number;
    defaultRebuildTime: number;
    driveLogRegionSize: number;
    driveLogMinOp: number;
    usingSlcWriteCache: boolean;
    usingPmd: boolean;
    minMappingOpWithPmd: number;
    dataOpen: number;
    dataOpenWithSlcWc: number;
    dataGcDamperCentral: number;
    minPfailVb: number;
    smallTableVb: number;
    pfailMaxPlaneCount: number;
    bolBlockNumber: number;
    extraTableLifeForAlignSpec: number;
}

export interface NandJournal {
    journalInsertTime: number;
    journalEntrySize: number;
    journalProgramUnit: number;
}

/** API response for GET /api/nand/:id/?config_set=N&include=extended_properties */
export interface Nand {
    id: number;
    name: string;
    physical: NandPhysical;
    endurance: NandEndurance;
    raid: NandRaid;
    mapping: NandMapping;
    firmware: NandFirmware;
    journal: NandJournal;
    pbPerDiskByChannel: Record<string, number>; // e.g. {"2": 100, "4": 200}
    createdAt: string;
    updatedAt: string;

    // Optional — included when requested via query params
    configs?: PropertyConfigSet;
    extendedProperties?: ExtendedPropertyValue[];
}

export interface NandInstance {
    id: number;
    name: string;
    nandId: number;

    moduleCapacity: number;
    userCapacity: number;
    namespaceNum: number;
    nsRemapTableUnit: number;
    dataPcaWidth: number;
    l2pWidth: number;
    dataVbDieRatio: number;
    pageNumPerRaidTag: number;
    p2lNodePerDataP2lGroup: number;
    dataP2lGroupNum: number;
    tableVbGoodDieRatio: number;

    createdAt: string;
    updatedAt: string;

    configs?: PropertyConfigSet;
    extendedProperties?: ExtendedPropertyValue[];
}

export interface NandPerf {
    id: number;
    name: string;
    nandId: number;

    bandwidth: number;
    moduleCapacity: number;
    channel: number;
    diePerChannel: number;

    createdAt: string;
    updatedAt: string;

    configs?: PropertyConfigSet;
    extendedProperties?: ExtendedPropertyValue[];
}

// ----- Cpu / Dram ----- //

export interface Cpu {
    id: number;
    name: string;
    bandwidth: number;
    createdAt: string;
    updatedAt: string;

    configs?: PropertyConfigSet;
    extendedProperties?: ExtendedPropertyValue[];
}

export interface Dram {
    id: number;
    name: string;
    bandwidth: number;
    channel: number;
    transferRate: number;
    createdAt: string;
    updatedAt: string;

    configs?: PropertyConfigSet;
    extendedProperties?: ExtendedPropertyValue[];
}

// ----- Results ----- //

/** Renamed from ResultCategory. */
export interface ResultProfile {
    id: number;
    name: string; // AIPR Upper Bound, AIPR Lower Bound, Multi-plane Read, etc.
    workloads: ResultProfileWorkloadEntry[];
}

export interface ResultWorkload {
    id: number;
    name: string; // Host Write, TLC Erase, GC Read, etc.
    type: number;
}

/** A workload's appearance within a profile, with per-appearance property definitions. */
export interface ResultProfileWorkloadEntry {
    id: number;
    name: string;
    type: number;
    configs?: PropertyConfigSet;
    extendedPropertyDefinitions?: ExtendedPropertyDefinition[];
    instances?: ResultInstance[];
}

/** A specific result entry — one per profile-workload per calculation record. */
export interface ResultInstance {
    id: number;
    extendedProperties: ExtendedPropertyValue[];
    createdAt: string;
    updatedAt: string;
}

/** A saved result record with hardware inputs and produced results. */
export interface ResultRecord {
    id: number;
    name: string;

    // Hardware inputs (all optional)
    nandId?: number;
    nandInstanceId?: number;
    nandPerfId?: number;
    cpuId?: number;
    dramId?: number;

    resultInstances?: ResultInstance[];
    createdAt: string;
    updatedAt: string;
}
