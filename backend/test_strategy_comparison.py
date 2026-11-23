import pprint

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.strategy_comparison import (
    compare_strategies,
    create_comparison_summary
)


symbols = [
    "AAPL",
    "RELIANCE.NS"
]


prices = get_historical_prices(
    symbols,
    period="5y"
)


split_index = int(
    len(prices) * 0.80
)


train_data = prices.iloc[
    :split_index
].copy()


test_data = prices.iloc[
    split_index:
].copy()


results = compare_strategies(
    train_data=train_data,
    test_data=test_data
)


summary = create_comparison_summary(
    results
)


# --------------------------------------------------
# Performance Summary
# --------------------------------------------------

print("\n")
print("=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)


for row in summary:
    print(row)


# --------------------------------------------------
# Detailed Strategy Comparison
# --------------------------------------------------

print("\n")
print("=" * 60)
print("STRATEGY COMPARISON")
print("=" * 60)


pprint.pprint(
    results,
    sort_dicts=False
)