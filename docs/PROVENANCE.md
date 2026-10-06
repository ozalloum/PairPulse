# Package provenance

This repository snapshot was prepared on 6 October 2026 from the author's
`PairPulse_reproducibility_package` supplied for the PairPulse manuscript.
The original source folder was left unchanged.

## Original checksum audit

The supplied checksum manifest is preserved as
[ORIGINAL_CHECKSUMS.sha256](ORIGINAL_CHECKSUMS.sha256). The initial audit is
preserved as [original_checksum_audit.json](original_checksum_audit.json).
Of its 42 entries, 36 matched at import. Five existing files differed:

- `manuscript/pairpulse.tex`
- `results/figure4_reproducibility_structure.pdf`
- `results/figure5_computational_workflow.pdf`
- `results/figure5_computational_workflow.png`
- `scripts/make_reproducibility_figures.py`

The sixth discrepancy was an absent
`results/figure4_reproducibility_structure.png`. The author subsequently
supplied this PNG, and it is included in the repository snapshot. The initial
audit intentionally retains its original missing-file result.

These discrepancies record differences from the earlier manifest; they do
not identify which version is scientifically correct. The supplied solver
code, numerical CSVs, run metadata, manuscript source and manuscript PDF were
preserved. Repository preparation did not rebuild the manuscript or establish
that its PDF corresponds to the latest source and figures.

## Repository preparation

Preparation added citation metadata, a data guide, dependency-version pins,
Git ignore/attribute files, and a standard-library checksum verifier. The
README now documents Windows setup and regeneration into a separate output
folder. No numerical solver or reproduction-script changes were made.

The root `CHECKSUMS.sha256` describes this prepared snapshot and supersedes
the earlier manifest for file-integrity checks. Verify it before modifying
files, using `python scripts/verify_checksums.py` from the repository root.
Fresh computations and plots are not expected to match every original byte:
floating-point libraries, fonts, PDF metadata and runtime measurements can
vary. Check numerical agreement separately from file integrity.

The bundled manuscript and submission notes describe the pre-release
package and may contain repository/DOI placeholders. No DOI or journal
acceptance is implied by this snapshot. The MIT license applies to PairPulse
code; bundled CAS files retain their upstream license notices.

## Verification of this snapshot

On 6 October 2026, all four supplied unit tests passed on Windows with Python
3.12.14, NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8. Both reproduction
scripts completed with 41 momentum points, including all 246 momentum/tail
combinations in the error map. The five regenerated CSV tables had matching
headers, row counts, sampling coordinates and ODE evaluation counts.

The largest absolute difference over all numerical CSV columns was
`7.78e-15` (rounded upward), in the Dirac norm diagnostic. Occupation
differences were at most `2.29e-16` (rounded upward), and integrated-density
differences were at most `2.61e-18` (rounded upward). Per-column differences
and the fresh run metadata are in
[repository_validation.json](repository_validation.json).

The checks used the repository source directly on the Python import path;
an editable pip installation was not verified in this environment. The
notebook JSON and all Python sources parsed successfully, and all six
supplied PNG files passed image-integrity checks. The notebook was not
executed and the manuscript was not compiled as part of repository
preparation. These checks establish reproduction of the supplied numerical
examples, not broader physical validation.
