# OpenFOAM-13 Solver Module Map

Use this map only to identify candidate module cards. The selected card and local OpenFOAM-13 runtime remain authoritative.

| Physical family | Candidate module | Common legacy lineage | Algorithm notes |
| --- | --- | --- | --- |
| Single-phase incompressible | `incompressibleFluid` | `simpleFoam`, `pisoFoam`, `pimpleFoam` | SIMPLE for steady; PISO/PIMPLE for transient as supported |
| Incompressible interface-capturing multiphase | `incompressibleVoF` | `interFoam` family | Usually transient PIMPLE; actual phase names required |
| General thermal/compressible pressure-based fluid | `fluid` | `rhoSimpleFoam`, `rhoPimpleFoam` family | Actual energy variable and thermophysical model required |
| Shock-oriented compressible flow | `shockFluid` | density-based shock solver lineage | Transient shock-capturing controls required |
| Multicomponent/species fluid | `multicomponentFluid` | reacting/multicomponent lineage | Actual species inventory and reaction/mixture model required |

Do not use the map to infer field names, model dictionaries, or boundary values. A legacy name is explanatory lineage; execution must follow the selected OpenFOAM-13 module/application contract.
