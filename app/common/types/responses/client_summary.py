from pydantic import BaseModel, ConfigDict
from datetime import date


class ClientSummary(BaseModel):
    """Summary information for a client in list view."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "display_name": "Andrew & Rebecca Smith",
                "last_report_date": "2024-03-31",
                "last_report_id": 5
            }
        },
    )

    id: int
    display_name: str  # "Andrew & Rebecca Smith"
    last_report_date: date | None
    last_report_id: int | None
