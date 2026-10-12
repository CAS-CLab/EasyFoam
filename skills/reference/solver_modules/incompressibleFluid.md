# `incompressibleFluid` Module Card

## Intended family

Single-phase incompressible flow with constant or modelled transport properties. It may support steady or transient pressure–velocity coupling depending on the selected algorithm and case dictionaries.

## Legacy lineage

Common explanatory lineage includes `simpleFoam`, `pisoFoam`, and `pimpleFoam`. Do not execute a legacy name unless the active Foundation v13 installation explicitly supports that workflow; prefer `foamRun -solver incompressibleFluid` when selected.

## Planning contract

Resolve:

- steady/transient physical intent;
- SIMPLE/PISO/PIMPLE agreement;
- laminar/RAS/LES treatment and model;
- viscosity/transport model and value(s);
- pressure convention/reference requirement;
- actual turbulence/model fields;
- motion, buoyancy or source extensions;
- formal controls and requested QoIs.

## Typical file families

- actual velocity and pressure-like field files;
- transport/physical properties and momentum-transport configuration;
- gravity, MRF/motion, source/constraint files only when active;
- `controlDict`, `fvSchemes`, `fvSolution` and required mesh/functionObject dictionaries.

Exact field and dictionary names must follow the local module/model contract.

## Compatibility checks

- no compressible thermophysical behavior is being requested under an incompressible assumption;
- pressure/velocity boundaries are well posed and reference treatment is explicit;
- wall/turbulence conditions agree with model and mesh resolution;
- steady/transient controls and algorithm block agree;
- every active field has schemes and linear solver coverage.

## Frequent failures

Missing transport/momentum model, singular pressure system, omitted turbulence field, field–patch mismatch, wrong algorithm block, unstable outlet/backflow, or numerics used to hide poor mesh/BCs.

## Evidence and claim limits

Collect static contract, mesh, formal run, residual/conservation, QoI and physical evidence. Execution alone does not establish incompressible-model appropriateness, convergence or mesh independence.
