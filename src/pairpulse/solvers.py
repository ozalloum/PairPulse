"""Independent mode-evolution formulations for fermion pair production."""

from __future__ import annotations

from dataclasses import dataclass
from math import log, pi, sqrt

import numpy as np
from scipy.integrate import solve_ivp

from .pulses import ElectricPulse, SauterPulse


@dataclass(frozen=True)
class ModeResult:
    occupation: float
    diagnostic: float
    nfev: int
    time_span: tuple[float, float]


def _validate_mode(momentum: float, mass: float, charge: float) -> None:
    if mass <= 0.0:
        raise ValueError("mass must be positive")
    if charge <= 0.0:
        raise ValueError("charge magnitude must be positive")
    if not np.isfinite(momentum):
        raise ValueError("momentum must be finite")


def _instantaneous_kinematics(t: float, p: float, m: float,
                              q: float, pulse: ElectricPulse) -> tuple[float, float]:
    kinetic_p = p - q * float(pulse.potential(t))
    omega = sqrt(m * m + kinetic_p * kinetic_p)
    return kinetic_p, omega


def _maximum_step(t0: float, tf: float, p: float, m: float, q: float,
                  pulse: ElectricPulse) -> float:
    # Bound phase advance for strongly accelerated modes as well as low-field runs.
    samples = np.linspace(t0, tf, 257)
    pi_max = max(abs(p - q * float(pulse.potential(float(t)))) for t in samples)
    omega_max = sqrt(m * m + pi_max * pi_max)
    return 0.18 / omega_max


def solve_dirac_mode(
    momentum: float,
    pulse: ElectricPulse,
    *,
    mass: float = 1.0,
    charge: float = 1.0,
    tail_factor: float = 12.0,
    rtol: float = 2e-10,
    atol: float = 2e-12,
) -> ModeResult:
    r"""Evolve the two-component Dirac mode and project onto the out state.

    The Hamiltonian is ``H(t)=pi(t) sigma_1 + m sigma_3``, with
    ``pi=p-q A(t)``.  Initial and final instants are finite, placed
    ``tail_factor`` pulse widths beyond the outer pulse centers.
    """
    _validate_mode(momentum, mass, charge)
    t0, tf = pulse.time_window(tail_factor)
    pi0, _ = _instantaneous_kinematics(t0, momentum, mass, charge, pulse)
    pif, _ = _instantaneous_kinematics(tf, momentum, mass, charge, pulse)

    def eigenvectors(kinetic_p: float) -> tuple[np.ndarray, np.ndarray]:
        theta = np.arctan2(kinetic_p, mass)
        positive = np.array([np.cos(theta / 2.0), np.sin(theta / 2.0)], dtype=complex)
        negative = np.array([-np.sin(theta / 2.0), np.cos(theta / 2.0)], dtype=complex)
        return positive, negative

    _, initial = eigenvectors(pi0)
    positive_out, _ = eigenvectors(pif)

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        kinetic_p = momentum - charge * float(pulse.potential(t))
        return -1j * np.array([
            mass * y[0] + kinetic_p * y[1],
            kinetic_p * y[0] - mass * y[1],
        ])

    sol = solve_ivp(rhs, (t0, tf), initial, method="DOP853", rtol=rtol,
                    atol=atol, max_step=_maximum_step(t0, tf, momentum, mass, charge, pulse))
    if not sol.success:
        raise RuntimeError(f"Dirac mode integration failed: {sol.message}")
    state = sol.y[:, -1]
    occupation = float(abs(np.vdot(positive_out, state)) ** 2)
    norm_error = float(abs(np.vdot(state, state).real - 1.0))
    return ModeResult(occupation, norm_error, int(sol.nfev), (float(t0), float(tf)))


def solve_qke_mode(
    momentum: float,
    pulse: ElectricPulse,
    *,
    mass: float = 1.0,
    charge: float = 1.0,
    tail_factor: float = 12.0,
    rtol: float = 2e-10,
    atol: float = 2e-12,
) -> ModeResult:
    r"""Integrate the non-Markovian quantum-kinetic mode equations.

    For ``(f,u,v)`` the equations are

    ``f_dot = W u/2``, ``u_dot = W(1-2f)-2 omega v``, and
    ``v_dot = 2 omega u``, where ``W=q E m / omega²``.  The spinor
    representation and this system are integrated independently.
    """
    _validate_mode(momentum, mass, charge)
    t0, tf = pulse.time_window(tail_factor)

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        kinetic_p, omega = _instantaneous_kinematics(t, momentum, mass, charge, pulse)
        electric = float(pulse.field(t))
        coupling = charge * electric * mass / (omega * omega)
        f, u, v = y
        return np.array([
            0.5 * coupling * u,
            coupling * (1.0 - 2.0 * f) - 2.0 * omega * v,
            2.0 * omega * u,
        ])

    sol = solve_ivp(rhs, (t0, tf), np.zeros(3), method="DOP853", rtol=rtol,
                    atol=atol, max_step=_maximum_step(t0, tf, momentum, mass, charge, pulse))
    if not sol.success:
        raise RuntimeError(f"QKE mode integration failed: {sol.message}")
    f, u, v = sol.y[:, -1]
    invariant = (1.0 - 2.0 * f) ** 2 + u * u + v * v
    return ModeResult(float(f), float(abs(invariant - 1.0)), int(sol.nfev),
                      (float(t0), float(tf)))


def _log_sinh_positive(x: float) -> float:
    if x <= 0.0:
        return -np.inf
    if x < 1e-4:
        return log(np.sinh(x))
    return x - log(2.0) + float(np.log1p(-np.exp(-2.0 * x)))


def sauter_exact_occupation(
    momentum: float,
    pulse: SauterPulse,
    *,
    mass: float = 1.0,
    charge: float = 1.0,
) -> float:
    r"""Exact asymptotic occupation number for one temporal Sauter pulse.

    This benchmark is independent of the ODE integrations and is useful for
    checking both finite-time solvers.  It uses natural units.
    """
    _validate_mode(momentum, mass, charge)
    if pulse.amplitude == 0.0:
        return 0.0
    e0, tau = pulse.amplitude, pulse.duration
    omega_minus = sqrt(mass**2 + (momentum - charge * e0 * tau) ** 2)
    omega_plus = sqrt(mass**2 + (momentum + charge * e0 * tau) ** 2)
    lam = charge * e0 * tau * tau
    a, b = pi * tau * omega_plus, pi * tau * omega_minus
    x1 = pi * lam + 0.5 * (a - b)
    x2 = pi * lam - 0.5 * (a - b)
    log_n = (_log_sinh_positive(x1) + _log_sinh_positive(x2)
             - _log_sinh_positive(a) - _log_sinh_positive(b))
    if not np.isfinite(log_n):
        return 0.0
    return float(np.exp(min(log_n, 0.0)))


def integrated_density(momentum: np.ndarray, occupation: np.ndarray) -> float:
    """Integrate a one-dimensional momentum spectrum with measure ``dp/(2 pi)``."""
    p = np.asarray(momentum, dtype=float)
    f = np.asarray(occupation, dtype=float)
    if p.ndim != 1 or f.shape != p.shape or p.size < 2:
        raise ValueError("momentum and occupation must be equal-length 1D arrays")
    order = np.argsort(p)
    p_sorted, f_sorted = p[order], f[order]
    integral = np.sum(0.5 * (f_sorted[1:] + f_sorted[:-1]) * np.diff(p_sorted))
    return float(integral / (2.0 * pi))
