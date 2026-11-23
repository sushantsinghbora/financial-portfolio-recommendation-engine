from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.recommendation_service import (
    recommend_portfolio
)

from app.services.ds_pipeline_service import (
    generate_ds_pipeline
)

from app.models.user import User

from app.core.security import (
    get_current_user
)

from app.database import SessionLocal


from app.services.market_service import get_historical_prices

from app.analytics.backtesting import (
    run_train_test_backtest
)

from app.analytics.strategy_comparison import (
    compare_strategies,
    create_comparison_summary
)

from app.models.portfolio import Portfolio
from app.models.holding import Holding

from app.analytics.efficient_frontier import (
    generate_efficient_frontier
)



# ==================================================
# ROUTER
# ==================================================

router = APIRouter(
    prefix="/recommendation",
    tags=["Portfolio Recommendation"]
)


# ==================================================
# EXISTING STOCK RECOMMENDATION REQUEST
# ==================================================

class RecommendationRequest(BaseModel):
    symbols: list[str]
    risk_profile: str


# ==================================================
# EXISTING STOCK RECOMMENDATION API
# ==================================================

@router.post("/")
def get_recommendation(
    request: RecommendationRequest
):
    """
    Generate an optimized portfolio recommendation
    for a list of stocks.
    """

    try:

        result = recommend_portfolio(
            symbols=request.symbols,
            risk_profile=request.risk_profile
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Recommendation failed: {str(error)}"
        )


# ==================================================
# DATA SCIENCE PIPELINE REQUEST
# ==================================================

class DSPipelineRequest(BaseModel):
    portfolio_id: int
    risk_profile: str


# ==================================================
# COMPLETE DATA SCIENCE PIPELINE API
# ==================================================

@router.post("/portfolio")
def run_portfolio_ds_pipeline(
    request: DSPipelineRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run the complete Data Science pipeline
    for the authenticated user's portfolio.

    The user ID is obtained securely from
    the JWT authentication token.
    """

    db = SessionLocal()

    try:

        result = generate_ds_pipeline(
            db=db,
            portfolio_id=request.portfolio_id,
            user_id=current_user.id,
            risk_profile=request.risk_profile
        )

        # ------------------------------------------
        # Portfolio not found OR does not belong
        # to authenticated user
        # ------------------------------------------

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Portfolio not found."
            )

        return result

    except HTTPException:

        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Data Science pipeline failed: "
                f"{str(error)}"
            )
        )

    finally:

        db.close()


# ==================================================
# PORTFOLIO BACKTESTING API
# ==================================================

@router.post("/portfolio/backtest")
def backtest_portfolio(
    request: DSPipelineRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run out-of-sample backtesting for the
    authenticated user's portfolio.
    """

    db = SessionLocal()

    try:
        # 1. Verify portfolio ownership
        portfolio = (
            db.query(Portfolio)
            .filter(
                Portfolio.id == request.portfolio_id,
                Portfolio.user_id == current_user.id
            )
            .first()
        )

        if portfolio is None:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found."
            )

        # 2. Fetch holdings
        holdings = (
            db.query(Holding)
            .filter(
                Holding.portfolio_id == portfolio.id
            )
            .all()
        )

        if not holdings:
            raise HTTPException(
                status_code=400,
                detail="Portfolio does not contain any holdings."
            )

        # 3. Extract stock symbols
        symbols = [
            holding.stock_symbol.strip().upper()
            for holding in holdings
        ]

        # 4. Download historical prices
        price_data = get_historical_prices(symbols)

        if price_data.empty:
            raise ValueError(
                "Unable to retrieve historical market data."
            )

        # 5. Run existing backtesting logic
        result = run_train_test_backtest(
            price_data=price_data,
            risk_profile=request.risk_profile
        )

        # 6. Return results
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.portfolio_name,
            "backtest": result
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Backtesting failed: {str(error)}"
        )

    finally:
        db.close()


