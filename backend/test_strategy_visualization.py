import matplotlib.pyplot as plt

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.strategy_comparison import (
    compare_strategies
)

from app.analytics.visualization import (
    plot_strategy_performance
)


# --------------------------------------------------
# Assets
# --------------------------------------------------

symbols = [
    "AAPL",
    "RELIANCE.NS"
]


# --------------------------------------------------
# Download historical data
# --------------------------------------------------

prices = get_historical_prices(
    symbols,
    period="5y"
)


# --------------------------------------------------
# 80/20 chronological train-test split
# --------------------------------------------------

split_index = int(
    len(prices) * 0.80
)

train_data = prices.iloc[
    :split_index
].copy()

test_data = prices.iloc[
    split_index:
].copy()


# --------------------------------------------------
# Compare investment strategies
# --------------------------------------------------

comparison_results = compare_strategies(
    train_data=train_data,
    test_data=test_data
)


# --------------------------------------------------
# Create strategy performance chart
# --------------------------------------------------

fig = plot_strategy_performance(
    comparison_results
)


# --------------------------------------------------
# Save visualization
# --------------------------------------------------

fig.savefig(
    "strategy_performance.png",
    dpi=150,
    bbox_inches="tight"
)


# --------------------------------------------------
# Display chart
# --------------------------------------------------

plt.show()


print(
    "Strategy performance visualization "
    "generated successfully."
)