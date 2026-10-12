# Dictionary and Keyword Errors

Dictionary errors are usually Write-stage defects even when discovered during Run.

## Common causes

- missing required file or object;
- wrong file location/region;
- malformed braces, lists, dimensions or token type;
- unsupported legacy keyword/dictionary family;
- wrong model subdictionary for selected module;
- duplicate/conflicting entries;
- missing include or unresolved macro/reference;
- object/header name mismatch;
- required field solver/scheme entry absent.

## Diagnosis

1. Identify the reader, file and keyword from the first error.
2. Confirm selected OpenFOAM-13 module/model and expected dictionary family.
3. Inspect the smallest relevant Reference or local working tutorial pattern.
4. Check cross-file dependencies and actual names.
5. Apply the minimal correction; do not add unrelated fallback dictionaries.
6. Re-run the failing parser/preprocessing/solver startup command.

## Experience rules

A parser accepting syntax does not prove semantic compatibility. A missing entry may reflect an earlier wrong module/model choice, so route to Plan when the physical contract itself is unresolved.
