# CFD Physics Taxonomy

Use this card before selecting an OpenFOAM module. Classification is ordered because an early physical choice changes later fields, dictionaries, algorithms, and validation.

## Classification order

1. **Phase regime** — single continuum, interface-capturing multiphase, dispersed multiphase, Lagrangian particles, or coupled regions.
2. **Compressibility** — incompressible, low-Mach with thermal-density effects, or compressible.
3. **Energy and composition** — isothermal, energy-coupled, species transport, reaction, combustion, or phase change.
4. **Time behavior** — steady physical model, transient physical model, or steady target solved by pseudo-time/iteration.
5. **Turbulence treatment** — laminar, RAS, LES, DNS, or unresolved pending user/reference decision.
6. **Motion** — static, MRF, prescribed moving mesh, dynamic mesh, overset, rigid-body, or topology change.
7. **Body/source terms** — gravity, buoyancy, surface tension, porous resistance, heat/mass/momentum sources, actuator regions.
8. **Geometry and mesh source** — simple parametric, surface/CAD, imported mesh, existing case, or missing.

## Decision notes

- A solver name is evidence of user intent, not a substitute for this classification.
- “Steady” does not automatically imply incompressible or SIMPLE; “transient” does not by itself select PISO or PIMPLE.
- “Thermal” does not identify the solved energy variable. The selected module and thermophysical model determine whether the formal field is `T`, `h`, `e`, or another supported variable.
- “Multiphase” is insufficient without the phase model, phase names, material properties, interface treatment, and required phase fields.
- “Turbulent” is insufficient without simulation type and model compatibility. Keep `simulationType` separate from the model name.
- MRF is a stationary-mesh rotating-frame model and requires an actual cellZone; it is not equivalent to moving mesh.

## Typical consequences

| Classification | Consequences to resolve |
| --- | --- |
| Incompressible single-phase | pressure convention, `U`, pressure field family, transport and turbulence contract |
| Compressible/thermal | thermophysical package, energy variable, density/pressure relation, temperature/enthalpy BCs |
| VoF/interface capturing | explicit phase names, phase fraction fields, surface tension, interface compression, boundedness |
| Species/reacting | species inventory, inert/default species, reaction/chemistry data, energy coupling |
| LES/DNS | transient requirement, filter/grid adequacy, timestep/Courant limits, statistics duration |
| MRF/rotating machinery | exact rotating zone, rotation axis/origin/speed, stationary/rotating interfaces |
| Buoyancy | gravity vector, density model, reference state, thermal BCs and hydrostatic pressure convention |

## Blocking conditions

Block Plan when a missing classification changes the module, solved fields, material model, boundary conditions, mesh zones, formal run controls, or requested evidence. Record non-decisive uncertainty explicitly rather than forcing a false category.
