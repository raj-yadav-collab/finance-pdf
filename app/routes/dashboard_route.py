from fastapi import APIRouter, Depends
from app.controllers.dashboard_controller import DashboardController
from app.utils.dependencies import get_dashboard_controller

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def get_dashboard(controller: DashboardController = Depends(get_dashboard_controller)):
    """Get dashboard summary."""
    return controller.get_dashboard()
