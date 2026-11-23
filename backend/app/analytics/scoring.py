def calculate_portfolio_health_score(
    annual_return: float,
    annual_volatility: float,
    sharpe_ratio: float,
    diversification_score: float
):
    """
    Calculate an overall portfolio health score (0-100).
    """

    # Annual Return Score (Max 30)
    return_score = min(
        max(annual_return * 100, 0),
        30
    )

    # Sharpe Score (Max 30)
    sharpe_score = min(
        max(sharpe_ratio * 15, 0),
        30
    )

    # Diversification Score (Max 20)
    diversification_component = min(
        diversification_score / 5,
        20
    )

    # Risk Score (Max 20)
    if annual_volatility <= 0.15:
        risk_score = 20
    elif annual_volatility <= 0.25:
        risk_score = 15
    elif annual_volatility <= 0.35:
        risk_score = 10
    else:
        risk_score = 5

    total_score = (
        return_score
        + sharpe_score
        + diversification_component
        + risk_score
    )

    total_score = round(min(total_score, 100), 2)

    if total_score >= 85:
        grade = "Excellent"

    elif total_score >= 70:
        grade = "Good"

    elif total_score >= 50:
        grade = "Average"

    else:
        grade = "Poor"

    return {
        "portfolio_health_score": total_score,
        "portfolio_grade": grade
    }