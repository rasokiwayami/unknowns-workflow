# WO-5b Implementation Notes

## Deviations

### D1: Resolved containment did not reject in-root symlinks

- Expected (plan): resolved-path containment would provide the required path safety.
- Found (territory): in-root file and directory symlinks stayed contained while still violating the no-symlink contract; graph storage paths could also follow symlinks.
- Chosen conservative option: reject symlinks in caller-selected fingerprint components and graph root, evidence directory, stream, and lock paths before access.
- Why conservative: it fails closed without dereferencing caller-controlled storage aliases.
- Follow-up needed: no; characterization tests cover the discovered boundaries.
