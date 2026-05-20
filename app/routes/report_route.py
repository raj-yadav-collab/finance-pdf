from fastapi import APIRouter, Depends
from app.controllers.report_controller import ReportController
from app.common.types.requests.generate_report_request import GenerateReportRequest
from app.common.types.requests.quarterly_balances_request import QuarterlyBalancesRequest
from app.utils.dependencies import get_report_controller

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/initiate")
async def initiate_report(
    request: GenerateReportRequest, controller: ReportController = Depends(get_report_controller)
):
    """Initiate a new quarterly report."""
    return controller.initiate_report(request)


@router.get("/{report_id}")
async def get_report_entry(report_id: int, controller: ReportController = Depends(get_report_controller)):
    """Get report entry form data."""
    return controller.get_report_entry(report_id)


@router.put("/{report_id}/balances")
async def save_balances(
    report_id: int,
    request: QuarterlyBalancesRequest,
    controller: ReportController = Depends(get_report_controller),
):
    """Save quarterly balances."""
    return controller.save_balances(report_id, request)


@router.get("/{report_id}/calculations")
async def get_calculations(
    report_id: int, controller: ReportController = Depends(get_report_controller)
):
    """Get current calculations for a report."""
    return controller.get_calculations(report_id)


@router.post("/{report_id}/finalize")
async def finalize_report(
    report_id: int, controller: ReportController = Depends(get_report_controller)
):
    """Finalize a report."""
    return controller.finalize_report(report_id)


@router.get("/{report_id}/pdf/sacs")
async def download_sacs_pdf(
    report_id: int,
    download: bool = False,
    controller: ReportController = Depends(get_report_controller),
):
    """View or download SACS PDF for a report."""
    return controller.download_sacs_pdf(report_id, download=download)


@router.get("/{report_id}/pdf/tcc")
async def download_tcc_pdf(
    report_id: int,
    download: bool = False,
    controller: ReportController = Depends(get_report_controller),
):
    """View or download TCC PDF for a report."""
    return controller.download_tcc_pdf(report_id, download=download)


@router.get("/client/{client_id}/reports")
async def get_report_history(
    client_id: int, controller: ReportController = Depends(get_report_controller)
):
    """Get report history for a client."""
    return controller.get_report_history(client_id)
