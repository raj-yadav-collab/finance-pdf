from pydantic import BaseModel, ConfigDict


class SACSCalculation(BaseModel):
    """SACS (Simple Automated Cash Flow System) calculation results."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inflow": 15000,
                "outflow": 5000,
                "excess": 10000,
                "private_reserve_balance": 75000,
                "private_reserve_target": 35000,
                "schwab_investment_balance": 15000
            }
        }
    )

    inflow: float
    outflow: float
    excess: float  # inflow - outflow
    private_reserve_balance: float
    private_reserve_target: float
    schwab_investment_balance: float | None


class TCCCalculation(BaseModel):
    """TCC (Total Client Chart) calculation results."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_1_retirement_total": 150000,
                "client_2_retirement_total": 120000,
                "non_retirement_total": 250000,
                "trust_total": 100000,
                "grand_total": 620000,
                "liabilities_total": 250000,
                "account_balances": {
                    "1": 45000,
                    "2": 85000
                }
            }
        }
    )

    client_1_retirement_total: float
    client_2_retirement_total: float | None
    non_retirement_total: float
    trust_total: float
    grand_total: float
    liabilities_total: float
    account_balances: dict[int, float]  # account_id -> balance


class CalculationPreview(BaseModel):
    """Live calculation preview combining SACS and TCC results."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sacs": {
                    "inflow": 15000,
                    "outflow": 5000,
                    "excess": 10000,
                    "private_reserve_balance": 75000,
                    "private_reserve_target": 35000,
                    "schwab_investment_balance": 15000
                },
                "tcc": {
                    "client_1_retirement_total": 150000,
                    "client_2_retirement_total": 120000,
                    "non_retirement_total": 250000,
                    "trust_total": 100000,
                    "grand_total": 620000,
                    "liabilities_total": 250000,
                    "account_balances": {}
                }
            }
        }
    )

    sacs: SACSCalculation
    tcc: TCCCalculation
