from config import config
from app.repositories.client_repository import ClientRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.report_repository import ReportRepository
from app.services.client_service import ClientService
from app.services.report_service import ReportService
from app.services.pdf_service import PDFService
from app.controllers.client_controller import ClientController
from app.controllers.report_controller import ReportController
from app.controllers.dashboard_controller import DashboardController


def get_client_repository() -> ClientRepository:
    """Get client repository instance."""
    return ClientRepository(config.DATABASE_PATH)


def get_account_repository() -> AccountRepository:
    """Get account repository instance."""
    return AccountRepository(config.DATABASE_PATH)


def get_report_repository() -> ReportRepository:
    """Get report repository instance."""
    return ReportRepository(config.DATABASE_PATH)


def get_client_service() -> ClientService:
    """Get client service instance."""
    client_repo = get_client_repository()
    account_repo = get_account_repository()
    return ClientService(client_repo, account_repo)


def get_report_service() -> ReportService:
    """Get report service instance."""
    client_repo = get_client_repository()
    account_repo = get_account_repository()
    report_repo = get_report_repository()
    client_service = get_client_service()
    return ReportService(client_repo, account_repo, report_repo, client_service)


def get_pdf_service() -> PDFService:
    """Get PDF service instance."""
    return PDFService()


def get_client_controller() -> ClientController:
    """Get client controller instance."""
    client_service = get_client_service()
    return ClientController(client_service)


def get_report_controller() -> ReportController:
    """Get report controller instance."""
    report_service = get_report_service()
    pdf_service = get_pdf_service()
    account_repo = get_account_repository()
    return ReportController(report_service, pdf_service, account_repo)


def get_dashboard_controller() -> DashboardController:
    """Get dashboard controller instance."""
    client_service = get_client_service()
    return DashboardController(client_service)
