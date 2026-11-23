
import numpy as np
import pandas as pd


def generate_efficient_frontier(
    historical_prices,
    risk_free_rate=0.06,
    num_portfolios=10000
):
    """
    Generate Monte Carlo portfolio simulations,
    identify the maximum Sharpe ratio portfolio,
    and calculate an approximate efficient frontier.
    """

    if not isinstance(historical_prices, pd.DataFrame):
        raise ValueError(
            "Historical prices must be a pandas DataFrame."
        )

    prices = (
        historical_prices
        .dropna(axis=1, how="all")
        .dropna()
    )

    if prices.empty or prices.shape[1] < 2:
        raise ValueError(
            "At least two assets with valid price data are required."
        )

    returns = prices.pct_change().dropna()

    if returns.empty:
        raise ValueError(
            "Not enough historical data to calculate returns."
        )

    mean_returns = returns.mean() * 252
    covariance_matrix = returns.cov() * 252

    num_assets = len(mean_returns)
    asset_names = list(mean_returns.index)

    results = []

    best_sharpe = -np.inf
    best_weights = None

    rng = np.random.default_rng()

    for _ in range(num_portfolios):

        weights = rng.random(num_assets)
        weights /= np.sum(weights)

        portfolio_return = np.dot(
            weights,
            mean_returns
        )

        portfolio_volatility = np.sqrt(
            np.dot(
                weights.T,
                np.dot(covariance_matrix, weights)
            )
        )

        if portfolio_volatility <= 0:
            sharpe_ratio = 0
        else:
            sharpe_ratio = (
                portfolio_return - risk_free_rate
            ) / portfolio_volatility

        results.append({
            "return": float(portfolio_return),
            "risk": float(portfolio_volatility),
            "sharpe": float(sharpe_ratio)
        })

        if sharpe_ratio > best_sharpe:
            best_sharpe = sharpe_ratio
            best_weights = weights.copy()

    simulations = pd.DataFrame(results)

    # ------------------------------------------
    # IDENTIFY MAXIMUM SHARPE RATIO PORTFOLIO
    # ------------------------------------------

    optimal_portfolio = {
        "expected_return": float(
            np.dot(best_weights, mean_returns)
        ),
        "expected_volatility": float(
            np.sqrt(
                np.dot(
                    best_weights.T,
                    np.dot(covariance_matrix, best_weights)
                )
            )
        ),
        "sharpe_ratio": float(best_sharpe),
        "weights": {
            asset: float(weight)
            for asset, weight in zip(
                asset_names,
                best_weights
            )
        }
    }

    # ------------------------------------------
    # CALCULATE APPROXIMATE EFFICIENT FRONTIER
    # ------------------------------------------

    simulations_sorted = simulations.sort_values("risk")

    simulations_sorted["risk_group"] = pd.cut(
        simulations_sorted["risk"],
        bins=50,
        duplicates="drop"
    )

    efficient_frontier = (
        simulations_sorted
        .groupby("risk_group", observed=True)
        .agg({
            "risk": "mean",
            "return": "max"
        })
        .dropna()
        .sort_values("risk")
        .reset_index(drop=True)
    )

    frontier_data = [
        {
            "risk": float(row["risk"]),
            "return": float(row["return"])
        }
        for _, row in efficient_frontier.iterrows()
    ]

    return {
        "simulations": simulations.to_dict(
            orient="records"
        ),
        "efficient_frontier": frontier_data,
        "optimal_portfolio": optimal_portfolio,
        "assets": asset_names,
        "num_portfolios": num_portfolios
    }
