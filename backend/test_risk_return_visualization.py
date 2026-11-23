import matplotlib.pyplot as plt

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.strategy_comparison import (
    compare_strategies
)

from app.analytics.visualization import (
    plot_risk_return_comparison
)


# ==================================================
# ASSETS
# ==================================================

symbols = [
    "AAPL",
    "RELIANCE.NS"
]


# ==================================================
# DOWNLOAD HISTORICAL DATA
# ==================================================

prices = get_historical_prices(
    symbols,
    period="5y"
)


# ==================================================
# 80/20 TRAIN-TEST SPLIT
# ==================================================

split_index = int(
    len(prices) * 0.80
)


train_data = prices.iloc[
    :split_index
].copy()


test_data = prices.iloc[
    split_index:
].copy()


# ==================================================
# STRATEGY COMPARISON
# ==================================================

comparison_results = compare_strategies(
    train_data=train_data,
    test_data=test_data
)


# ==================================================
# CREATE RISK-RETURN VISUALIZATION
# ==================================================

fig = plot_risk_return_comparison(
    comparison_results
)


# ==================================================
# SAVE VISUALIZATION
# ==================================================

fig.savefig(
    "risk_return_comparison.png",
    dpi=150,
    bbox_inches="tight"
)


# ==================================================
# DISPLAY VISUALIZATION
# ==================================================

plt.show()


print(
    "Risk-return visualization "
    "generated successfully."
)