import numpy as np

from app.services.market_service import get_historical_prices


def calculate_efficient_frontier(simulations):
    """
    Identify portfolios that form the efficient frontier.

    A portfolio is considered efficient if no previously
    encountered portfolio has lower or equal risk with
    a higher return.
    """

    sorted_simulations = sorted(
        simulations,
        key=lambda x: x["volatility"]
    )

    efficient_portfolios = []

    highest_return = -float("inf")

    for portfolio in sorted_simulations:

        if portfolio["return"] > highest_return:

            efficient_portfolios.append(portfolio)

            highest_return = portfolio["return"]

    return efficient_portfolios


def run_monte_carlo(
    symbols: list[str],
    num_simulations: int = 10000
):
    """
    Run Monte Carlo portfolio simulation.

    Parameters
    ----------
    symbols : list[str]
        Stock symbols.

    num_simulations : int
        Number of random portfolios to generate.

    Returns
    -------
    dict
        Simulated portfolios, maximum Sharpe portfolio,
        minimum volatility portfolio and efficient frontier.
    """

    # --------------------------------------------------
    # 1. Download historical prices
    # --------------------------------------------------

    prices = get_historical_prices(symbols)

    if prices.empty:
        raise ValueError(
            "No historical price data found."
        )

    # --------------------------------------------------
    # 2. Calculate daily returns
    # --------------------------------------------------

    daily_returns = prices.pct_change().dropna()

    # --------------------------------------------------
    # 3. Annualized statistics
    # --------------------------------------------------

    mean_returns = daily_returns.mean() * 252

    covariance_matrix = (
        daily_returns.cov() * 252
    )

    # --------------------------------------------------
    # 4. Portfolio configuration
    # --------------------------------------------------

    num_assets = len(symbols)

    # Store:
    # Column 0 -> Return
    # Column 1 -> Volatility
    # Column 2 -> Sharpe Ratio

    results = np.zeros(
        (num_simulations, 3)
    )

    weights_record = []

    # --------------------------------------------------
    # 5. Generate random portfolios
    # --------------------------------------------------

    for i in range(num_simulations):

        while True:

            # Generate random weights
            weights = np.random.random(
                num_assets
            )

            # Normalize weights
            weights = (
                weights /
                np.sum(weights)
            )

            # Maximum 40% allocation
            # to any individual stock
            if np.all(weights <= 0.40):
                break

        weights_record.append(weights)

        # --------------------------------------------------
        # Portfolio expected return
        # --------------------------------------------------

        portfolio_return = np.sum(
            mean_returns * weights
        )

        # --------------------------------------------------
        # Portfolio volatility
        # --------------------------------------------------

        portfolio_volatility = np.sqrt(
            np.dot(
                weights.T,
                np.dot(
                    covariance_matrix,
                    weights
                )
            )
        )

        # --------------------------------------------------
        # Sharpe ratio
        # --------------------------------------------------

        if portfolio_volatility == 0:

            sharpe_ratio = 0

        else:

            sharpe_ratio = (
                portfolio_return /
                portfolio_volatility
            )

        # Store results
        results[i, 0] = portfolio_return
        results[i, 1] = portfolio_volatility
        results[i, 2] = sharpe_ratio

    # --------------------------------------------------
    # 6. Find maximum Sharpe portfolio
    # --------------------------------------------------

    max_sharpe_index = np.argmax(
        results[:, 2]
    )

    max_sharpe_weights = (
        weights_record[max_sharpe_index]
    )

    # --------------------------------------------------
    # 7. Find minimum volatility portfolio
    # --------------------------------------------------

    min_volatility_index = np.argmin(
        results[:, 1]
    )

    min_volatility_weights = (
        weights_record[min_volatility_index]
    )

    # --------------------------------------------------
    # 8. Convert simulations into readable records
    # --------------------------------------------------

    simulations = []

    for i in range(num_simulations):

        simulations.append(
            {
                "return": float(
                    round(
                        results[i, 0] * 100,
                        2
                    )
                ),

                "volatility": float(
                    round(
                        results[i, 1] * 100,
                        2
                    )
                ),

                "sharpe_ratio": float(
                    round(
                        results[i, 2],
                        3
                    )
                )
            }
        )

    # --------------------------------------------------
    # 9. Calculate efficient frontier
    # --------------------------------------------------

    efficient_frontier = (
        calculate_efficient_frontier(
            simulations
        )
    )

    # --------------------------------------------------
    # 10. Return complete analysis
    # --------------------------------------------------

    return {

        # ----------------------------------------------
        # Maximum Sharpe Portfolio
        # ----------------------------------------------

        "max_sharpe_portfolio": {

            "weights": {
                symbol: float(
                    round(
                        weight * 100,
                        2
                    )
                )
                for symbol, weight in zip(
                    symbols,
                    max_sharpe_weights
                )
            },

            "expected_return": float(
                round(
                    results[
                        max_sharpe_index,
                        0
                    ] * 100,
                    2
                )
            ),

            "volatility": float(
                round(
                    results[
                        max_sharpe_index,
                        1
                    ] * 100,
                    2
                )
            ),

            "sharpe_ratio": float(
                round(
                    results[
                        max_sharpe_index,
                        2
                    ],
                    3
                )
            )
        },

        # ----------------------------------------------
        # Minimum Volatility Portfolio
        # ----------------------------------------------

        "minimum_volatility_portfolio": {

            "weights": {
                symbol: float(
                    round(
                        weight * 100,
                        2
                    )
                )
                for symbol, weight in zip(
                    symbols,
                    min_volatility_weights
                )
            },

            "expected_return": float(
                round(
                    results[
                        min_volatility_index,
                        0
                    ] * 100,
                    2
                )
            ),

            "volatility": float(
                round(
                    results[
                        min_volatility_index,
                        1
                    ] * 100,
                    2
                )
            ),

            "sharpe_ratio": float(
                round(
                    results[
                        min_volatility_index,
                        2
                    ],
                    3
                )
            )
        },

        # ----------------------------------------------
        # All Monte Carlo simulations
        # ----------------------------------------------

        "simulations": simulations,

        # ----------------------------------------------
        # Efficient Frontier
        # ----------------------------------------------

        "efficient_frontier": efficient_frontier
    }


# ------------------------------------------------------
# Local testing
# ------------------------------------------------------

if __name__ == "__main__":

    symbols = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA"
    ]

    result = run_monte_carlo(
        symbols,
        num_simulations=10000
    )

    print(
        "\nMaximum Sharpe Portfolio:"
    )

    print(
        result["max_sharpe_portfolio"]
    )

    print(
        "\nMinimum Volatility Portfolio:"
    )

    print(
        result["minimum_volatility_portfolio"]
    )

    print(
        "\nNumber of Simulations:"
    )

    print(
        len(result["simulations"])
    )

    print(
        "\nEfficient Frontier Portfolios:"
    )

    print(
        len(result["efficient_frontier"])
    )