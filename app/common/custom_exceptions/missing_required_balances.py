class MissingRequiredBalancesError(Exception):
    """Raised when required account balances are missing for report generation."""
    def __init__(self, missing_account_ids: list):
        self.missing_account_ids = missing_account_ids
        super().__init__(f"Missing balances for accounts: {missing_account_ids}")
