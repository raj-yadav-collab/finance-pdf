from pydantic import BaseModel, ConfigDict
from datetime import date, datetime


class ClientSchema(BaseModel):
    """Database schema for client records."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name_1: str
    last_name_1: str
    dob_1: date
    ssn_last4_1: str
    first_name_2: str | None
    last_name_2: str | None
    dob_2: date | None
    ssn_last4_2: str | None
    monthly_salary: float
    monthly_expense_budget: float
    insurance_deductibles_total: float
    created_at: datetime
    updated_at: datetime
