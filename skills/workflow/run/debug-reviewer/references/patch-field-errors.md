# Patch and Field Errors

Typical messages include unknown patch, missing boundary entry, incompatible patch type, wrong field class/dimensions, or required field not found.

## Diagnosis order

1. Read actual mesh boundary/region inventory.
2. Compare exact names with every field boundary block and consuming dictionary.
3. Confirm mesh patch type versus field condition semantics.
4. Confirm actual solved/model field inventory for the selected module.
5. Check dimensions, class, region and initial-time location.
6. Check coupled pair, phase/species/turbulence/wall requirements.

## Common root causes

Mesh regenerated/imported with different names, generic placeholder fields, omitted model fields, wrong energy/phase/species name, stale field files after region changes, or CaseSpec not reconciled with actual mesh.

## Routing

Patch/zone topology or naming producer defect → mesh specialist. Field file/BC defect → case-authoring. Missing decisive physical boundary/model information → Plan.
