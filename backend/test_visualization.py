from app.services.monte_carlo import run_monte_carlo
from app.services.portfolio_visualization import (
    plot_efficient_frontier
)


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

fig = plot_efficient_frontier(
    simulations=result["simulations"],
    efficient_frontier=result["efficient_frontier"],
    max_sharpe_portfolio=result["max_sharpe_portfolio"],
    min_volatility_portfolio=result[
        "minimum_volatility_portfolio"
    ]
)

fig.savefig(
    "efficient_frontier.png",
    dpi=150
)

print(
    "Efficient frontier visualization generated successfully."
)