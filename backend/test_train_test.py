import pprint

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.backtesting import (
    run_train_test_backtest
)


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
# Run out-of-sample backtest
# --------------------------------------------------

result = run_train_test_backtest(
    price_data=prices,
    risk_profile="moderate",
    train_ratio=0.80
)

# --------------------------------------------------
# Display result
# --------------------------------------------------

print("\n")
print("=" * 60)
print("OUT-OF-SAMPLE BACKTEST")
print("=" * 60)

pprint.pprint(
    result,
    sort_dicts=False
)