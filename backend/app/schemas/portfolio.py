from typing import List

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# Holding schemas
# -----------------------------

class HoldingCreate(BaseModel):
    stock_symbol: str = Field(
        ...,
        min_length=1,
        max_length=20
    )
    quantity: float = Field(..., gt=0)
    buy_price: float = Field(..., gt=0)


class HoldingUpdate(BaseModel):
    stock_symbol: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )
    quantity: float | None = Field(default=None, gt=0)
    buy_price: float | None = Field(default=None, gt=0)


class HoldingResponse(BaseModel):
    id: int
    stock_symbol: str
    quantity: float
    buy_price: float
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Portfolio schemas
# -----------------------------

class PortfolioCreate(BaseModel):
    portfolio_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


class PortfolioUpdate(BaseModel):
    portfolio_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


class PortfolioResponse(BaseModel):
    id: int
    portfolio_name: str
    user_id: int
    holdings: List[HoldingResponse] = []

    model_config = ConfigDict(from_attributes=True)