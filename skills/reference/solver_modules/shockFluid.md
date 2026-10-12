# `shockFluid` Module Card

## Intended family

Compressible flows requiring shock-oriented transient flux treatment and thermodynamic fields. Exact equations and fields must be confirmed from the local Foundation v13 module.

## Planning contract

Resolve:

- gas/thermophysical model and actual energy variable;
- initial/inlet/outlet/far-field thermodynamic state;
- Mach or equivalent regime and reference frame;
- transient physical time and acoustic/Courant constraints;
- shock-compatible flux, limiter and boundary treatment;
- geometry/domain placement and shock-sensitive mesh resolution;
- wall thermal/slip/no-slip intent and requested shock/QoI evidence.

## Typical file families

Velocity, pressure, density/thermodynamic and actual energy fields; thermophysical and momentum-transport dictionaries; transient `fvSchemes`, `fvSolution`, `controlDict`; geometry/mesh dictionaries and derived quantities such as Mach number when requested.

## Compatibility checks

- initial/boundary states are thermodynamically consistent;
- supersonic/subsonic information flow is reflected in BCs;
- energy/thermo fields and solver entries agree;
- mesh resolves shock location and key gradients sufficiently for the claim;
- timestep/Courant and flux treatment are appropriate;
- outlet/domain boundaries do not contaminate the shock/QoI.

## Frequent failures

Missing thermo entries, wrong energy field, nonphysical temperature/density, incompatible static/total conditions, excessive Courant number, oscillatory/unbounded shock, under-resolved geometry, or interpreting numerical shock thickness as physical diffusion.

## Must not guess

Gas model/properties, pressure/temperature state, Mach/reference quantities, shock angle/location criterion, wall thermal treatment or validation tolerance.
