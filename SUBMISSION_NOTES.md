# PairPulse validation revision - 9 October 2026

The manuscript is `manuscript/pairpulse.tex`, with its rebuilt PDF beside it.
All author-action notes and the unused note macro have been removed.

## Completed and measured

- 2,228 mode evaluations; zero failed integrations; all declared numerical criteria pass.
- Independent tolerance/cap and endpoint refinements; nine Sauter parameter pairs.
- Separate momentum-grid and momentum-domain refinement, plus yield control checks.
- Executed QuTiP 5.2.2 comparison and custom Gaussian-pulse check.
- Manuscript tables and interpretation updated from the retained data.
- Eight tests pass in each of two isolated local wheel installations, including
  Python 3.10.20 with NumPy 1.24.0, SciPy 1.10.0, Matplotlib 3.7.0.
- Hosted clean source installation and actual notebook-kernel execution passed
  on Linux and Windows; see `validation/hosted/` for revision-specific records.
- CRediT roles recorded from the author's confirmation; original five CSVs preserved.

## Versioned snapshot

The submission snapshot is v0.2.0:
https://github.com/ozalloum/PairPulse/releases/tag/v0.2.0
Its tag records the source commit. GitHub release metadata record whether the
published release is immutable. No archival DOI is claimed. CHECKSUMS.sha256
identifies the distributed files; run `python scripts/verify_checksums.py`.

Historical audit reports and restricted local Windows build/kernel failures
are retained as historical evidence. They are not current validation conclusions.
The release execution records and manuscript supersede the earlier open queries.

No journal submission or correspondence was sent. No PairPulse reviewer reports
were supplied, so the audit notes are not a reply to actual reviewer comments.
Journal-specific requirements and the author's final scientific approval remain
part of the submission process.
