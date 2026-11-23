from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding

from app.services.recommendation_service import (
    recommend_portfolio
)

from app.services.portfolio_analytics_service import (
    generate_portfolio_analytics
)


def generate_ds_pipeline(
    db: Session,
    portfolio_id: int,
    user_id: int,
    risk_profile: str
):
    """
    Run the complete Data Science pipeline.

    Pipeline:
        Portfolio
            ↓
        Portfolio Holdings
            ↓
        Historical Market Data and Analytics
            ↓
        Correlation Matrix
            ↓
        Diversification Score
            ↓
        Portfolio Health Score
            ↓
        Risk Profile
            ↓
        Portfolio Optimization
            ↓
        Final Recommendation
    """

    # --------------------------------------------------
    # 1. Fetch portfolio securely
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 2. Fetch portfolio holdings
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 3. Extract stock symbols
    # --------------------------------------------------

    symbols = [
        holding.stock_symbol.strip().upper()
        for holding in holdings
    ]

    # --------------------------------------------------
    # 4. Normalize risk profile
    # --------------------------------------------------

    normalized_risk_profile = (
        risk_profile.strip().lower()
    )

    if not normalized_risk_profile:
        raise ValueError(
            "Risk profile cannot be empty."
        )

    # --------------------------------------------------
    # 5. Generate complete portfolio analytics
    # --------------------------------------------------

    portfolio_analytics = generate_portfolio_analytics(
        db=db,
        portfolio_id=portfolio_id,
        user_id=user_id
    )

    if portfolio_analytics is None:
        return None

    # --------------------------------------------------
    # 6. Generate optimized recommendation
    # --------------------------------------------------

    recommendation = recommend_portfolio(
        symbols=symbols,
        risk_profile=normalized_risk_profile
    )

    # --------------------------------------------------
    # 7. Return complete Data Science pipeline result
    # --------------------------------------------------

    return {
        "portfolio_id": portfolio_id,

        "portfolio_name": portfolio.portfolio_name,

        "risk_profile": normalized_risk_profile,

        "portfolio_analytics": portfolio_analytics,

        "recommendation": recommendation
    }
