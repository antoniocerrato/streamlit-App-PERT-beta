import math

import numpy as np

from pert_math import (
    beta_pert_cdf,
    beta_pert_pdf,
    beta_pert_ppf,
    calculate_pert_parameters,
    sample_beta_pert,
)


def test_lambda_four_reproduces_classic_pert_mean():
    stats = calculate_pert_parameters(6, 10, 18, concentration=4)
    assert math.isclose(stats.beta_mean, stats.pert_mean, rel_tol=1e-12)


def test_mode_parameterization_is_correct():
    stats = calculate_pert_parameters(2, 5, 11, concentration=4)
    transformed_mode = 2 + (11 - 2) * (stats.alpha - 1) / (stats.alpha + stats.beta - 2)
    assert math.isclose(transformed_mode, 5, rel_tol=1e-12)


def test_cdf_and_ppf_are_inverse():
    probability = 0.9
    quantile = beta_pert_ppf(probability, 3, 6, 12, concentration=4)
    assert math.isclose(beta_pert_cdf(quantile, 3, 6, 12, 4), probability, rel_tol=1e-10)


def test_pdf_integrates_approximately_to_one():
    x = np.linspace(1, 9, 100_001)
    y = beta_pert_pdf(x, 1, 4, 9, concentration=4)
    assert math.isclose(np.trapezoid(y, x), 1.0, rel_tol=1e-5)


def test_simulation_mean_approaches_theoretical_mean():
    stats = calculate_pert_parameters(2, 5, 11, concentration=4)
    samples = sample_beta_pert(200_000, 2, 5, 11, concentration=4, seed=7)
    assert abs(samples.mean() - stats.beta_mean) < 0.02
