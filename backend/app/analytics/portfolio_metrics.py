import pandas as pd
import numpy as np


TRADING_DAYS = 252

def calculate_portfolio_weights(
    quantities: np.ndarray,
    latest_prices: np.ndarray
):
    """
    Calculate total portfolio value, holding values, and stock weights.

    Parameters
    ----------
    quantities : ndarray
        Number of shares owned for each stock.

    latest_prices : ndarray
        Latest market price of each stock.

    Returns
    -------
    dict
        Total portfolio value, individual holding values, and weights.
    """

    if len(quantities) != len(latest_prices):
        raise ValueError(
            "Quantities and latest prices must have the same length."
        )

    # Value of every holding
    holding_values = quantities * latest_prices

    # Total portfolio value
    total_portfolio_value = holding_values.sum()

    if total_portfolio_value <= 0:
        raise ValueError(
            "Total portfolio value must be greater than zero."
        )

    # Weight of each stock in the portfolio
    weights = holding_values / total_portfolio_value

    return {
        "holding_values": holding_values,
        "total_portfolio_value": float(total_portfolio_value),
        "weights": weights
    }





def calculate_portfolio_metrics(price_data: pd.DataFrame,
                                weights: np.ndarray):
    """
    Calculate portfolio performance metrics.

    Parameters
    ----------
    price_data : DataFrame
        Historical closing prices of stocks.

    weights : ndarray
        Portfolio weights.

    Returns
    -------
    dict
    """

    # Daily returns
    daily_returns = price_data.pct_change().dropna()

    # Portfolio daily return
    portfolio_daily_return = daily_returns.dot(weights)

    # Annual return
    annual_return = portfolio_daily_return.mean() * TRADING_DAYS

    # Annual volatility
    annual_volatility = (
        portfolio_daily_return.std()
        * np.sqrt(TRADING_DAYS)
    )

    # Sharpe Ratio
    sharpe_ratio = (
        annual_return / annual_volatility
        if annual_volatility != 0
        else 0
    )

    return {
        "daily_returns": portfolio_daily_return,
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_volatility),
        "sharpe_ratio": float(sharpe_ratio)
    }