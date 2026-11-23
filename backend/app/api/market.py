from fastapi import APIRouter, HTTPException

from app.services.market_service import get_stock_data

router = APIRouter(
    prefix="/market",
    tags=["Market Data"]
)


@router.get("/{symbol}")
def get_market_data(symbol: str):
    """
    Get live market data for a stock symbol.
    """

    stock = get_stock_data(symbol)

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Stock symbol not found."
        )

    return stock