import pandas as pd


def calculate_correlation_matrix(
    price_data: pd.DataFrame
):
    """
    Calculate the correlation matrix
    using daily stock returns.
    """

    if price_data.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    daily_returns = (
        price_data
        .pct_change()
        .dropna()
    )

    correlation_matrix = (
        daily_returns.corr()
    )

    return correlation_matrix