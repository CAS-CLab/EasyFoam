# Mesh Format Conversion Guidance

Select a converter from the actual source format and locally available OpenFOAM-13 utilities. Confirm syntax from the active installation rather than guessing an executable name.

## Before conversion

Identify element types/order, regions, boundary groups, zones, units, coordinate convention, and whether the source represents a surface or volume mesh. Surface formats require a meshing route, not a volume-mesh converter.

## Conversion controls

- use explicit scaling when units differ;
- preserve region and boundary group names where supported;
- document any renaming or type mapping;
- reject unsupported elements or know how they are downgraded;
- avoid destructive cleanup of the source artifact;
- keep actual converter stdout/stderr when the command runs.

## After conversion

Compare bounds/counts with the source, inspect patch/region/zone inventory, verify coupled interfaces and dimensionality, run `checkMesh`, and reconcile CaseSpec/model consumers. If essential metadata was lost, stop for a mapping decision rather than inventing names.
