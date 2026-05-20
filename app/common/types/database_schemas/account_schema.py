from pydantic import BaseModel, ConfigDict
from app.common.enums.account_type import AccountType


class AccountSchema(BaseModel):
    """Database schema for account records."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    account_type: AccountType
    label: str
    account_last4: str | None
    interest_rate: float | None
    property_address: str | None
    display_order: int
    is_active: bool
