from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class GenerateReportRequest(BaseModel):
    """Request model for initiating a new quarterly report."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_id": 1,
                "report_date": "2024-03-31"
            }
        }
    )

    client_id: int = Field(..., gt=0)
    report_date: date
