import numpy as np


def calculate_diversification_score(weights):
    """
    Calculate portfolio diversification score
    using the Herfindahl-Hirschman Index (HHI).

    Returns
    -------
    dict
    """
    weights = np.array(weights, dtype=float)
    
    if len(weights) == 0:
        raise ValueError(
            "Portfolio weights cannot be empty."
        )

    if not np.isclose(weights.sum(), 1.0):
        raise ValueError(
            "Portfolio weights must sum to 1."
        )

    # Herfindahl-Hirschman Index
    hhi = np.sum(weights ** 2)

    # Convert to score (0–100)
    diversification_score = (1 - hhi) * 100

    # Classification
    if diversification_score >= 75:
        level = "Excellent"

    elif diversification_score >= 50:
        level = "Good"

    elif diversification_score >= 25:
        level = "Moderate"

    else:
        level = "Poor"

    return {
        "diversification_score": round(
            diversification_score,
            2
        ),
        "diversification_level": level,
        "hhi": round(hhi, 4)
    }