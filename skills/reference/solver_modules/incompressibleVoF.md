# `incompressibleVoF` Module Card

## Intended family

Incompressible interface-capturing multiphase flow using explicit phase-fraction fields. These cases are normally transient and require bounded interface transport.

## Legacy lineage

The `interFoam` family is common explanatory lineage. Use the current Foundation v13 module/dictionary contract, not historical file names by memory.

## Planning contract

Resolve:

- explicit phase names and number of phases;
- density, viscosity and other phase properties;
- surface tension and interface model;
- gravity and coordinate direction when applicable;
- initial interface/phase distribution;
- actual phase-fraction field names;
- pressure convention/reference and velocity/phase BCs;
- PIMPLE/transient controls, `maxCo`/phase Courant policy;
- requested interface/phase-volume QoIs.

## Typical file families

Velocity, pressure-like and actual phase-fraction fields; phase/transport properties; gravity when active; interface-compatible `fvSchemes`, `fvSolution` and runtime controls.

## Compatibility checks

- phase names agree across dictionaries, fields, BCs and postprocessing;
- phase fractions are initialized and bounded consistently;
- inlet/outlet phase conditions are physically meaningful, including backflow;
- surface tension/gravity units and direction are correct;
- interface compression and flux schemes cover actual phase fields;
- mesh/timestep resolve the interface dynamics intended by the claim.

## Frequent failures

Assumed `alpha.water`, missing phase properties, unbounded phase fraction, inconsistent pressure convention, wrong gravity direction, absent phase-field solver/scheme, outlet phase instability, or interface initialized outside the intended geometry.

## Evidence

Assess phase bounds and volume, Courant controls, mass conservation, interface location/evolution, mesh resolution near interface and requested QoIs. A visually sharp interface is not sufficient validation.
