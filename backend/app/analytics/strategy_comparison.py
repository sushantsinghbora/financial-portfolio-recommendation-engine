import numpy as np
import pandas as pd

from app.services.recommendation_service import (
    optimize_portfolio
)

from app.analytics.backtesting import (
    evaluate_backtest
)


def compare_strategies(
    train_data: pd.DataFrame,
    test_data: pd.DataFrame
) -> dict:
    """
    Compare conservative, moderate and aggressive
    optimization strategies against an equal-weight
    benchmark using the same unseen test period.
    """

    if train_data.empty:
        raise ValueError(
            "Training data cannot be empty."
        )

    if test_data.empty:
        raise ValueError(
            "Testing data cannot be empty."
        )

    if list(train_data.columns) != list(
        test_data.columns
    ):
        raise ValueError(
            "Training and testing assets "
            "must be identical."
        )

    symbols = list(train_data.columns)

    results = {}

    # --------------------------------------------------
    # 1. Optimized risk-profile strategies
    # --------------------------------------------------

    for risk_profile in [
        "conservative",
        "moderate",
        "aggressive"
    ]:

        recommendation = optimize_portfolio(
            prices=train_data,
            risk_profile=risk_profile
        )

        allocation = recommendation[
            "recommended_allocation"
        ]

        weights = np.array([
            allocation[symbol] / 100
            for symbol in symbols
        ])

        performance = evaluate_backtest(
            price_data=test_data[symbols],
            weights=weights
        )

        results[risk_profile] = {
            "allocation": allocation,
            "optimization_metrics": (
                recommendation[
                    "optimization_metrics"
                ]
            ),
            "test_performance": performance
        }

    # --------------------------------------------------
    # 2. Equal-weight benchmark
    # --------------------------------------------------

    equal_weight = np.array(
        [1 / len(symbols)] * len(symbols)
    )

    benchmark_performance = (
        evaluate_backtest(
            price_data=test_data[symbols],
            weights=equal_weight
        )
    )

    benchmark_allocation = {
        symbol: round(
            100 / len(symbols),
            2
        )
        for symbol in symbols
    }

    results["equal_weight_benchmark"] = {
        "allocation": benchmark_allocation,
        "test_performance": benchmark_performance
    }

    return {
        "assets": symbols,
        "training_observations": len(
            train_data
        ),
        "testing_observations": len(
            test_data
        ),
        "strategies": results
    }


def create_comparison_summary(
    comparison_results: dict
) -> list[dict]:
    """
    Convert strategy comparison results into
    a compact tabular summary.
    """

    strategies = comparison_results["strategies"]

    summary = []

    for strategy_name, strategy_data in strategies.items():

        performance = strategy_data["test_performance"]

        summary.append({
            "strategy": strategy_name,
            "annualized_return": performance[
                "annualized_return"
            ],
            "annualized_volatility": performance[
                "annualized_volatility"
            ],
            "sharpe_ratio": performance[
                "sharpe_ratio"
            ],
            "maximum_drawdown": performance[
                "maximum_drawdown"
            ]
        })

    return summary
