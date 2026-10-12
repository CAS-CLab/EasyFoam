# Tutorial Family: Free-Surface / Interface-Capturing Flow

## Use

Structural reference for `incompressibleVoF` cases with matching phase model, phase count, transient algorithm and interface treatment.

## Required match

Explicit phase names/properties, gravity/surface tension, pressure convention, initial interface, phase BCs, interface schemes/compression, phase Courant policy and mesh resolution.

## Reusable structure

Placement of phase/property dictionaries, actual phase-field family patterns, transient PIMPLE controls, interface-related schemes/solvers, gravity setup and phase diagnostics may be referenced after name/model verification.

## Never copy blindly

Phase names (`water`, `air`, etc.), properties, surface tension, gravity direction, initial interface geometry, timestep/end time, patch conditions, mesh/domain or boundedness criteria.

## Evidence focus

Phase bounds/sum, phase volume/mass balance, interface motion, timestep/Courant behavior, mesh resolution at the interface and requested wave/bubble/free-surface QoIs.
