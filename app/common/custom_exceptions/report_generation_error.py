class ReportGenerationError(Exception):
    """Raised when PDF report generation fails."""
    def __init__(self, report_id: int, message: str = "PDF generation failed"):
        self.report_id = report_id
        super().__init__(f"Report generation failed for report_id {report_id}: {message}")
