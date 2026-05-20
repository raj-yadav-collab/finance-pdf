class ClientNotFoundError(Exception):
    """Raised when a client is not found in the database."""
    def __init__(self, client_id: int):
        self.client_id = client_id
        super().__init__(f"Client with id {client_id} not found")
