from typing import Any

from app.common.types.database_schemas.account_schema import AccountSchema
from app.common.types.responses.calculation_preview import (
    SACSCalculation,
    TCCCalculation,
)
from app.common.enums.account_type import AccountType
from app.common.constants.common import PRIVATE_RESERVE_MULTIPLIER


def _get_account_field(account: AccountSchema | dict[str, Any], field_name: str) -> Any:
    if isinstance(account, dict):
        return account[field_name]
    return getattr(account, field_name)


class CalculationService:
    """Service for all financial calculations (SACS and TCC)."""
    
    @staticmethod
    def calculate_sacs(
        inflow: float,
        outflow: float,
        private_reserve_balance: float,
        insurance_deductibles_total: float,
        schwab_investment_balance: float | None = None,
    ) -> SACSCalculation:
        """
        Calculate SACS (Simple Automated Cash Flow System) metrics.
        
        Args:
            inflow: Monthly after-tax income
            outflow: Monthly expense budget
            private_reserve_balance: Current private reserve balance
            insurance_deductibles_total: Total insurance deductibles
            schwab_investment_balance: Optional investment account balance
        
        Returns:
            SACSCalculation with all computed values
        """
        excess = inflow - outflow
        private_reserve_target = (
            PRIVATE_RESERVE_MULTIPLIER * outflow + insurance_deductibles_total
        )
        
        return SACSCalculation(
            inflow=inflow,
            outflow=outflow,
            excess=excess,
            private_reserve_balance=private_reserve_balance,
            private_reserve_target=private_reserve_target,
            schwab_investment_balance=schwab_investment_balance,
        )
    
    @staticmethod
    def calculate_tcc(
        accounts: list[AccountSchema | dict[str, Any]], balances: dict[int, float]
    ) -> TCCCalculation:
        """
        Calculate TCC (Total Client Chart) metrics.
        
        Args:
            accounts: List of account schemas
            balances: Dict mapping account_id to balance amount
        
        Returns:
            TCCCalculation with all computed net worth totals
        """
        client_1_retirement_total = 0.0
        client_2_retirement_total = 0.0
        non_retirement_total = 0.0
        trust_total = 0.0
        liabilities_total = 0.0
        
        for account in accounts:
            account_id = _get_account_field(account, "id")
            if account_id not in balances:
                continue
            
            balance = balances[account_id]
            account_type = AccountType(_get_account_field(account, "account_type"))
            
            if account_type == AccountType.RETIREMENT_CLIENT_1:
                client_1_retirement_total += balance
            elif account_type == AccountType.RETIREMENT_CLIENT_2:
                client_2_retirement_total += balance
            elif account_type == AccountType.NON_RETIREMENT:
                non_retirement_total += balance
            elif account_type == AccountType.TRUST:
                trust_total += balance
            elif account_type == AccountType.LIABILITY:
                liabilities_total += balance
        
        # Grand total includes all asset types, but NOT liabilities (shown separately)
        grand_total = (
            client_1_retirement_total
            + (client_2_retirement_total or 0)
            + non_retirement_total
            + trust_total
        )
        
        return TCCCalculation(
            client_1_retirement_total=client_1_retirement_total,
            client_2_retirement_total=client_2_retirement_total or None,
            non_retirement_total=non_retirement_total,
            trust_total=trust_total,
            grand_total=grand_total,
            liabilities_total=liabilities_total,
            account_balances=balances,
        )
    
    @staticmethod
    def validate_completeness(
        required_account_ids: list[int], entered_balances: dict[int, float]
    ) -> list[int]:
        """
        Validate that all required account balances have been entered.
        
        Args:
            required_account_ids: List of account IDs that must have balances
            entered_balances: Dict of account_id -> balance that have been entered
        
        Returns:
            List of missing account IDs (empty if all present)
        """
        missing = []
        for account_id in required_account_ids:
            if account_id not in entered_balances or entered_balances[account_id] is None:
                missing.append(account_id)
        return missing


def calculate_sacs(
    inflow: float,
    outflow: float,
    private_reserve_balance: float,
    insurance_deductibles_total: float,
    schwab_investment_balance: float | None = None,
) -> SACSCalculation:
    return CalculationService.calculate_sacs(
        inflow,
        outflow,
        private_reserve_balance,
        insurance_deductibles_total,
        schwab_investment_balance,
    )


def calculate_tcc(
    accounts: list[AccountSchema | dict[str, Any]], balances: dict[int, float]
) -> TCCCalculation:
    return CalculationService.calculate_tcc(accounts, balances)


def validate_completeness(
    required_account_ids: list[int], entered_balances: dict[int, float]
) -> list[int]:
    return CalculationService.validate_completeness(required_account_ids, entered_balances)
