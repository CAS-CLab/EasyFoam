# Tutorial Family: Multicomponent / Reacting Flow

## Use

Structural reference only when the species, mixture, thermo, energy and optional reaction model families match the selected `multicomponentFluid` contract.

## Required match

Actual species inventory and closure, thermophysical package, energy variable, reaction/chemistry data, boundary compositions, flow algorithm, source/ignition behavior and numerical stiffness.

## Reusable structure

Species solver/scheme grouping, mixture/thermo/reaction dictionary placement, composition boundary patterns and relevant functionObjects may be reused after exact name/model audit.

## Never copy blindly

Species names, kinetic/thermo data, inlet mixtures, temperatures, reaction rates, source terms, timestep, ignition, turbulence–chemistry interaction or validation criteria.

## Evidence focus

Species bounds/sum, mass/energy/reaction balance, temperature/heat release, convergence/stiffness behavior, flame/reaction-zone resolution and requested profiles/integrals.
