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

At initial repository preparation, the bundled manuscript and submission
notes described the pre-release package and contained repository placeholders.
The availability update below replaces those placeholders with the public URL.
No DOI or journal acceptance is implied by this snapshot. The MIT license applies to PairPulse
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

## Manuscript figure update

On 6 October 2026, the manuscript PDF was rebuilt from the existing
`manuscript/pairpulse.tex` after the author identified outdated Figures 4
and 5 in the initially supplied PDF. The source already referenced the
updated PDF figures in `results/`; no manuscript text or numerical results
were changed for this update.

The rebuild used pdfTeX 1.40.28 (MiKTeX 25.12) with the bundled CAS files.
Missing LaTeX packages and CM-Super font maps were supplied from TeX Live
in a temporary build environment. Repeated compilation resolved the
citations and cross-references. All ten PDF pages were rendered for layout
review, including the taller replacement workflow diagram. Figures 4 and
5 occur on PDF pages 6 and 7 (printed pages 5 and 6), respectively.

The decoded PDF drawing streams for all six embedded figures were checked
against their corresponding `results/*.pdf` files. In particular, Figures
4 and 5 match the current result files exactly. Build details and hashes
are recorded in [manuscript_rebuild.json](manuscript_rebuild.json). The root
checksum manifest has been refreshed for the updated repository snapshot.

## Manuscript availability update

On 6 October 2026, the developer's repository link in the program summary
and the Code and data availability statement were updated to point to
https://github.com/ozalloum/PairPulse. The statement describes the public
code, numerical data, documentation, and manuscript materials, and
distinguishes the PairPulse code license from the upstream CAS notices.
The README and submission notes were synchronized with this change.
No DOI, archival deposit, or journal acceptance is claimed.

The manuscript was rebuilt with the same CAS template and updated figures.
Current source and PDF hashes and figure checks are recorded in
[manuscript_rebuild.json](manuscript_rebuild.json). The numerical code and
result files were unchanged in this availability update.
