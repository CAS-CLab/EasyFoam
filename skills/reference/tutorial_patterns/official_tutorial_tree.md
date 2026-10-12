# Official Tutorial Tree Index

This index is generalized from the official OpenFOAM-13 `tutorials/` tree. It intentionally records module and pattern categories only. Concrete tutorial case names are not listed.

## Generic Directory Grammar

```text
tutorials/
  <solver-or-physics-module>/
    <tutorial-case>/
      0/ or <time-directory>/
      constant/
      system/
      Allrun, Allclean, Allmesh, or related run helpers
```

Common file-category grammar:

```text
0/ or <time-directory>:
  field initial and boundary-condition files

constant/:
  physicalProperties, phaseProperties, momentumTransport,
  thermophysical/combustion/model dictionaries, dynamicMeshDict,
  polyMesh or triSurface resources when applicable

system/:
  controlDict, fvSchemes, fvSolution, blockMeshDict,
  decomposeParDict, setFieldsDict, snappyHexMeshDict,
  fvModels, fvConstraints, mesh and postprocess dictionaries
```

## Official Top-Level Tutorial Modules

- `XiFluid`
- `compressibleMultiphaseVoF`
- `compressibleVoF`
- `film`
- `fluid`
- `incompressibleDenseParticleFluid`
- `incompressibleDriftFlux`
- `incompressibleFluid`
- `incompressibleMultiphaseVoF`
- `incompressibleVoF`
- `isothermalFilm`
- `isothermalFluid`
- `legacy`
- `mesh`
- `movingMesh`
- `multiRegion`
- `multicomponentFluid`
- `multiphaseEuler`
- `potentialFoam`
- `resources`
- `shockFluid`
- `solidDisplacement`

## Generalized Pattern Families

- incompressible pressure-velocity flow: `0/`, `constant/physicalProperties`, `constant/momentumTransport`, `system/controlDict`, `system/fvSchemes`, `system/fvSolution`
- free-surface or interface-capturing flow: phase fields, `constant/phaseProperties`, `system/setFieldsDict`, bounded transport and interface controls
- compressible or shock flow: pressure, velocity, thermodynamic fields, thermophysical or physical-property dictionaries, transient stability controls
- multicomponent or combustion flow: species/progress variables, chemistry or combustion dictionaries, coupled scalar/flow solver controls
- Eulerian multiphase flow: phase models, multiple phase fields, interphase closure dictionaries, boundedness checks
- film flow: surface-film fields and film physical-property dictionaries coupled to a parent flow or surface region
- moving mesh: `constant/dynamicMeshDict`, mesh-motion fields or constraints, mesh update controls
- multi-region flow and heat transfer: region-scoped `0/`, `constant/`, and `system/` dictionaries with coupled region controls
- mesh-only workflows: `blockMeshDict`, `snappyHexMeshDict`, `surfaceFeaturesDict`, `meshQualityDict`, and import/conversion dictionaries
- solid displacement: solid field files, mechanical properties, displacement solution controls
- potential-flow initialization: potential-flow fields and minimal system controls for initialization or preprocessing

## Use Rules

Workflow Plan may use this file to choose a tutorial pattern category, then read the minimal solver module and family cards. Workflow must not infer case-specific dimensions, boundary values, material constants, or numerical controls from this generalized index.
