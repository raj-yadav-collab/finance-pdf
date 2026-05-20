class ReportNotFoundError(Exception):
    """Raised when a report is not found in the database."""
    def __init__(self, report_id: int):
        self.report_id = report_id
        super().__init__(f"Report with id {report_id} not found")
