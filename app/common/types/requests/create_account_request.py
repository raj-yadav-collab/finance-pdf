from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.common.enums.account_type import AccountType


class CreateAccountRequest(BaseModel):
    """Request model for creating a new account."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_type": "retirement_1",
                "label": "Roth IRA",
                "account_last4": "1234",
                "display_order": 0
            }
        }
    )

    account_type: AccountType
    label: str = Field(..., min_length=1)
    account_last4: str | None = Field(default=None, min_length=4, max_length=4)
    interest_rate: float | None = None  # liabilities only
    property_address: str | None = None  # trust only
    display_order: int = 0

    @field_validator("label", "account_last4", "property_address", mode="before")
    @classmethod
    def trim_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator("account_last4", "property_address", mode="before")
    @classmethod
    def blank_optional_values_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
