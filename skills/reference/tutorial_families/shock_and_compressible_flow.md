# Tutorial Family: Shock and Compressible Flow

## Use

Structural reference for `shockFluid` or compatible `fluid` cases only when thermo, energy, boundary-information and transient flux families match.

## Required match

Gas/thermo model, actual energy field, initial/static/total state, Mach regime, subsonic/supersonic boundary behavior, transient/Courant controls, shock-compatible schemes and geometry/domain.

## Reusable structure

Thermo dictionary layout, energy/pressure/velocity field patterns, transient controls, derived Mach/sampling patterns and shock-sensitive utility order may be referenced.

## Never copy blindly

Gas data, pressure/temperature/Mach values, shock angle/location, wedge/nozzle dimensions, far-field boundaries, flux/limiter settings, timestep or acceptance criteria.

## Evidence focus

Thermodynamic positivity/consistency, shock location and jump trends, conservation, mesh/timestep sensitivity, oscillations and applicable analytical/experimental comparisons.
