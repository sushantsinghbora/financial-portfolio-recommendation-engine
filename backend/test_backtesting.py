import numpy as np

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.backtesting import (
    evaluate_backtest
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
    period="1y"
)

# --------------------------------------------------
# Test allocation
# --------------------------------------------------

weights = np.array([
    0.50,
    0.50
])

# --------------------------------------------------
# Evaluate portfolio
# --------------------------------------------------

results = evaluate_backtest(
    price_data=prices,
    weights=weights
)

# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n")
print("=" * 60)
print("BACKTESTING TEST")
print("=" * 60)

print("\nAssets:")
print(symbols)

print("\nAllocation:")
print({
    "AAPL": "50%",
    "RELIANCE.NS": "50%"
})

print("\nPerformance:")
print(results)