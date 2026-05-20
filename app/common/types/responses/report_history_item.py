from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from app.common.enums.report_status import ReportStatus


class ReportHistoryItem(BaseModel):
    """Individual report in history list."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 5,
                "report_date": "2024-03-31",
                "status": "final",
                "created_at": "2024-04-01T10:30:00"
            }
        },
    )

    id: int
    report_date: date
    status: ReportStatus
    created_at: datetime
