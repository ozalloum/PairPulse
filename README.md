# PairPulse

Public repository: [github.com/ozalloum/PairPulse](https://github.com/ozalloum/PairPulse).

PairPulse is a small, reproducible reference implementation for fermion pair creation by spatially homogeneous, time-dependent electric fields in 1+1 dimensions. It independently evolves (i) a two-component Dirac mode and (ii) the non-Markovian quantum-kinetic equations, and checks both against the exact asymptotic result for a temporal Sauter pulse.

The contribution is computational: a transparent paired implementation, an exact benchmark, pulse superposition, numerical diagnostics, and scripts that regenerate the manuscript figures and tables. The package does **not** claim a new pair-production mechanism or a new analytic result.

## Scope and conventions

Natural units are used, with mass defaulting to `m=1`. The positive charge magnitude is `q=1`; changing the sign of the charge is equivalent to reflecting canonical momentum for the backgrounds included here. The prescribed field is external and spatially uniform. Back-reaction, collisions, spatial gradients, photon dynamics, and self-consistent Maxwell evolution are outside the model.

For each canonical momentum `p`, the kinetic momentum is `pi(t)=p-q A(t)`. The default pulse is `E(t)=E0 sechÂ²((t-tc)/tau)`, `A(t)=-E0 tau tanh((t-tc)/tau)`. `PulseTrain` adds a finite number of these fields and potentials.

## Installation

Python 3.10 or later is required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[plots,test]'
python -m unittest discover -s tests -v
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` instead of the `source` command.
The bundled measurements were generated with Python 3.12.14, NumPy 2.3.5,
SciPy 1.17.0 and Matplotlib 3.10.8. To use those numerical-library versions,
install `requirements-reproduce.txt` before installing this package.

## Reproduce the results

Keep the supplied reference results in `results/` and write new runs into a
separate directory:

```bash
python scripts/reproduce.py --output regenerated --points 41
python scripts/make_reproducibility_figures.py --output regenerated --points 41
```

The scripts generate the spectra, tail-convergence data, momentum/window error-map CSV, run metadata, and all six Python-generated figures in the selected output directory. The package-structure and computational-workflow diagrams are drawn with Matplotlib by `make_reproducibility_figures.py`; the error map is computed from fresh Dirac and quantum-kinetic integrations against the exact Sauter benchmark. Run `bash scripts/build_manuscript.sh` to rebuild the CAS-format manuscript PDF. To execute the accompanying notebook, start Jupyter from the project root and open `notebooks/PairPulse_reproduction.ipynb`.

The manuscript build reads figures from `results/`; it does not automatically
use `regenerated/`. Numerical differences at floating-point precision and
machine-dependent runtimes are expected. See [the data guide](docs/DATA.md) for
the supplied CSV files and diagnostic conventions. Verify the distributed file
snapshot with `python scripts/verify_checksums.py` before changing its files.

## Redraw the figures

Redraw all six figures from the archived data without new mode integrations:

```bash
python scripts/redraw_figures.py --data results --output redrawn
```

The audit revision doubles axes, tick and legend text to 20 points in Figures
1--3 and 6 and enlarges Figure 4 box text. Scientific plot titles are supplied
by manuscript captions; panel identifiers and diagram headings are retained.

## Minimal use

```python
from pairpulse import SauterPulse, solve_dirac_mode, solve_qke_mode

pulse = SauterPulse(amplitude=0.3, duration=2.0)
print(solve_dirac_mode(0.0, pulse).occupation)
print(solve_qke_mode(0.0, pulse).occupation)
```

The Dirac result's `diagnostic` is the final spinor norm error. The QKE result's `diagnostic` is the absolute deviation of `(1-2f)^2+u^2+v^2` from unity. Both results also contain the ODE function-evaluation count and the finite integration interval.

## Program contents

- `src/pairpulse/pulses.py`: Sauter pulses and finite pulse trains.
- `src/pairpulse/solvers.py`: independent Dirac and quantum-kinetic mode solvers, exact Sauter benchmark, and momentum-integrated density.
- `scripts/reproduce.py`: regeneration of plots, CSV tables, and environment/run metadata.
- `scripts/make_reproducibility_figures.py`: Python package/workflow diagrams and a momentum-versus-tail-extent finite-window error map, including its data CSV.
- `notebooks/PairPulse_reproduction.ipynb`: executable walk-through.
- `tests/`: compact numerical regression tests.
- `manuscript/`: CAS double-column LaTeX source, compiled PDF, the matching `cas-dc.cls`, `cas-common.sty`, required CAS thumbnail assets, and the upstream CAS-bundle notice.
- `scripts/build_manuscript.sh`: rebuilds the manuscript PDF with two `pdflatex` passes (a TeX installation with the packages listed in the source is required).

## Interpretation and limits

The integrated quantity is `n_1D = integral dp f(p)/(2 pi)` for one fermionic mode species in 1+1 dimensions; it is not a 3+1-dimensional number density. Finite momentum windows and finite pulse-tail windows are explicit numerical approximations. The error map is over canonical momentum and finite time-window tail extent; the prescribed field is spatially homogeneous, so the package has no spatial error coordinate. The manuscript reports the tested window and the generated convergence diagnostics. Extending the code to scalar QED, spatial inhomogeneity, 3+1 dimensions, back-reaction, or production-scale parameter scans would require additional derivations and validation.

Both formulations use the same DOP853 integrator, tolerance settings and sampled
step-cap rule. Agreement cannot exclude shared integration or endpoint error.
The diagnostics are evaluated at the final time, not maximized over the trajectory.
The frequency estimate uses 257 sample times and is not a rigorous bound for
arbitrary custom profiles. Custom pulses must provide consistent field/potential
functions with decayed endpoints; the interface does not verify these conditions.

The additional release-validation suite completed 2,228 mode evaluations with
zero failed integrations. It includes independent tolerance/step-cap and endpoint
refinements, nine Sauter parameter pairs, a Gaussian custom pulse, QuTiP 5.2.2
comparisons, and separate momentum-grid/domain refinement. All declared numerical
criteria passed. The original five CSVs in `results/` are preserved; new evidence
is in `validation/`. These are finite empirical checks, not universal error bounds.

## Reproduce the extended validation

```sh
python -m pip install -r requirements-validation.txt .
python -m unittest discover -s tests -v
python scripts/validate_release.py --output validation-new --workers 4
python scripts/summarize_validation.py --data validation-new
python scripts/execute_notebook.py --output kernel-output
```

The validation runner requires a fresh output directory and preserves individual
failures. The notebook runner starts a real Jupyter kernel and imports the
installed package. The workflow in `.github/workflows/validation.yml` checks a
minimum dependency environment and Python 3.12 on Linux and Windows.
Hosted run [37854584448](https://github.com/ozalloum/PairPulse/actions/runs/37854584448)
passed clean source installation, dependency checks, and actual notebook-kernel
execution on both operating systems. All four notebook code cells completed with
no error outputs. That preliminary run used four regression tests; the expanded
eight-test suite is checked again during publication. Retained release execution
records distinguish those runs and include the executed notebooks.

Two isolated local wheel installations passed all eight tests: Python 3.10.20
with NumPy 1.24.0/SciPy 1.10.0 and Python 3.12.14 with the reproduction libraries.
The restricted local Windows environment blocked the isolated source build and
Jupyter connection-file permissions; these local failures remain in the evidence
and are distinct from the successful hosted checks.

## License

PairPulse code is distributed under the [MIT license](LICENSE). The bundled
Elsevier CAS class, support style and assets retain their upstream notices;
see [CAS-BUNDLE-README.txt](manuscript/CAS-BUNDLE-README.txt). Dependencies retain
their own licenses.

## Citation and provenance

The submission snapshot is identified by
[v0.2.0](https://github.com/ozalloum/PairPulse/releases/tag/v0.2.0).
The release provides the submission ZIP, manuscript PDF, and checksums, and its
tag identifies the exact source commit. Citation metadata are provided in
[CITATION.cff](CITATION.cff). No DOI has been
assigned in this repository. The manuscript's program summary and code and
data availability statement link to the public PairPulse repository.
The repository preparation and original checksum discrepancies are documented
in [docs/PROVENANCE.md](docs/PROVENANCE.md).
