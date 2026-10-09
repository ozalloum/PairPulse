# PairPulse

PairPulse implements paired Dirac and quantum-kinetic mode solvers for fermion pair production in prescribed, spatially homogeneous electric fields in 1+1 dimensions. An exact temporal Sauter-pulse result, conservation diagnostics, pulse superposition, and reproduction scripts support numerical checks with common conventions.

The current submission snapshot is [v0.2.1](https://github.com/ozalloum/PairPulse/releases/tag/v0.2.1). Download `PairPulse_submission_v0.2.1.zip` for the manuscript PDF and source, code, notebook, and six figures. The release tag fixes the source commit; SHA-256 manifests identify the distributed files.

## Package contents

- `src/pairpulse/`: pulse definitions, Dirac and quantum-kinetic solvers, exact Sauter occupation, and integrated density.
- `tests/`: eight regression tests.
- `notebooks/PairPulse_reproduction.ipynb`: reproduction notebook with outputs cleared.
- `scripts/`: numerical reproduction, plotting, optional validation, notebook execution, manuscript building, and checksum verification.
- `results/`: the six manuscript figures in PDF and PNG formats.
- `manuscript/`: LaTeX source, compiled PDF, Elsevier CAS class and support files.

This distribution excludes numerical validation records, CSV datasets, run metadata, executed notebooks, and execution logs. The supplied scripts generate new datasets and diagnostics. The manuscript reports the calculations performed for the study; the underlying numerical records are not included in this release or its submission archive.

## Install and test

Use Python 3.10 or later. From the project root:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[plots,test]'
python -m unittest discover -s tests -v
```

In Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. For the pinned reproduction libraries, install `requirements-reproduce.txt` before installing PairPulse.

```python
from pairpulse import SauterPulse, solve_dirac_mode, solve_qke_mode
pulse = SauterPulse(amplitude=0.3, duration=2.0)
print(solve_dirac_mode(0.0, pulse).occupation)
print(solve_qke_mode(0.0, pulse).occupation)
```

## Regenerate numerical data and figures

Run from the project root:

```sh
python scripts/reproduce.py --output regenerated --points 41
python scripts/make_reproducibility_figures.py --output regenerated --points 41
```

These commands calculate spectra, pulse-tail convergence, integrated yields, and the momentum/window error map, and write CSV data and metadata into `regenerated/`. They also generate the six publication figures. Numerical roundoff and runtimes depend on the environment.

Once the CSVs have been generated, figures can be redrawn without new integrations:

```sh
python scripts/redraw_figures.py --data regenerated --output redrawn
```

The manuscript build uses the supplied figures in `results/`:

```sh
bash scripts/build_manuscript.sh
```

A LaTeX installation with the packages requested by the source is required. To use newly generated figures, first copy the corresponding figure PDFs into `results/`.

## Notebook and optional checks

Start Jupyter in the project root and open `notebooks/PairPulse_reproduction.ipynb`, or execute its kernel programmatically:

```sh
python -m pip install -r requirements-validation.txt .
python scripts/execute_notebook.py --output kernel-output
```

Optional extended calculations can be run into a fresh output directory:

```sh
python scripts/validate_release.py --output validation-new --workers 4
python scripts/summarize_validation.py --data validation-new
```

The runner preserves failures and includes optional software-comparison calculations in addition to the studies reported in the revised manuscript. Generated output records are not part of the distributed snapshot. The continuous-integration workflow checks installation, regression tests, and notebook execution.

## Conventions and scope

Natural units are used. Defaults are mass `m=1` and positive charge magnitude `q=1`; kinetic momentum is `p-q*A(t)`. The integrated quantity is `integral dp f(p)/(2*pi)` for one fermionic mode species in 1+1 dimensions. It is not a three-dimensional density.

Both formulations use DOP853. Agreement between them cannot exclude shared integration or endpoint errors. The reported `diagnostic` is a final-time norm or invariant error, not a maximum over the trajectory. Custom pulses must supply consistent electric-field and vector-potential functions and appropriate decayed endpoints. The sampled frequency estimate does not rigorously bound arbitrary pulse profiles.

Back-reaction, collisions, spatial gradients, transverse momenta, photon dynamics, and self-consistent Maxwell evolution are outside this model.

## Checksums, license, and citation

Before modifying the distribution, run `python scripts/verify_checksums.py` to verify every listed file. Cite the version in `CITATION.cff`. No archival DOI is assigned.

PairPulse code uses the [MIT License](LICENSE). The bundled Elsevier CAS files retain their upstream notices in [CAS-BUNDLE-README.txt](manuscript/CAS-BUNDLE-README.txt). Dependencies retain their respective licenses.
