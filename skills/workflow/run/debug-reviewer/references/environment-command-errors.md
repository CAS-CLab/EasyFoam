# Environment and Command Errors

These remain in Run when the formal case does not need modification.

## Failure classes

- OpenFOAM environment not sourced or wrong version active;
- module/application/utility absent;
- invalid command flags or argument order;
- working directory/case path incorrect;
- permission, disk-space, file-system or symlink issue;
- MPI launcher/library/rank failure;
- decomposed/reconstructed state mismatch;
- process interruption or resource exhaustion.

## Diagnosis

Record environment/version evidence, exact argv/cwd, executable discovery, return code and first stderr/log error. Compare command form with the active local installation rather than guessing historical syntax.

## Recovery

Correct invocation/environment in the attempt configuration and rerun the same formal case hash. Do not modify dictionaries merely to work around a missing executable or wrong environment. Resource limitations may block rather than fail the CFD contract.
