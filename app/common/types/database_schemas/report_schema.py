from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from app.common.enums.report_status import ReportStatus


class ReportSchema(BaseModel):
    """Database schema for quarterly report records."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    report_date: date
    status: ReportStatus
    created_at: datetime
