from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.services.market_service import get_stock_data


def calculate_live_portfolio(
    db: Session,
    portfolio_id: int,
    user_id: int
):
    """
    Calculate the live value and profit/loss of a user's portfolio.
    """

    # Find the portfolio and ensure it belongs to the logged-in user
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

    total_investment = 0.0
    total_current_value = 0.0

    holdings_result = []

    for holding in portfolio.holdings:

        market_data = get_stock_data(
            holding.stock_symbol
        )

        # Continue even if market data for one stock fails
        if market_data is None:
            holdings_result.append({
                "holding_id": holding.id,
                "symbol": holding.stock_symbol,
                "quantity": holding.quantity,
                "buy_price": holding.buy_price,
                "market_data_available": False,
                "message": "Live market data unavailable."
            })

            continue

        current_price = market_data["current_price"]

        invested_amount = (
            holding.quantity * holding.buy_price
        )

        current_value = (
            holding.quantity * current_price
        )

        profit_loss = (
            current_value - invested_amount
        )

        if invested_amount != 0:
            profit_loss_percent = (
                profit_loss / invested_amount
            ) * 100
        else:
            profit_loss_percent = 0.0

        total_investment += invested_amount
        total_current_value += current_value

        holdings_result.append({
            "holding_id": holding.id,
            "symbol": holding.stock_symbol,
            "company_name": market_data[
                "company_name"
            ],
            "quantity": holding.quantity,
            "buy_price": round(
                holding.buy_price,
                2
            ),
            "current_price": round(
                current_price,
                2
            ),
            "invested_amount": round(
                invested_amount,
                2
            ),
            "current_value": round(
                current_value,
                2
            ),
            "profit_loss": round(
                profit_loss,
                2
            ),
            "profit_loss_percent": round(
                profit_loss_percent,
                2
            ),
            "currency": market_data["currency"],
            "market_data_available": True
        })

    total_profit_loss = (
        total_current_value - total_investment
    )

    if total_investment != 0:
        total_profit_loss_percent = (
            total_profit_loss / total_investment
        ) * 100
    else:
        total_profit_loss_percent = 0.0

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.portfolio_name,
        "total_investment": round(
            total_investment,
            2
        ),
        "total_current_value": round(
            total_current_value,
            2
        ),
        "total_profit_loss": round(
            total_profit_loss,
            2
        ),
        "total_profit_loss_percent": round(
            total_profit_loss_percent,
            2
        ),
        "holdings_count": len(
            portfolio.holdings
        ),
        "holdings": holdings_result
    }