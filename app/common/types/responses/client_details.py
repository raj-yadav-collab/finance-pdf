from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from app.common.enums.account_type import AccountType


class AccountInfo(BaseModel):
    """Detailed account information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_type: AccountType
    label: str
    account_last4: str | None
    interest_rate: float | None
    property_address: str | None
    display_order: int


class ClientDetails(BaseModel):
    """Full client details with accounts."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "first_name_1": "Andrew",
                "last_name_1": "Smith",
                "dob_1": "1980-05-15",
                "age_1": 44,
                "ssn_last4_1": "1234",
                "first_name_2": "Rebecca",
                "last_name_2": "Smith",
                "dob_2": "1982-03-20",
                "age_2": 42,
                "ssn_last4_2": "5678",
                "monthly_salary": 15000,
                "monthly_expense_budget": 5000,
                "insurance_deductibles_total": 5000,
                "accounts": []
            }
        },
    )

    id: int
    first_name_1: str
    last_name_1: str
    dob_1: date
    age_1: int
    ssn_last4_1: str
    first_name_2: str | None
    last_name_2: str | None
    dob_2: date | None
    age_2: int | None
    ssn_last4_2: str | None
    monthly_salary: float
    monthly_expense_budget: float
    insurance_deductibles_total: float
    accounts: list[AccountInfo] = Field(default_factory=list)
