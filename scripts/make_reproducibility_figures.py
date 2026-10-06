#!/usr/bin/env python3
"""Generate the package/workflow diagrams and the finite-window error map.

All graphics use Matplotlib and are saved as vector PDF and raster PNG. The
error-map CSV records every mode calculation behind the heat map.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.colors import LogNorm

from pairpulse import SauterPulse, sauter_exact_occupation, solve_dirac_mode, solve_qke_mode


INK = "#18324b"
BLUE = "#dceaf5"
TEAL = "#dcefe9"
GOLD = "#f8edcf"
PALE = "#f4f6f8"
MUTED = "#556575"


def _box(ax, xy, width, height, title, body, color=BLUE, *, title_size=11,
         body_size=9, mono=False):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=color, edgecolor=INK, linewidth=1.05,
        transform=ax.transAxes, clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(x + 0.025, y + height - 0.035, title, transform=ax.transAxes,
            ha="left", va="top", fontsize=title_size, fontweight="bold", color=INK)
    ax.text(x + 0.025, y + height - 0.085, body, transform=ax.transAxes,
            ha="left", va="top", fontsize=body_size, color=INK,
            family="monospace" if mono else "sans-serif", linespacing=1.35)


def _arrow(ax, start, end, *, color=INK, rad=0.0, lw=1.5):
    arrow = FancyArrowPatch(
        start, end, transform=ax.transAxes, arrowstyle="-|>",
        mutation_scale=10, linewidth=lw, color=color,
        shrinkA=0, shrinkB=0, capstyle="round", joinstyle="round",
        connectionstyle=f"arc3,rad={rad}", clip_on=False, zorder=3,
    )
    ax.add_patch(arrow)


def make_structure_figure(output: Path, project_root: Path) -> None:
    """Draw the public package tree as artifact groups tied to real paths."""
    required = (
        "src/pairpulse/pulses.py", "src/pairpulse/solvers.py",
        "tests/test_pairpulse.py", "notebooks/PairPulse_reproduction.ipynb",
        "scripts/reproduce.py", "scripts/make_reproducibility_figures.py",
        "scripts/build_manuscript.sh", "results/run_metadata.json",
        "results/tail_convergence.csv", "manuscript/pairpulse.tex",
        "manuscript/pairpulse.pdf", "README.md", "pyproject.toml",
        "LICENSE", "CHECKSUMS.sha256",
    )
    missing = [rel for rel in required if not (project_root / rel).is_file()]
    if missing:
        raise FileNotFoundError(f"Package structure has missing files: {missing}")

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.set_axis_off()
    ax.text(0.5, 0.97, "PairPulse public reproducibility package",
            ha="center", va="top", transform=ax.transAxes,
            fontsize=16, fontweight="bold", color=INK)
    ax.text(0.5, 0.90, "One source package links mode solvers, validation, generated artifacts, and the manuscript",
            ha="center", va="top", transform=ax.transAxes,
            fontsize=9.5, color=MUTED)

    # Root node and three content groups describe the actual directory tree.
    _box(ax, (0.35, 0.735), 0.30, 0.11, "PairPulse/", "MIT-licensed source archive",
         color=GOLD, title_size=12, body_size=8.6)

    _box(ax, (0.01, 0.25), 0.31, 0.40, "Source and verification",
         "src/pairpulse/\n  pulses.py — E(t), A(t)\n  solvers.py — Dirac, QKE\n    exact Sauter benchmark\n\ntests/test_pairpulse.py\nnotebooks/\n  PairPulse_reproduction.ipynb\nREADME · pyproject · LICENSE",
         color=BLUE, body_size=8.0, mono=True)
    _box(ax, (0.345, 0.25), 0.31, 0.40, "Scripts and outputs",
         "scripts/reproduce.py\n  spectra / yields / diagnostics\nscripts/make_\n  reproducibility_figures.py\n  diagrams + error map\n\nresults/\n  CSV datasets + JSON metadata\n  figures: PDF and PNG",
         color=TEAL, body_size=8.0, mono=True)
    _box(ax, (0.68, 0.25), 0.31, 0.40, "Manuscript and release",
         "manuscript/\n  pairpulse.tex + pairpulse.pdf\n  CAS class, styles, assets\n\nscripts/build_manuscript.sh\nCHECKSUMS.sha256\nSUBMISSION_NOTES.md",
         color=GOLD, body_size=8.0, mono=True)
    ax.plot([0.50, 0.50], [0.719, 0.697], transform=ax.transAxes,
            color=INK, linewidth=1.5, solid_capstyle="round", clip_on=False)
    ax.plot([0.165, 0.835], [0.697, 0.697], transform=ax.transAxes,
            color=INK, linewidth=1.5, solid_capstyle="round", clip_on=False)
    _arrow(ax, (0.165, 0.697), (0.165, 0.666))
    _arrow(ax, (0.50, 0.697), (0.50, 0.666))
    _arrow(ax, (0.835, 0.697), (0.835, 0.666))

    ax.text(0.5, 0.18,
            "Rebuild: run both Python scripts → regenerate the CAS PDF → verify CHECKSUMS.sha256",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=9.2, color=INK, fontweight="semibold")
    ax.text(0.5, 0.105,
            "Generated datasets and figures are included alongside their source-generating code.",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=8.4, color=MUTED)
    fig.subplots_adjust(left=0.025, right=0.975, top=0.98, bottom=0.04)
    fig.savefig(output / "figure4_reproducibility_structure.pdf", bbox_inches="tight")
    fig.savefig(output / "figure4_reproducibility_structure.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_workflow_figure(output: Path) -> None:
    """Draw the run-to-publication workflow implemented by the package."""
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    ax.set_axis_off()
    ax.text(0.5, 0.97, "Computational workflow for the reproducibility datasets and figures",
            ha="center", va="top", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=INK)
    ax.text(0.5, 0.905, "The same field and momentum conventions are used by both independent mode formulations",
            ha="center", va="top", transform=ax.transAxes,
            fontsize=8.4, color=MUTED)

    _box(ax, (0.01, 0.53), 0.29, 0.29, "1  Set parameters",
         "Pulse parameters and units\nMomentum grid p/m\nTail extent L/τ\nSolver tolerances",
         color=GOLD, title_size=10, body_size=8.5)
    _box(ax, (0.355, 0.53), 0.29, 0.29, "2  Define the field",
         "Sauter pulse or pulse train\nE(t), A(t), finite window",
         color=BLUE, title_size=10, body_size=8.5)
    _box(ax, (0.70, 0.53), 0.29, 0.29, "3  Solve each mode",
         "Dirac spinor: DOP853\nQKE state (f,u,v): DOP853\nIndependent integrations",
         color=TEAL, title_size=10, body_size=8.5)
    _box(ax, (0.70, 0.105), 0.29, 0.29, "4  Validate each run",
         "Exact Sauter benchmark\nDirac norm; QKE invariant\nDirac–QKE agreement; tail test",
         color=BLUE, title_size=10, body_size=8.5)
    _box(ax, (0.355, 0.105), 0.29, 0.29, "5  Save datasets",
         "Spectrum and yield CSV\nTail and p–L/τ map CSV\nRun metadata JSON",
         color=TEAL, title_size=10, body_size=8.5)
    _box(ax, (0.01, 0.105), 0.29, 0.29, "6  Generate and build",
         "Python/Matplotlib figures\nLaTeX → two-pass CAS PDF\nPackage checksums",
         color=GOLD, title_size=10, body_size=8.5)

    _arrow(ax, (0.315, 0.675), (0.340, 0.675))
    _arrow(ax, (0.660, 0.675), (0.685, 0.675))
    _arrow(ax, (0.845, 0.515), (0.845, 0.410))
    _arrow(ax, (0.685, 0.250), (0.660, 0.250))
    _arrow(ax, (0.340, 0.250), (0.315, 0.250))
    ax.text(0.5, 0.018,
            "Scripts: reproduce.py · make_reproducibility_figures.py · build_manuscript.sh",
            ha="center", va="bottom", transform=ax.transAxes,
            fontsize=7.8, color=MUTED, family="monospace")

    fig.subplots_adjust(left=0.025, right=0.975, top=0.98, bottom=0.04)
    fig.savefig(output / "figure5_computational_workflow.pdf", bbox_inches="tight")
    fig.savefig(output / "figure5_computational_workflow.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_window_error_map(output: Path, *, points: int,
                          tail_factors: tuple[float, ...]) -> dict[str, float]:
    """Compute and plot absolute finite-window errors for the exact benchmark."""
    pulse = SauterPulse(amplitude=0.3, duration=2.0)
    momenta = np.linspace(-1.5, 1.5, points)
    rows: list[tuple[float, ...]] = []
    error_dirac = np.empty((len(tail_factors), points))
    error_qke = np.empty_like(error_dirac)
    for i, factor in enumerate(tail_factors):
        for j, momentum in enumerate(momenta):
            exact = sauter_exact_occupation(float(momentum), pulse)
            d = solve_dirac_mode(float(momentum), pulse, tail_factor=factor)
            k = solve_qke_mode(float(momentum), pulse, tail_factor=factor)
            error_dirac[i, j] = abs(d.occupation - exact)
            error_qke[i, j] = abs(k.occupation - exact)
            rows.append((momentum, factor, exact, d.occupation, k.occupation,
                         error_dirac[i, j], error_qke[i, j],
                         d.diagnostic, k.diagnostic, d.nfev, k.nfev))

    csv_path = output / "sauter_window_error_map.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("momentum", "tail_extent_over_tau", "exact_asymptotic",
                         "dirac_finite_window", "qke_finite_window",
                         "dirac_absolute_error", "qke_absolute_error",
                         "dirac_norm_error", "qke_invariant_error",
                         "dirac_nfev", "qke_nfev"))
        writer.writerows(rows)

    # A floor is needed only to display roundoff-level values on logarithmic axes.
    floor = 1e-16
    ceiling = max(float(error_dirac.max()), float(error_qke.max()))
    norm = LogNorm(vmin=floor, vmax=ceiling)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0), sharex=True, sharey=True,
                             constrained_layout=True)
    for ax, err, title in zip(axes, (error_dirac, error_qke),
                              ("Dirac modes", "Quantum-kinetic modes")):
        mesh = ax.pcolormesh(momenta, tail_factors, np.maximum(err, floor),
                             shading="nearest", cmap="magma_r", norm=norm)
        ax.set_title(title, fontsize=11, color=INK, pad=8)
        ax.set_xlabel(r"canonical momentum $p/m$")
        ax.set_xticks(np.linspace(-1.5, 1.5, 7))
        ax.set_yticks(tail_factors)
        ax.grid(which="major", color="white", linewidth=0.35, alpha=0.45)
    axes[0].set_ylabel(r"tail extent $L/\tau$")
    colorbar = fig.colorbar(mesh, ax=axes, pad=0.025, shrink=0.96)
    colorbar.set_label(r"absolute error $|f_p(T)-f_p^{\rm exact}|$", rotation=90)
    fig.suptitle(r"Finite-window error against the asymptotic Sauter benchmark ($E_0/m^2=0.3$, $m\tau=2$)",
                 fontsize=11, color=INK)
    fig.savefig(output / "figure6_sauter_window_error_map.pdf", bbox_inches="tight")
    fig.savefig(output / "figure6_sauter_window_error_map.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    return {
        "map_points": int(points),
        "map_tail_factors": [float(x) for x in tail_factors],
        "map_max_absolute_error_dirac": float(error_dirac.max()),
        "map_max_absolute_error_qke": float(error_qke.max()),
        "map_min_absolute_error_dirac": float(error_dirac.min()),
        "map_min_absolute_error_qke": float(error_qke.min()),
        "map_plot_floor": floor,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--points", type=int, default=41)
    parser.add_argument("--tail-factors", type=float, nargs="+",
                        default=(4.0, 6.0, 8.0, 10.0, 12.0, 14.0))
    args = parser.parse_args()
    if args.points < 9:
        parser.error("--points must be at least 9")
    if any(x <= 0 for x in args.tail_factors):
        parser.error("all --tail-factors must be positive")
    if len(set(args.tail_factors)) != len(args.tail_factors):
        parser.error("--tail-factors must be unique")
    args.output.mkdir(parents=True, exist_ok=True)
    project_root = Path(__file__).resolve().parents[1]
    make_structure_figure(args.output, project_root)
    make_workflow_figure(args.output)
    stats = make_window_error_map(args.output, points=args.points,
                                  tail_factors=tuple(args.tail_factors))
    print(stats)


if __name__ == "__main__":
    main()
