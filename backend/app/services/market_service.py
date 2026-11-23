import yfinance as yf
import pandas as pd


def get_stock_data(symbol: str):
    """
    Fetch the latest market information for a stock symbol.
    """

    # Convert symbols such as aapl to AAPL
    symbol = symbol.strip().upper()

    if not symbol:
        return None

    try:
        stock = yf.Ticker(symbol)

        # Fetch recent price history.
        # This also helps verify whether the symbol is valid.
        history = stock.history(period="5d")

        if history.empty:
            return None

        latest_price = float(history["Close"].iloc[-1])

        # Use the previous trading day's closing price when available.
        if len(history) >= 2:
            previous_close = float(history["Close"].iloc[-2])
        else:
            previous_close = latest_price

        price_change = latest_price - previous_close

        if previous_close != 0:
            price_change_percent = (
                price_change / previous_close
            ) * 100
        else:
            price_change_percent = 0

        # Fetch additional company information.
        info = stock.info

        return {
            "symbol": symbol,
            "company_name": info.get(
                "longName",
                info.get("shortName", symbol)
            ),
            "current_price": round(latest_price, 2),
            "previous_close": round(previous_close, 2),
            "price_change": round(price_change, 2),
            "price_change_percent": round(
                price_change_percent,
                2
            ),
            "currency": info.get("currency"),
            "exchange": info.get("exchange"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_high": info.get(
                "fiftyTwoWeekHigh"
            ),
            "fifty_two_week_low": info.get(
                "fiftyTwoWeekLow"
            )
        }

    except Exception as error:
        print(
            f"Error fetching market data for "
            f"{symbol}: {error}"
        )
        return None


def get_historical_prices(
    symbols: list[str],
    period: str = "5y"
) -> pd.DataFrame:
    """
    Download historical adjusted closing prices
    for multiple stocks.
    """

    symbols = [
        symbol.strip().upper()
        for symbol in symbols
    ]

    data = yf.download(
        symbols,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if data.empty:
        raise ValueError(
            "Unable to download historical market data."
        )

    # Keep only closing prices
    prices = data["Close"]

    # Remove rows containing missing values
    prices = prices.dropna()

    return prices
