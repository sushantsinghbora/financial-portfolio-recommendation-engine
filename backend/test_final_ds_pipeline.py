import pprint

from app.database import SessionLocal

from app.models.portfolio import Portfolio
from app.models.holding import Holding

from app.services.ds_pipeline_service import (
    generate_ds_pipeline
)

from app.services.market_service import (
    get_historical_prices
)

from app.analytics.strategy_comparison import (
    compare_strategies,
    create_comparison_summary
)

from app.analytics.visualization import (
    plot_strategy_performance,
    plot_risk_return_comparison,
    plot_drawdown_comparison
)


# ==================================================
# CONFIGURATION
# ==================================================

USER_ID = 1

# Use the portfolio that contains holdings.
PORTFOLIO_ID = 3

RISK_PROFILE = "moderate"


# ==================================================
# DATABASE SESSION
# ==================================================

db = SessionLocal()


try:

    # ==================================================
    # FETCH PORTFOLIO
    # ==================================================

    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == PORTFOLIO_ID,
            Portfolio.user_id == USER_ID
        )
        .first()
    )

    if portfolio is None:
        raise ValueError(
            "Portfolio not found."
        )

    # ==================================================
    # FETCH HOLDINGS
    # ==================================================

    holdings = (
        db.query(Holding)
        .filter(
            Holding.portfolio_id == portfolio.id
        )
        .all()
    )

    if not holdings:
        raise ValueError(
            "Selected portfolio does not contain holdings."
        )

    symbols = [
        holding.stock_symbol.upper()
        for holding in holdings
    ]


    # ==================================================
    # HEADER
    # ==================================================

    print("\n")
    print("=" * 70)
    print("FINAL DATA SCIENCE PIPELINE")
    print("=" * 70)

    print(
        f"Portfolio: {portfolio.portfolio_name}"
    )

    print(
        f"Portfolio ID: {portfolio.id}"
    )

    print(
        f"Risk Profile: {RISK_PROFILE}"
    )

    print(
        f"Assets: {symbols}"
    )


    # ==================================================
    # STEP 1
    # PORTFOLIO DATA SCIENCE PIPELINE
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 1 — PORTFOLIO ANALYTICS + RECOMMENDATION")
    print("=" * 70)

    ds_result = generate_ds_pipeline(
        db=db,
        portfolio_id=PORTFOLIO_ID,
        user_id=USER_ID,
        risk_profile=RISK_PROFILE
    )

    pprint.pprint(
        ds_result,
        sort_dicts=False
    )


    # ==================================================
    # STEP 2
    # HISTORICAL MARKET DATA
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 2 — HISTORICAL MARKET DATA")
    print("=" * 70)

    prices = get_historical_prices(
        symbols,
        period="5y"
    )

    print(
        f"Observations: {len(prices)}"
    )

    print(
        f"Assets: {list(prices.columns)}"
    )

    print(
        f"Start Date: {prices.index[0].date()}"
    )

    print(
        f"End Date: {prices.index[-1].date()}"
    )


    # ==================================================
    # STEP 3
    # TRAIN / TEST SPLIT
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 3 — CHRONOLOGICAL TRAIN / TEST SPLIT")
    print("=" * 70)

    split_index = int(
        len(prices) * 0.80
    )

    train_data = prices.iloc[
        :split_index
    ].copy()

    test_data = prices.iloc[
        split_index:
    ].copy()

    print(
        f"Training observations: {len(train_data)}"
    )

    print(
        f"Testing observations: {len(test_data)}"
    )

    print(
        f"Training period: "
        f"{train_data.index[0].date()} "
        f"to "
        f"{train_data.index[-1].date()}"
    )

    print(
        f"Testing period: "
        f"{test_data.index[0].date()} "
        f"to "
        f"{test_data.index[-1].date()}"
    )


    # ==================================================
    # STEP 4
    # STRATEGY COMPARISON
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 4 — OUT-OF-SAMPLE STRATEGY COMPARISON")
    print("=" * 70)

    comparison_results = compare_strategies(
        train_data=train_data,
        test_data=test_data
    )

    summary = create_comparison_summary(
        comparison_results
    )

    print("\nPERFORMANCE SUMMARY")

    for row in summary:
        print(row)


    # ==================================================
    # STEP 5
    # BEST STRATEGY
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 5 — BEST OUT-OF-SAMPLE STRATEGY")
    print("=" * 70)

    best_strategy = max(
        summary,
        key=lambda row:
            row["sharpe_ratio"]
    )

    print(
        f"Best strategy: "
        f"{best_strategy['strategy']}"
    )

    print(
        f"Annualized return: "
        f"{best_strategy['annualized_return']}%"
    )

    print(
        f"Annualized volatility: "
        f"{best_strategy['annualized_volatility']}%"
    )

    print(
        f"Sharpe ratio: "
        f"{best_strategy['sharpe_ratio']}"
    )

    print(
        f"Maximum drawdown: "
        f"{best_strategy['maximum_drawdown']}%"
    )


    # ==================================================
    # STEP 6
    # VISUALIZATION — STRATEGY PERFORMANCE
    # ==================================================

    print("\n")
    print("=" * 70)
    print("STEP 6 — GENERATING VISUALIZATIONS")
    print("=" * 70)

    strategy_fig = plot_strategy_performance(
        comparison_results
    )

    strategy_fig.savefig(
        "final_strategy_performance.png",
        dpi=150,
        bbox_inches="tight"
    )

    strategy_fig.close()


    # ==================================================
    # STEP 7
    # VISUALIZATION — RISK RETURN
    # ==================================================

    risk_return_fig = (
        plot_risk_return_comparison(
            comparison_results
        )
    )

    risk_return_fig.savefig(
        "final_risk_return_comparison.png",
        dpi=150,
        bbox_inches="tight"
    )

    risk_return_fig.close()


    # ==================================================
    # STEP 8
    # VISUALIZATION — DRAWDOWN
    # ==================================================

    drawdown_fig = (
        plot_drawdown_comparison(
            comparison_results
        )
    )

    drawdown_fig.savefig(
        "final_drawdown_comparison.png",
        dpi=150,
        bbox_inches="tight"
    )

    drawdown_fig.close()


    print(
        "Strategy performance visualization: generated"
    )

    print(
        "Risk-return visualization: generated"
    )

    print(
        "Drawdown visualization: generated"
    )


    # ==================================================
    # FINAL RESULT
    # ==================================================

    print("\n")
    print("=" * 70)
    print("FINAL PIPELINE RESULT")
    print("=" * 70)

    print(
        f"Portfolio: "
        f"{portfolio.portfolio_name}"
    )

    print(
        f"Risk profile: "
        f"{RISK_PROFILE}"
    )

    print(
        f"Assets: "
        f"{symbols}"
    )

    print(
        f"Best strategy: "
        f"{best_strategy['strategy']}"
    )

    print(
        f"Out-of-sample return: "
        f"{best_strategy['annualized_return']}%"
    )

    print(
        f"Out-of-sample volatility: "
        f"{best_strategy['annualized_volatility']}%"
    )

    print(
        f"Out-of-sample Sharpe: "
        f"{best_strategy['sharpe_ratio']}"
    )

    print(
        f"Maximum drawdown: "
        f"{best_strategy['maximum_drawdown']}%"
    )

    print("\n")

    print("=" * 70)
    print("DATA SCIENCE PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


finally:

    # ==================================================
    # CLOSE DATABASE CONNECTION
    # ==================================================

    db.close()