import matplotlib.pyplot as plt


def plot_efficient_frontier(
    simulations,
    efficient_frontier,
    max_sharpe_portfolio,
    min_volatility_portfolio
):
    """
    Create an Efficient Frontier risk-return visualization.
    """

    # Extract simulation data
    volatility = [
        portfolio["volatility"]
        for portfolio in simulations
    ]

    returns = [
        portfolio["return"]
        for portfolio in simulations
    ]

    sharpe_ratios = [
        portfolio["sharpe_ratio"]
        for portfolio in simulations
    ]

    # Extract efficient frontier
    frontier_volatility = [
        portfolio["volatility"]
        for portfolio in efficient_frontier
    ]

    frontier_returns = [
        portfolio["return"]
        for portfolio in efficient_frontier
    ]

    # Maximum Sharpe
    max_sharpe_volatility = (
        max_sharpe_portfolio["volatility"]
    )

    max_sharpe_return = (
        max_sharpe_portfolio["expected_return"]
    )

    # Minimum volatility
    min_volatility = (
        min_volatility_portfolio["volatility"]
    )

    min_volatility_return = (
        min_volatility_portfolio["expected_return"]
    )

    # Create figure
    plt.figure(figsize=(12, 7))

    # Monte Carlo portfolios
    scatter = plt.scatter(
        volatility,
        returns,
        c=sharpe_ratios,
        alpha=0.35,
        s=10
    )

    # Efficient Frontier
    plt.plot(
        frontier_volatility,
        frontier_returns,
        linewidth=2
    )

    # Maximum Sharpe portfolio
    plt.scatter(
        max_sharpe_volatility,
        max_sharpe_return,
        marker="*",
        s=250,
        label="Maximum Sharpe"
    )

    # Minimum volatility portfolio
    plt.scatter(
        min_volatility,
        min_volatility_return,
        marker="X",
        s=150,
        label="Minimum Volatility"
    )

    # Labels
    plt.xlabel(
        "Annualized Volatility (%)"
    )

    plt.ylabel(
        "Expected Annual Return (%)"
    )

    plt.title(
        "Monte Carlo Portfolio Simulation & Efficient Frontier"
    )

    plt.colorbar(
        scatter,
        label="Sharpe Ratio"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    return plt.gcf()