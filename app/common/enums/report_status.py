from enum import Enum


class ReportStatus(str, Enum):
    """Report status classification."""
    DRAFT = "draft"
    FINAL = "final"
