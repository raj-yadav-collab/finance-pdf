from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from datetime import date
from typing import Any


class UpdateClientRequest(BaseModel):
    """Request model for updating an existing client."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "monthly_salary": 16000,
                "monthly_expense_budget": 5200
            }
        }
    )

    first_name_1: str | None = Field(default=None, min_length=1)
    last_name_1: str | None = Field(default=None, min_length=1)
    dob_1: date | None = None
    ssn_last4_1: str | None = Field(default=None, min_length=4, max_length=4)
    first_name_2: str | None = None
    last_name_2: str | None = None
    dob_2: date | None = None
    ssn_last4_2: str | None = Field(default=None, min_length=4, max_length=4)
    monthly_salary: float | None = Field(default=None, gt=0)
    monthly_expense_budget: float | None = Field(default=None, gt=0)
    insurance_deductibles_total: float | None = Field(default=None, ge=0)

    @field_validator(
        "first_name_1",
        "last_name_1",
        "ssn_last4_1",
        "first_name_2",
        "last_name_2",
        "ssn_last4_2",
        mode="before",
    )
    @classmethod
    def trim_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator(
        "first_name_1",
        "last_name_1",
        "dob_1",
        "ssn_last4_1",
        "first_name_2",
        "last_name_2",
        "dob_2",
        "ssn_last4_2",
        mode="before",
    )
    @classmethod
    def blank_optional_values_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