# ==================================================
# STRATEGY COMPARISON API
# ==================================================

@router.post("/portfolio/compare-strategies")
def compare_portfolio_strategies(
    request: DSPipelineRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Compare conservative, moderate, aggressive,
    and equal-weight strategies on the same
    out-of-sample test period.
    """

    db = SessionLocal()

    try:
        # 1. Verify portfolio ownership
        portfolio = (
            db.query(Portfolio)
            .filter(
                Portfolio.id == request.portfolio_id,
                Portfolio.user_id == current_user.id
            )
            .first()
        )

        if portfolio is None:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found."
            )

        # 2. Fetch holdings
        holdings = (
            db.query(Holding)
            .filter(
                Holding.portfolio_id == portfolio.id
            )
            .all()
        )

        if not holdings:
            raise HTTPException(
                status_code=400,
                detail="Portfolio does not contain any holdings."
            )

        # 3. Extract symbols
        symbols = [
            holding.stock_symbol.strip().upper()
            for holding in holdings
        ]

        # 4. Download historical prices
        price_data = get_historical_prices(symbols)

        if price_data.empty:
            raise ValueError(
                "Unable to retrieve historical market data."
            )

        # 5. Clean data and align stock prices
        price_data = price_data[symbols].dropna()

        if price_data.empty:
            raise ValueError(
                "No common historical price data is available."
            )

        # 6. Chronological 80/20 train-test split
        split_index = int(len(price_data) * 0.80)

        train_data = price_data.iloc[:split_index].copy()
        test_data = price_data.iloc[split_index:].copy()

        # 7. Compare strategies
        comparison_results = compare_strategies(
            train_data=train_data,
            test_data=test_data
        )

        # 8. Create table-ready summary
        summary = create_comparison_summary(
            comparison_results
        )

        # 9. Return complete results
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.portfolio_name,
            "training_period": {
                "start": str(train_data.index[0].date()),
                "end": str(train_data.index[-1].date())
            },
            "testing_period": {
                "start": str(test_data.index[0].date()),
                "end": str(test_data.index[-1].date())
            },
            "comparison": comparison_results,
            "summary": summary
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Strategy comparison failed: {str(error)}"
        )

    finally:
        db.close()


# ==================================================
# EFFICIENT FRONTIER API
# ==================================================

@router.post("/portfolio/efficient-frontier")
def get_portfolio_efficient_frontier(
    request: DSPipelineRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate Monte Carlo portfolio simulations
    and identify the maximum Sharpe ratio portfolio.
    """

    db = SessionLocal()

    try:
        # 1. Verify portfolio ownership
        portfolio = (
            db.query(Portfolio)
            .filter(
                Portfolio.id == request.portfolio_id,
                Portfolio.user_id == current_user.id
            )
            .first()
        )

        if portfolio is None:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found."
            )

        # 2. Fetch holdings
        holdings = (
            db.query(Holding)
            .filter(
                Holding.portfolio_id == portfolio.id
            )
            .all()
        )

        if not holdings:
            raise HTTPException(
                status_code=400,
                detail="Portfolio does not contain any holdings."
            )

        # 3. Extract stock symbols
        symbols = [
            holding.stock_symbol.strip().upper()
            for holding in holdings
        ]

        # 4. Download historical prices
        price_data = get_historical_prices(symbols)

        if price_data.empty:
            raise ValueError(
                "Unable to retrieve historical market data."
            )

        # 5. Clean and align price data
        price_data = price_data[symbols].dropna()

        if price_data.empty:
            raise ValueError(
                "No common historical price data is available."
            )

        # 6. Generate Efficient Frontier
        result = generate_efficient_frontier(
            historical_prices=price_data,
            num_portfolios=10000
        )

        # 7. Return results
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.portfolio_name,
            "efficient_frontier": result
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Efficient Frontier generation failed: "
                f"{str(error)}"
            )
        )

    finally:
        db.close()


