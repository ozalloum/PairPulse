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

## Scientific/editorial audit and figure typography

On 6 October 2026 the manuscript wording, captions, references and typography
were audited. Ordinary plot titles were moved into captions, Figure 4 box text
was enlarged, and the Figure 5 generator was synchronized with the portrait
workflow. The new redraw script uses the archived CSVs. All numerical source
files and five CSVs remain byte-identical to the pre-audit snapshot.

All four tests and both complete reproduction scripts passed. Each of the four
notebook code cells executed sequentially with the Agg backend; no Jupyter
kernel or Colab session was tested. pip installation could not be verified
because local temporary-file writes were denied. Numerical comparison and
environment details are in audit_validation.json. These checks supersede the
earlier notebook-execution status above but do not constitute broader validation.

The PDF was compiled with the existing multi-file MiKTeX/CAS build environment
after the built-in compiler failed to locate its platform directories. Current
build metadata are in manuscript_rebuild.json. Author queries deliberately
remain in the manuscript. No publication or journal submission was performed
as part of this audit.

## Author-confirmed contributions

On 7 October 2026, Othman H. Y. Zalloum confirmed that he carried out all aspects
of the work. The manuscript now records the applicable CRediT roles and removes
the contribution query. Three manuscript queries remain: numerical validation,
comparison with existing software, and an immutable public release. The PDF and
local archives were refreshed. No numerical results or other factual declarations
were changed by this contribution update.


## Validation revision, 9 October 2026

PairPulse version 0.2.0 exposes the existing step-cap coefficient as a public
argument (default unchanged at 0.18), rejects nonfinite/invalid controls, and
adds eight regression tests and a 2,228-evaluation validation protocol. The
original five numerical CSVs remain unchanged. New results are retained under
`validation/`; the manuscript incorporates these measured results and removes
all author-action notes as requested. Local wheel-installation tests pass for
both the minimum and reproduction dependency environments. Source-build and
kernel-permission failures are recorded separately and are not counted as passes.

Hosted run 37854584448 at commit 9cc8e8524e3b71a4c57b15d2c9d7843adb479636
subsequently passed clean source installation and all four notebook code cells
on Linux and Windows. Its four-test checks precede the expanded eight-test
release check. Hosted execution records are retained under validation/hosted/.
Earlier statements that author queries remain describe earlier snapshots;
the v0.2.0 manuscript contains no author-action notes.
