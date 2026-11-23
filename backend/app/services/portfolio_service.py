from typing import List

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import PortfolioCreate
from app.analytics.portfolio_metrics import (
    calculate_portfolio_metrics,
    calculate_portfolio_weights
)


def create_portfolio(
    db: Session,
    current_user: User,
    portfolio_data: PortfolioCreate
):
    """
    Create a new portfolio for the authenticated user.
    """

    new_portfolio = Portfolio(
        portfolio_name=portfolio_data.portfolio_name,
        user_id=current_user.id
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return new_portfolio


def get_portfolios(
    db: Session,
    current_user: User
):
    """
    Return all portfolios owned by the authenticated user.
    """

    return (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id
        )
        .all()
    )


def analyze_portfolio(
    symbols: List[str],
    quantities: List[float],
    price_data: pd.DataFrame
):
    """
    Generate portfolio analytics using historical closing prices.

    Parameters
    ----------
    symbols : List[str]
        Stock symbols in the user's portfolio.

    quantities : List[float]
        Number of shares owned for each stock.

    price_data : pd.DataFrame
        Historical closing prices. Each column must represent one stock.

    Returns
    -------
    dict
        Portfolio value, allocation, annual return,
        volatility and Sharpe ratio.
    """

    if not symbols:
        raise ValueError(
            "Portfolio must contain at least one stock."
        )

    if len(symbols) != len(quantities):
        raise ValueError(
            "Each stock symbol must have a corresponding quantity."
        )

    if price_data.empty:
        raise ValueError(
            "Historical stock price data cannot be empty."
        )

    # Ensure symbols use a standard format
    normalized_symbols = [
        symbol.strip().upper()
        for symbol in symbols
    ]

    # Confirm that all stocks exist in the price DataFrame
    missing_symbols = [
        symbol
        for symbol in normalized_symbols
        if symbol not in price_data.columns
    ]

    if missing_symbols:
        raise ValueError(
            "Historical price data is missing for: "
            + ", ".join(missing_symbols)
        )

    # Arrange price columns in exactly the same order as the symbols
    ordered_price_data = price_data[normalized_symbols].copy()

    # Remove incomplete rows
    ordered_price_data = ordered_price_data.dropna()

    if len(ordered_price_data) < 2:
        raise ValueError(
            "At least two days of historical prices are required."
        )

    quantities_array = np.asarray(
        quantities,
        dtype=float
    )

    if np.any(quantities_array <= 0):
        raise ValueError(
            "All stock quantities must be greater than zero."
        )

    # Latest available closing price for each stock
    latest_prices = (
        ordered_price_data.iloc[-1]
        .to_numpy(dtype=float)
    )

    # Calculate portfolio value and stock weights
    weight_results = calculate_portfolio_weights(
        quantities=quantities_array,
        latest_prices=latest_prices
    )

    # Calculate return, risk and Sharpe ratio
    metric_results = calculate_portfolio_metrics(
        price_data=ordered_price_data,
        weights=weight_results["weights"]
    )

    holdings = []

    for index, symbol in enumerate(normalized_symbols):
        holdings.append({
            "symbol": symbol,
            "quantity": float(quantities_array[index]),
            "latest_price": float(latest_prices[index]),
            "holding_value": float(
                weight_results["holding_values"][index]
            ),
            "weight": float(
                weight_results["weights"][index]
            ),
            "weight_percentage": float(
                weight_results["weights"][index] * 100
            )
        })

    return {
        "total_portfolio_value": weight_results[
            "total_portfolio_value"
        ],
        "annual_return": metric_results[
            "annual_return"
        ],
        "annual_return_percentage": (
            metric_results["annual_return"] * 100
        ),
        "annual_volatility": metric_results[
            "annual_volatility"
        ],
        "annual_volatility_percentage": (
            metric_results["annual_volatility"] * 100
        ),
        "sharpe_ratio": metric_results[
            "sharpe_ratio"
        ],
        "holdings": holdings
    }