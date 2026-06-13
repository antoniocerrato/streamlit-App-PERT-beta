"""Funciones matemáticas para el método PERT de tres valores y Beta-PERT."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.stats import beta as beta_distribution


@dataclass(frozen=True)
class PertParameters:
    """Parámetros y estadísticos principales de una estimación Beta-PERT."""

    optimistic: float
    most_likely: float
    pessimistic: float
    concentration: float
    alpha: float
    beta: float
    pert_mean: float
    beta_mean: float
    pert_standard_deviation: float
    pert_variance: float
    beta_variance: float


def validate_three_point_estimate(a: float, m: float, b: float) -> None:
    """Valida una estimación de tres valores.

    Se exige a < b y a <= m <= b. Se permiten m=a o m=b para estudiar
    casos límite, aunque la moda queda situada en un extremo.
    """

    values = (a, m, b)
    if not all(np.isfinite(value) for value in values):
        raise ValueError("Los tres valores deben ser números finitos.")
    if a >= b:
        raise ValueError("El valor pesimista debe ser mayor que el optimista (a < b).")
    if not a <= m <= b:
        raise ValueError("Debe cumplirse a ≤ m ≤ b.")


def beta_pert_shape_parameters(
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
) -> tuple[float, float]:
    """Calcula los parámetros alfa y beta de la distribución Beta-PERT."""

    validate_three_point_estimate(a, m, b)
    if not np.isfinite(concentration) or concentration <= 0:
        raise ValueError("El parámetro de concentración λ debe ser positivo.")

    alpha = 1.0 + concentration * (m - a) / (b - a)
    beta = 1.0 + concentration * (b - m) / (b - a)
    return alpha, beta


def calculate_pert_parameters(
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
) -> PertParameters:
    """Calcula los estadísticos clásicos PERT y los de Beta-PERT."""

    alpha, beta = beta_pert_shape_parameters(a, m, b, concentration)
    span = b - a

    pert_mean = (a + 4.0 * m + b) / 6.0
    beta_mean = a + span * alpha / (alpha + beta)
    pert_standard_deviation = span / 6.0
    pert_variance = pert_standard_deviation**2
    beta_variance = (
        span**2
        * alpha
        * beta
        / ((alpha + beta) ** 2 * (alpha + beta + 1.0))
    )

    return PertParameters(
        optimistic=a,
        most_likely=m,
        pessimistic=b,
        concentration=concentration,
        alpha=alpha,
        beta=beta,
        pert_mean=pert_mean,
        beta_mean=beta_mean,
        pert_standard_deviation=pert_standard_deviation,
        pert_variance=pert_variance,
        beta_variance=beta_variance,
    )


def beta_pert_pdf(
    x: Iterable[float] | np.ndarray,
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
) -> np.ndarray:
    """Densidad Beta-PERT transformada al intervalo [a, b]."""

    alpha, beta = beta_pert_shape_parameters(a, m, b, concentration)
    x_array = np.asarray(x, dtype=float)
    z = (x_array - a) / (b - a)
    density = beta_distribution.pdf(z, alpha, beta) / (b - a)
    return np.where((x_array >= a) & (x_array <= b), density, 0.0)


def beta_pert_cdf(
    x: float | np.ndarray,
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
) -> float | np.ndarray:
    """Función de distribución acumulada Beta-PERT."""

    alpha, beta = beta_pert_shape_parameters(a, m, b, concentration)
    z = (np.asarray(x, dtype=float) - a) / (b - a)
    result = beta_distribution.cdf(z, alpha, beta)
    result = np.where(np.asarray(x) < a, 0.0, result)
    result = np.where(np.asarray(x) > b, 1.0, result)
    return float(result) if np.ndim(result) == 0 else result


def beta_pert_ppf(
    probability: float,
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
) -> float:
    """Cuantil de la distribución Beta-PERT."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("La probabilidad debe estar comprendida entre 0 y 1.")
    alpha, beta = beta_pert_shape_parameters(a, m, b, concentration)
    return float(a + (b - a) * beta_distribution.ppf(probability, alpha, beta))


def sample_beta_pert(
    size: int,
    a: float,
    m: float,
    b: float,
    concentration: float = 4.0,
    seed: int | None = None,
) -> np.ndarray:
    """Genera observaciones aleatorias de una distribución Beta-PERT."""

    if size <= 0:
        raise ValueError("El tamaño de la simulación debe ser positivo.")
    alpha, beta = beta_pert_shape_parameters(a, m, b, concentration)
    rng = np.random.default_rng(seed)
    return a + (b - a) * rng.beta(alpha, beta, size=size)
