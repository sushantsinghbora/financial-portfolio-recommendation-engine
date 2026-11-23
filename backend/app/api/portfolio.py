from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.holding import Holding
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse
)
from app.core.security import get_current_user
from app.services import portfolio_service
from app.services.portfolio_analysis_service import (
    calculate_live_portfolio
)
from app.services.portfolio_analytics_service import (
    generate_portfolio_analytics
)

from fastapi import APIRouter

from app.services.portfolio_optimizer import optimize_portfolio

router = APIRouter()
router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PortfolioResponse)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return portfolio_service.create_portfolio(
        db=db,
        current_user=current_user,
        portfolio_data=portfolio
    )

@router.get("/", response_model=list[PortfolioResponse])
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return portfolio_service.get_portfolios(
        db=db,
        current_user=current_user
    )

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        .first()
    )

    if not db_portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    db_portfolio.portfolio_name = portfolio.portfolio_name

    db.commit()
    db.refresh(db_portfolio)

    return db_portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        .first()
    )

    if not db_portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    db.delete(db_portfolio)
    db.commit()

    return {
        "message": "Portfolio deleted successfully"
    }

@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingResponse
)
def add_holding(
    portfolio_id: int,
    holding: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        .first()
    )

    if not db_portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    new_holding = Holding(
        stock_symbol=holding.stock_symbol.upper(),
        quantity=holding.quantity,
        buy_price=holding.buy_price,
        portfolio_id=db_portfolio.id
    )

    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)

    return new_holding

@router.get(
    "/{portfolio_id}/holdings",
    response_model=list[HoldingResponse]
)
def get_holdings(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    holdings = (
        db.query(Holding)
        .filter(Holding.portfolio_id == portfolio.id)
        .all()
    )

    return holdings


@router.delete("/{portfolio_id}/holdings/{holding_id}")
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify portfolio belongs to the logged-in user
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    # Find the holding inside this portfolio
    holding = (
        db.query(Holding)
        .filter(
            Holding.id == holding_id,
            Holding.portfolio_id == portfolio_id
        )
        .first()
    )

    if not holding:
        raise HTTPException(
            status_code=404,
            detail="Holding not found"
        )

    db.delete(holding)
    db.commit()

    return {
        "message": "Holding deleted successfully",
        "holding_id": holding_id
    }


@router.get("/{portfolio_id}/live")
def get_live_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return live valuation and profit/loss for a portfolio.
    """

    result = calculate_live_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        user_id=current_user.id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    return result


@router.get("/{portfolio_id}/analytics")
def get_portfolio_analytics(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        result = generate_portfolio_analytics(
            db=db,
            portfolio_id=portfolio_id,
            user_id=current_user.id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found"
            )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




@router.get("/test-optimizer")
def test_optimizer():

    symbols = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA"
    ]

    return optimize_portfolio(symbols)