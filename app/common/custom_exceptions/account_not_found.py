class AccountNotFoundError(Exception):
    """Raised when an account is not found in the database."""
    def __init__(self, account_id: int):
        self.account_id = account_id
        super().__init__(f"Account with id {account_id} not found")
