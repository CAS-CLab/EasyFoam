# Tutorial Pattern Index Format

The tutorial index is read-only metadata used to locate candidate structural references.

Each entry should contain:

```yaml
id: stable-pattern-id
openfoam_version: Foundation-v13
path: relative/local/tutorial/path
module_or_application: incompressibleFluid
algorithm: PIMPLE
physics_tags: [incompressible, transient, single_phase]
dictionary_family: [physicalProperties, momentumTransport]
mesh_tags: [blockMesh]
feature_tags: [probes]
required_files: [system/controlDict, system/fvSolution]
notes: concise applicability limits
```

## Index rules

- Use relative or logical paths; do not store machine-specific absolute paths.
- Index only locally confirmed patterns.
- Keep version and module lineage explicit.
- Tags support retrieval but do not establish compatibility.
- Do not store copied case answers, user data, or generated Workflow results.
- Update the index only through explicit Evolution when the knowledge itself changes.
