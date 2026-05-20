class DuplicateReportError(Exception):
    """Raised when a draft report already exists for a client in a quarter."""
    def __init__(self, client_id: int, report_date: str):
        self.client_id = client_id
        self.report_date = report_date
        super().__init__(f"Draft report already exists for client {client_id} on {report_date}")
