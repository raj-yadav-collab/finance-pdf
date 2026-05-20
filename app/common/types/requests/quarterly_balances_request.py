from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class AccountBalanceEntry(BaseModel):
    """Individual account balance entry within a quarterly report."""
    account_id: int = Field(..., gt=0)
    balance: float = Field(..., ge=0)
    cash_balance: float | None = Field(default=None, ge=0)  # investment accounts only
    balance_date: date | None = None  # defaults to report_date if omitted
    is_stale: bool = False  # True = red asterisk on TCC bubble


class QuarterlyBalancesRequest(BaseModel):
    """Request model for saving quarterly balance data."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_date": "2024-03-31",
                "private_reserve_balance": 75000,
                "schwab_investment_balance": 15000,
                "account_balances": [
                    {
                        "account_id": 1,
                        "balance": 45000,
                        "balance_date": "2024-03-31",
                        "is_stale": False
                    },
                    {
                        "account_id": 2,
                        "balance": 85000,
                        "balance_date": "2024-03-31",
                        "is_stale": False
                    }
                ]
            }
        }
    )

    report_date: date
    private_reserve_balance: float = Field(..., ge=0)
    schwab_investment_balance: float | None = None
    account_balances: list[AccountBalanceEntry] = Field(default_factory=list)
