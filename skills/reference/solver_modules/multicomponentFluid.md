# `multicomponentFluid` Module Card

## Intended family

Fluid workflows with multiple transported species/composition fields and optional reaction/combustion/thermal coupling. Actual support and dictionary structure must be confirmed from the local Foundation v13 installation.

## Planning contract

Resolve:

- actual species names and ordering;
- inert/default species and closure rule;
- mixture, diffusion/transport, thermo and equation-of-state models;
- reaction/chemistry/combustion models and data when active;
- actual energy variable and thermal coupling;
- species initial/boundary compositions and normalization;
- source terms, ignition or reaction controls;
- steady/transient algorithm and stiffness/timestep implications.

## Typical file families

Velocity/pressure/thermodynamic fields, actual species fields, mixture/thermo/transport and optional reaction/chemistry dictionaries, momentum transport, system schemes/solvers for every active equation, and formal runtime controls.

## Compatibility checks

- every configured species has the required field/solver/scheme/BC coverage;
- mass fractions/compositions satisfy closure and physical bounds;
- thermo/reaction data refer to the same species inventory;
- energy and heat-release coupling are consistent;
- inlet mixtures and wall/outlet conditions are physically defined;
- stiffness and timestep/solver settings are defensible.

## Frequent failures

Literal `Yi` placeholder, missing `YiFinal`-family coverage, inconsistent species lists, absent thermo/reaction data, non-normalized inlet composition, negative mass fractions, wrong energy field, or a parser-valid but physically incompatible chemistry package.

## Evidence

Assess species boundedness/sum, mass and elemental/reaction balance where possible, temperature/heat release, conservation, convergence and requested species/QoI profiles. Solver completion alone does not validate chemistry.
