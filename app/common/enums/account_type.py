from enum import Enum


class AccountType(str, Enum):
    """Account type classification."""
    RETIREMENT_CLIENT_1 = "retirement_1"
    RETIREMENT_CLIENT_2 = "retirement_2"
    NON_RETIREMENT = "non_retirement"
    TRUST = "trust"
    LIABILITY = "liability"
    PRIVATE_RESERVE = "private_reserve"
