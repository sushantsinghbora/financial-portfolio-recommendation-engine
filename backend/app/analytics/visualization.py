import matplotlib.pyplot as plt


# ==================================================
# STRATEGY PERFORMANCE
# ==================================================

def plot_strategy_performance(
    comparison_results: dict
):
    """
    Plot annualized return for each strategy.

    Parameters
    ----------
    comparison_results : dict
        Output from compare_strategies().

    Returns
    -------
    matplotlib.figure.Figure
        Strategy performance chart.
    """

    strategies = comparison_results[
        "strategies"
    ]

    strategy_names = []
    annualized_returns = []

    for strategy_name, strategy_data in strategies.items():

        strategy_names.append(
            strategy_name.replace(
                "_",
                " "
            ).title()
        )

        annualized_returns.append(
            strategy_data[
                "test_performance"
            ][
                "annualized_return"
            ]
        )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    ax.bar(
        strategy_names,
        annualized_returns
    )

    ax.set_title(
        "Out-of-Sample Strategy Performance"
    )

    ax.set_xlabel(
        "Strategy"
    )

    ax.set_ylabel(
        "Annualized Return (%)"
    )

    ax.grid(
        axis="y",
        alpha=0.3
    )

    plt.xticks(
        rotation=20
    )

    fig.tight_layout()

    return fig


# ==================================================
# RISK-RETURN COMPARISON
# ==================================================

def plot_risk_return_comparison(
    comparison_results: dict
):
    """
    Plot annualized return against annualized
    volatility for each investment strategy.

    Sharpe ratio is displayed next to each
    strategy for additional interpretation.

    Parameters
    ----------
    comparison_results : dict
        Output from compare_strategies().

    Returns
    -------
    matplotlib.figure.Figure
        Risk-return scatter plot.
    """

    strategies = comparison_results[
        "strategies"
    ]

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    for strategy_name, strategy_data in strategies.items():

        performance = strategy_data[
            "test_performance"
        ]

        volatility = performance[
            "annualized_volatility"
        ]

        annual_return = performance[
            "annualized_return"
        ]

        sharpe = performance[
            "sharpe_ratio"
        ]

        label = (
            strategy_name
            .replace(
                "_",
                " "
            )
            .title()
        )

        # ------------------------------------------
        # Plot strategy
        # ------------------------------------------

        ax.scatter(
            volatility,
            annual_return,
            s=120
        )

        # ------------------------------------------
        # Add strategy label
        # ------------------------------------------

        ax.annotate(
            f"{label}\n"
            f"Sharpe: {sharpe}",
            (
                volatility,
                annual_return
            ),
            xytext=(
                8,
                8
            ),
            textcoords="offset points"
        )

    # ----------------------------------------------
    # Chart labels
    # ----------------------------------------------

    ax.set_title(
        "Out-of-Sample Risk-Return Comparison"
    )

    ax.set_xlabel(
        "Annualized Volatility (%)"
    )

    ax.set_ylabel(
        "Annualized Return (%)"
    )

    ax.grid(
        alpha=0.3
    )

    fig.tight_layout()

    return fig


# ==================================================
# MAXIMUM DRAWDOWN COMPARISON
# ==================================================

def plot_drawdown_comparison(
    comparison_results: dict
):
    """
    Plot maximum drawdown for each strategy.

    More negative values indicate larger
    historical losses from peak to trough.
    """

    strategies = comparison_results[
        "strategies"
    ]

    strategy_names = []
    drawdowns = []

    for strategy_name, strategy_data in strategies.items():

        strategy_names.append(
            strategy_name.replace(
                "_",
                " "
            ).title()
        )

        drawdowns.append(
            strategy_data[
                "test_performance"
            ][
                "maximum_drawdown"
            ]
        )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    ax.bar(
        strategy_names,
        drawdowns
    )

    ax.set_title(
        "Maximum Drawdown Comparison"
    )

    ax.set_xlabel(
        "Strategy"
    )

    ax.set_ylabel(
        "Maximum Drawdown (%)"
    )

    ax.grid(
        axis="y",
        alpha=0.3
    )

    plt.xticks(
        rotation=20
    )

    fig.tight_layout()

    return fig