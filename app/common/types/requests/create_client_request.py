from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from datetime import date
from typing import Any


class CreateClientRequest(BaseModel):
    """Request model for creating a new client."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name_1": "Andrew",
                "last_name_1": "Smith",
                "dob_1": "1980-05-15",
                "ssn_last4_1": "1234",
                "first_name_2": "Rebecca",
                "last_name_2": "Smith",
                "dob_2": "1982-03-20",
                "ssn_last4_2": "5678",
                "monthly_salary": 15000,
                "monthly_expense_budget": 5000,
                "insurance_deductibles_total": 5000
            }
        }
    )

    first_name_1: str = Field(..., min_length=1)
    last_name_1: str = Field(..., min_length=1)
    dob_1: date
    ssn_last4_1: str = Field(..., min_length=4, max_length=4)
    first_name_2: str | None = None
    last_name_2: str | None = None
    dob_2: date | None = None
    ssn_last4_2: str | None = Field(default=None, min_length=4, max_length=4)
    monthly_salary: float = Field(..., gt=0)
    monthly_expense_budget: float = Field(..., gt=0)
    insurance_deductibles_total: float = Field(default=0, ge=0)

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

    @field_validator("first_name_2", "last_name_2", "dob_2", "ssn_last4_2", mode="before")
    @classmethod
    def blank_optional_values_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
