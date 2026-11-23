from app.services.recommendation_service import (
    recommend_portfolio
)


symbols = [
    "AAPL",
    "MSFT",
    "NVDA",
    "TSLA"
]


for profile in [
    "conservative",
    "moderate",
    "aggressive"
]:

    result = recommend_portfolio(
        symbols,
        profile
    )

    print("\n")
    print("=" * 50)
    print(
        f"{profile.upper()} PORTFOLIO"
    )
    print("=" * 50)

    print(
        result
    )