# PairPulse data guide

The reference files are in `results/`. The CSVs are UTF-8 text with a header
row and comma delimiters. Natural units are used, with `m=q=1` in the supplied
experiments. Occupation is dimensionless. Momentum is canonical momentum, in
units of the mass. The integrated density is per unit length for one fermionic
mode species in 1+1 dimensions.

| File | Contents |
| --- | --- |
| `sauter_spectrum.csv` | Single Sauter pulse: momentum, Dirac and QKE occupations, exact asymptotic occupation, final invariant/norm errors, and total ODE evaluations. |
| `double_pulse_spectrum.csv` | Two separated Sauter pulses: momentum, occupations from both formulations, final invariant/norm errors, and total ODE evaluations. No analytic reference is assumed. |
| `tail_convergence.csv` | Single-pulse calculations at momentum zero for five tail extents; exact and numerical occupations, absolute errors, diagnostics and evaluation counts. |
| `sauter_window_error_map.csv` | Momentum-by-tail-extent grid: exact asymptotic and finite-window occupations, their absolute errors, diagnostics and evaluation counts. |
| `integrated_yields.csv` | Trapezoidal integration of the supplied finite momentum spectra with measure `dp/(2*pi)`. |
| `run_metadata.json` | Recorded environment, spectrum resolution, elapsed time, numerical errors and evaluation counts for the supplied reference run. |

`qke_invariant_error` is the absolute deviation of `(1-2f)^2+u^2+v^2` from one
at the final integration time. `dirac_norm_error` is the final spinor norm
error. These are diagnostic errors, not bounds on the error in the occupation.
`nfev` fields count ODE right-hand-side evaluations; they are not timings.

For the single pulse, `E0=0.3` and `tau=2`. The double pulse uses two
same-polarity pulses with amplitude 0.30, duration 1.1 and centers -3.5 and 3.5.
The two spectra each contain 41 momenta, spanning [-1.5,1.5] for the single
pulse and [-1.8,1.8] for the double pulse. Tail extent is measured in pulse
durations. The plotting floor `1e-16` is for displaying the error map and does
not modify the CSV values.

PDF and PNG figures visualize these tables or show the package/workflow
structure. Run the two reproduction scripts into `regenerated/` to compare
fresh calculations with these reference files. Finite time and momentum
windows remain numerical approximations; the data do not establish behavior
outside the documented model and parameter settings.
