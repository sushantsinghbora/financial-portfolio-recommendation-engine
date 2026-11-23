import numpy as np
from scipy.optimize import minimize

from app.services.market_service import (
    get_historical_prices
)


# ==================================================
# RISK PROFILES
# ==================================================

RISK_PROFILES = {
    "conservative": {
        "max_allocation": 0.50,
        "risk_aversion": 2.0,
        "description": (
            "Prioritizes lower portfolio risk "
            "and diversification."
        )
    },

    "moderate": {
        "max_allocation": 0.50,
        "risk_aversion": 1.0,
        "description": (
            "Balances expected return and "
            "portfolio risk."
        )
    },

    "aggressive": {
        "max_allocation": 0.60,
        "risk_aversion": 0.25,
        "description": (
            "Accepts higher portfolio risk "
            "for higher return potential."
        )
    }
}


# ==================================================
# PORTFOLIO OPTIMIZATION
# ==================================================

def optimize_portfolio(
    prices,
    risk_profile: str
):
    """
    Optimize portfolio allocation using
    mean-variance optimization.

    Parameters
    ----------
    prices : pandas.DataFrame
        Historical closing prices.

    risk_profile : str
        conservative, moderate, or aggressive.

    Returns
    -------
    dict
        Optimized portfolio allocation and metrics.
    """

    # --------------------------------------------------
    # Validate risk profile
    # --------------------------------------------------

    risk_profile = (
        risk_profile
        .strip()
        .lower()
    )

    if risk_profile not in RISK_PROFILES:
        raise ValueError(
            "Invalid risk profile. "
            "Choose conservative, moderate, or aggressive."
        )

    profile = RISK_PROFILES[
        risk_profile
    ]

    # --------------------------------------------------
    # Validate price data
    # --------------------------------------------------

    if prices is None or prices.empty:
        raise ValueError(
            "Historical price data cannot be empty."
        )

    prices = prices.copy()

    # Remove incomplete observations
    prices = prices.dropna()

    if len(prices) < 2:
        raise ValueError(
            "At least two observations are required "
            "for portfolio optimization."
        )

    # --------------------------------------------------
    # Normalize symbols
    # --------------------------------------------------

    symbols = [
        str(symbol).strip().upper()
        for symbol in prices.columns
    ]

    prices.columns = symbols

    num_assets = len(symbols)

    if num_assets == 0:
        raise ValueError(
            "No assets available for optimization."
        )

    # --------------------------------------------------
    # Calculate daily returns
    # --------------------------------------------------

    daily_returns = (
        prices
        .pct_change()
        .dropna()
    )

    if daily_returns.empty:
        raise ValueError(
            "Unable to calculate daily returns."
        )

    # --------------------------------------------------
    # Annualized expected returns
    # --------------------------------------------------

    mean_returns = (
        daily_returns.mean() * 252
    )

    # --------------------------------------------------
    # Annualized covariance matrix
    # --------------------------------------------------

    covariance_matrix = (
        daily_returns.cov() * 252
    )

    # Convert to numpy arrays
    expected_returns = (
        mean_returns.to_numpy(
            dtype=float
        )
    )

    covariance = (
        covariance_matrix.to_numpy(
            dtype=float
        )
    )

    # --------------------------------------------------
    # Handle numerical issues
    # --------------------------------------------------

    covariance = (
        covariance
        + np.eye(num_assets) * 1e-8
    )

    # --------------------------------------------------
    # Objective function
    # --------------------------------------------------

    def objective(weights):

        portfolio_return = np.dot(
            expected_returns,
            weights
        )

        portfolio_variance = np.dot(
            weights.T,
            np.dot(
                covariance,
                weights
            )
        )

        return (
            -portfolio_return
            + profile["risk_aversion"]
            * portfolio_variance
        )

    # --------------------------------------------------
    # Portfolio weights must total 100%
    # --------------------------------------------------

    constraints = (
        {
            "type": "eq",
            "fun": lambda weights:
                np.sum(weights) - 1
        },
    )

    # --------------------------------------------------
    # Allocation limits
    # --------------------------------------------------

    # Adjust allocation limit only when required
    # to make the optimization constraints feasible.
    max_allocation = max(
        profile["max_allocation"],
        1.0 / num_assets
    )

    max_allocation = min(
        max_allocation,
        1.0
    )

    bounds = tuple(
        (0.0, max_allocation)
        for _ in range(num_assets)  
    )
    # --------------------------------------------------
    # Check whether constraints are feasible
    # --------------------------------------------------

    if (
        num_assets * max_allocation
        < 1.0
    ):
        raise ValueError(
            "Risk-profile allocation constraints "
            "are infeasible for the number of assets."
        )

    # --------------------------------------------------
    # Initial equal allocation
    # --------------------------------------------------

    initial_weights = (
        np.ones(num_assets)
        / num_assets
    )

    # Make sure initial weights satisfy bounds
    if np.any(
        initial_weights > max_allocation
    ):
        initial_weights = np.minimum(
            initial_weights,
            max_allocation
        )

        initial_weights = (
            initial_weights
            / initial_weights.sum()
        )

    # --------------------------------------------------
    # First optimization attempt
    # --------------------------------------------------

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={
            "maxiter": 2000,
            "ftol": 1e-9,
            "disp": False
        }
    )

    # --------------------------------------------------
    # Retry optimization if first attempt fails
    # --------------------------------------------------

    if not result.success:

        # Alternative starting point
        fallback_weights = np.ones(
            num_assets
        ) / num_assets

        result = minimize(
            objective,
            fallback_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 5000,
                "ftol": 1e-8,
                "disp": False
            }
        )

    # --------------------------------------------------
    # Final validation
    # --------------------------------------------------

    if not result.success:
        raise ValueError(
            "Recommendation optimization failed: "
            f"{result.message}"
        )

    weights = np.asarray(
        result.x,
        dtype=float
    )

    # --------------------------------------------------
    # Numerical cleanup
    # --------------------------------------------------

    weights[
        np.abs(weights) < 1e-10
    ] = 0.0

    # Normalize weights so they sum exactly to 1
    weights = (
        weights
        / weights.sum()
    )

    # --------------------------------------------------
    # Portfolio expected return
    # --------------------------------------------------

    portfolio_return = np.dot(
        expected_returns,
        weights
    )

    # --------------------------------------------------
    # Portfolio volatility
    # --------------------------------------------------

    portfolio_variance = np.dot(
        weights.T,
        np.dot(
            covariance,
            weights
        )
    )

    portfolio_volatility = np.sqrt(
        max(
            portfolio_variance,
            0.0
        )
    )

    # --------------------------------------------------
    # Sharpe ratio
    # --------------------------------------------------

    if portfolio_volatility == 0:

        sharpe_ratio = 0.0

    else:

        # Assumes zero risk-free rate
        sharpe_ratio = (
            portfolio_return
            / portfolio_volatility
        )

    # --------------------------------------------------
    # Final allocation
    # --------------------------------------------------

    allocation = {
        symbol: float(
            round(
                weight * 100,
                2
            )
        )
        for symbol, weight in zip(
            symbols,
            weights
        )
    }

    # --------------------------------------------------
    # Return recommendation
    # --------------------------------------------------

    return {
        "risk_profile": risk_profile,

        "description": profile[
            "description"
        ],

        "recommended_allocation": allocation,

        "optimization_metrics": {
            "expected_return": float(
                round(
                    portfolio_return * 100,
                    2
                )
            ),

            "expected_volatility": float(
                round(
                    portfolio_volatility * 100,
                    2
                )
            ),

            "sharpe_ratio": float(
                round(
                    sharpe_ratio,
                    3
                )
            )
        }
    }


# ==================================================
# PUBLIC RECOMMENDATION FUNCTION
# ==================================================

def recommend_portfolio(
    symbols: list[str],
    risk_profile: str
):
    """
    Generate a portfolio recommendation from
    stock symbols and investor risk profile.

    This function downloads historical market
    data and passes it to the optimizer.
    """

    # --------------------------------------------------
    # Validate symbols
    # --------------------------------------------------

    if not symbols:
        raise ValueError(
            "At least one stock symbol is required."
        )

    normalized_symbols = [
        symbol.strip().upper()
        for symbol in symbols
        if symbol and symbol.strip()
    ]

    if not normalized_symbols:
        raise ValueError(
            "No valid stock symbols were provided."
        )

    # --------------------------------------------------
    # Download historical prices
    # --------------------------------------------------

    prices = get_historical_prices(
        normalized_symbols
    )

    if prices.empty:
        raise ValueError(
            "No historical price data found."
        )

    # --------------------------------------------------
    # Optimize portfolio
    # --------------------------------------------------

    return optimize_portfolio(
        prices,
        risk_profile
    )