# `blockMesh` Rules

Use `blockMesh` for genuinely block-constructible structured or multi-block domains and for explicitly approved background domains.

## Required contract

- coordinate system, units/scale, vertex coordinates, block topology and orientation;
- cell counts and grading in each direction;
- boundary faces grouped into exact patch names and mesh types;
- merge/cyclic/wedge/empty relationships when applicable;
- intended dimensionality and characteristic resolution.

## Experience rules

- Check vertex ordering and positive cell orientation before tuning quality.
- Shared block faces must be topologically conformal unless a supported interface is intended.
- Grading transitions should resolve boundary layers/features without extreme adjacent-cell jumps.
- Two-dimensional cases require one-cell thickness and correct `empty` patches; wedge cases require consistent wedge geometry.
- Periodic/cyclic faces require compatible geometry and pairing.
- Do not approximate a complex named body with a box and claim fidelity.

## Validation

Run `blockMesh`, inspect the actual boundary/zone inventory, then run `checkMesh`. Visual inspection of block topology is recommended for multi-block, wedge, cyclic, or highly graded meshes.
