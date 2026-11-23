import numpy as np
from scipy.optimize import minimize

from app.services.market_service import get_historical_prices


def optimize_portfolio(symbols: list[str]):

    # Download historical prices
    prices = get_historical_prices(symbols)

    if prices.empty:
        raise ValueError("No historical price data found.")

    # Daily returns
    daily_returns = prices.pct_change().dropna()

    # Annual statistics
    mean_returns = daily_returns.mean() * 252
    covariance_matrix = daily_returns.cov() * 252

    # Portfolio performance function
    def portfolio_performance(weights):

        portfolio_return = np.sum(mean_returns * weights)

        portfolio_volatility = np.sqrt(
            np.dot(
                weights.T,
                np.dot(covariance_matrix, weights)
            )
        )

        return portfolio_return, portfolio_volatility

    # Objective function
    def negative_sharpe_ratio(weights):

        portfolio_return, portfolio_volatility = portfolio_performance(
            weights
        )

        if portfolio_volatility == 0:
            return 0

        sharpe_ratio = portfolio_return / portfolio_volatility

        return -sharpe_ratio

    # Number of stocks
    num_assets = len(symbols)

    # Equal-weight starting point
    initial_weights = np.array(
        [1 / num_assets] * num_assets
    )

    # All weights must add up to 100%
    constraints = (
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1
        },
    )

    # No short selling + dynamically feasible allocation limit
    max_allocation = max(0.40, 1 / num_assets)

    bounds = tuple(
        (0, max_allocation)
        for _ in range(num_assets)  
    )
    # Run optimization
    result = minimize(
        negative_sharpe_ratio,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    # Check optimization result
    if not result.success:
        raise ValueError(
            f"Portfolio optimization failed: {result.message}"
        )

    # Optimized weights
    optimal_weights = result.x

    # Final portfolio metrics
    expected_return, expected_volatility = portfolio_performance(
        optimal_weights
    )

    sharpe_ratio = expected_return / expected_volatility

    # Final result
    return {
        "weights": {
            symbol: round(weight * 100, 2)
            for symbol, weight in zip(symbols, optimal_weights)
        },
        "expected_return": round(expected_return * 100, 2),
        "expected_volatility": round(expected_volatility * 100, 2),
        "sharpe_ratio": round(sharpe_ratio, 3)
    }