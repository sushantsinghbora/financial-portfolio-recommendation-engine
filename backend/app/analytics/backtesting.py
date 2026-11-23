import numpy as np
import pandas as pd

from app.services.recommendation_service import (
    optimize_portfolio
)

TRADING_DAYS = 252


def calculate_portfolio_returns(
    price_data: pd.DataFrame,
    weights: np.ndarray
) -> pd.Series:
    """
    Calculate daily portfolio returns from
    historical prices and portfolio weights.
    """

    if price_data.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if len(price_data.columns) != len(weights):
        raise ValueError(
            "Number of weights must match "
            "number of assets."
        )

    daily_returns = (
        price_data
        .pct_change()
        .dropna()
    )

    portfolio_returns = daily_returns.dot(
        weights
    )

    return portfolio_returns


def calculate_cumulative_return(
    portfolio_returns: pd.Series
) -> float:
    """
    Calculate total compounded return
    over the backtesting period.
    """

    if portfolio_returns.empty:
        return 0.0

    cumulative_return = (
        (1 + portfolio_returns).prod() - 1
    )

    return float(cumulative_return)


def calculate_annualized_return(
    portfolio_returns: pd.Series
) -> float:
    """
    Calculate annualized compounded return.
    """

    if portfolio_returns.empty:
        return 0.0

    total_return = (
        (1 + portfolio_returns).prod()
    )

    number_of_days = len(portfolio_returns)

    annualized_return = (
        total_return
        ** (TRADING_DAYS / number_of_days)
    ) - 1

    return float(annualized_return)


def calculate_annualized_volatility(
    portfolio_returns: pd.Series
) -> float:
    """
    Calculate annualized portfolio volatility.
    """

    if portfolio_returns.empty:
        return 0.0

    volatility = (
        portfolio_returns.std()
        * np.sqrt(TRADING_DAYS)
    )

    return float(volatility)


def calculate_sharpe_ratio(
    portfolio_returns: pd.Series
) -> float:
    """
    Calculate annualized Sharpe ratio.

    Assumes a zero risk-free rate for simplicity.
    """

    annualized_return = (
        calculate_annualized_return(
            portfolio_returns
        )
    )

    annualized_volatility = (
        calculate_annualized_volatility(
            portfolio_returns
        )
    )

    if annualized_volatility == 0:
        return 0.0

    return float(
        annualized_return /
        annualized_volatility
    )


def calculate_maximum_drawdown(
    portfolio_returns: pd.Series
) -> float:
    """
    Calculate maximum portfolio drawdown.

    Returns a negative percentage value.
    """

    if portfolio_returns.empty:
        return 0.0

    cumulative_growth = (
        1 + portfolio_returns
    ).cumprod()

    running_maximum = (
        cumulative_growth.cummax()
    )

    drawdown = (
        cumulative_growth /
        running_maximum
    ) - 1

    maximum_drawdown = drawdown.min()

    return float(maximum_drawdown)



def evaluate_backtest(
    price_data: pd.DataFrame,
    weights: np.ndarray
) -> dict:
    """
    Evaluate a portfolio on historical test data.

    Returns performance metrics and cumulative
    portfolio growth for chart visualization.
    """

    portfolio_returns = calculate_portfolio_returns(
        price_data,
        weights
    )

    cumulative_return = calculate_cumulative_return(
        portfolio_returns
    )

    annualized_return = calculate_annualized_return(
        portfolio_returns
    )

    annualized_volatility = calculate_annualized_volatility(
        portfolio_returns
    )

    sharpe_ratio = calculate_sharpe_ratio(
        portfolio_returns
    )

    maximum_drawdown = calculate_maximum_drawdown(
        portfolio_returns
    )

    # Calculate cumulative growth from daily returns.
    cumulative_growth = (1 + portfolio_returns).cumprod()

    # Convert growth into percentage returns.
    cumulative_returns = (
        (cumulative_growth - 1) * 100
    )

    # Prepare date/value pairs for the dashboard.
    cumulative_returns_data = [
        {
            "date": str(index.date())
            if hasattr(index, "date")
            else str(index),
            "cumulative_return": float(round(value, 4))
        }
        for index, value in cumulative_returns.items()
    ]

    return {
        "cumulative_return": float(
            round(cumulative_return * 100, 2)
        ),
        "annualized_return": float(
            round(annualized_return * 100, 2)
        ),
        "annualized_volatility": float(
            round(annualized_volatility * 100, 2)
        ),
        "sharpe_ratio": float(
            round(sharpe_ratio, 3)
        ),
        "maximum_drawdown": float(
            round(maximum_drawdown * 100, 2)
        ),
        "cumulative_returns": cumulative_returns_data
    }




def run_train_test_backtest(
    price_data: pd.DataFrame,
    risk_profile: str = "moderate",
    train_ratio: float = 0.80
) -> dict:
    """
    Perform out-of-sample portfolio backtesting.

    The historical data is split chronologically into
    training and testing periods.

    The portfolio optimizer sees only the training data.
    The resulting allocation is then evaluated on the
    unseen testing data.
    """

    if price_data.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if not 0 < train_ratio < 1:
        raise ValueError(
            "train_ratio must be between 0 and 1."
        )

    # --------------------------------------------------
    # Ensure enough observations
    # --------------------------------------------------

    if len(price_data) < 30:
        raise ValueError(
            "At least 30 observations are required "
            "for train-test backtesting."
        )

    # --------------------------------------------------
    # Chronological train/test split
    # --------------------------------------------------

    split_index = int(
        len(price_data) * train_ratio
    )

    train_data = price_data.iloc[
        :split_index
    ].copy()

    test_data = price_data.iloc[
        split_index:
    ].copy()

    if train_data.empty or test_data.empty:
        raise ValueError(
            "Unable to create train-test split."
        )

    # --------------------------------------------------
    # Optimize using TRAINING data only
    # --------------------------------------------------

    recommendation = optimize_portfolio(
        prices=train_data,
        risk_profile=risk_profile
    )

    # --------------------------------------------------
    # Extract optimized allocation
    # --------------------------------------------------

    allocation = recommendation[
        "recommended_allocation"
    ]

    symbols = list(
        train_data.columns
    )

    weights = np.array([
        allocation[symbol] / 100
        for symbol in symbols
    ])

    # --------------------------------------------------
    # Evaluate ONLY on unseen TEST data
    # --------------------------------------------------

    test_performance = evaluate_backtest(
        price_data=test_data[
            symbols
        ],
        weights=weights
    )

    # --------------------------------------------------
    # Return complete backtest result
    # --------------------------------------------------

    return {
        "risk_profile": risk_profile,

        "train_ratio": train_ratio,

        "train_observations": len(
            train_data
        ),

        "test_observations": len(
            test_data
        ),

        "training_period": {
            "start": str(
                train_data.index[0].date()
            ),
            "end": str(
                train_data.index[-1].date()
            )
        },

        "testing_period": {
            "start": str(
                test_data.index[0].date()
            ),
            "end": str(
                test_data.index[-1].date()
            )
        },

        "recommended_allocation": allocation,

        "optimization_metrics": (
            recommendation[
                "optimization_metrics"
            ]
        ),

        "out_of_sample_performance": (
            test_performance
        )
    }