from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding

from app.services.market_service import get_historical_prices
from app.services.portfolio_service import analyze_portfolio

from app.analytics.risk_analysis import (
    calculate_correlation_matrix
)

from app.analytics.diversification import (
    calculate_diversification_score
)

from app.analytics.scoring import (
    calculate_portfolio_health_score
)


def generate_portfolio_analytics(
    db: Session,
    portfolio_id: int,
    user_id: int
):
    """
    Generate complete portfolio analytics.
    """

    # Fetch portfolio
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        )
        .first()
    )

    if portfolio is None:
        return None

    # Fetch holdings
    holdings = (
        db.query(Holding)
        .filter(
            Holding.portfolio_id == portfolio.id
        )
        .all()
    )

    if not holdings:
        raise ValueError(
            "Portfolio does not contain any holdings."
        )

    # Extract symbols and quantities
    symbols = [
        holding.stock_symbol.upper()
        for holding in holdings
    ]

    quantities = [
        holding.quantity
        for holding in holdings
    ]

    # Download historical prices
    historical_prices = get_historical_prices(symbols)

    # Core portfolio metrics
    analytics = analyze_portfolio(
        symbols=symbols,
        quantities=quantities,
        price_data=historical_prices
    )

    # Correlation Matrix
    correlation = calculate_correlation_matrix(
        historical_prices
    )

    # Diversification Score
    weights = [
        holding["weight"]
        for holding in analytics["holdings"]
    ]

    diversification = calculate_diversification_score(
        weights
    )

    # Portfolio Health Score
    health = calculate_portfolio_health_score(
        annual_return=analytics["annual_return"],
        annual_volatility=analytics["annual_volatility"],
        sharpe_ratio=analytics["sharpe_ratio"],
        diversification_score=diversification[
            "diversification_score"
        ]
    )

    analytics["correlation_matrix"] = (
        correlation.round(2).to_dict()
    )

    analytics["diversification"] = diversification

    analytics["portfolio_health"] = health

    return analytics