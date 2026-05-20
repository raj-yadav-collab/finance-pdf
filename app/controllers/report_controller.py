import logging
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.common.types.database_schemas.account_schema import AccountSchema
from app.common.types.responses.calculation_preview import SACSCalculation
from app.services.report_service import ReportService
from app.services.pdf_service import PDFService
from app.repositories.account_repository import AccountRepository
from app.common.custom_exceptions.client_not_found import ClientNotFoundError
from app.common.custom_exceptions.report_not_found import ReportNotFoundError
from app.common.custom_exceptions.missing_required_balances import (
    MissingRequiredBalancesError,
)
from app.common.custom_exceptions.report_generation_error import ReportGenerationError
from app.common.types.requests.generate_report_request import GenerateReportRequest
from app.common.types.requests.quarterly_balances_request import QuarterlyBalancesRequest
from app.common.constants.messages import *

logger = logging.getLogger(__name__)


class ReportController:
    """Controller for report-related HTTP requests."""
    
    def __init__(
        self,
        report_service: ReportService,
        pdf_service: PDFService,
        account_repo: AccountRepository,
    ):
        self.report_service = report_service
        self.pdf_service = pdf_service
        self.account_repo = account_repo

    @staticmethod
    def _sacs_from_saved_data(sacs_data: dict) -> SACSCalculation:
        return SACSCalculation(
            inflow=sacs_data["inflow"],
            outflow=sacs_data["outflow"],
            excess=sacs_data["excess"],
            private_reserve_balance=sacs_data["private_reserve_balance"],
            private_reserve_target=sacs_data["private_reserve_target"],
            schwab_investment_balance=sacs_data.get("schwab_investment_balance"),
        )

    @staticmethod
    def _content_disposition(report_name: str, report_id: int, download: bool) -> str:
        disposition = "attachment" if download else "inline"
        return f'{disposition}; filename="{report_name}_{report_id}.pdf"'

    def _account_schemas_for_client(self, client_id: int) -> list[AccountSchema]:
        accounts = self.account_repo.get_accounts_for_client(client_id)
        return [
            AccountSchema(
                id=acc['id'],
                client_id=acc['client_id'],
                account_type=acc['account_type'],
                label=acc['label'],
                account_last4=acc.get('account_last4'),
                interest_rate=acc.get('interest_rate'),
                property_address=acc.get('property_address'),
                display_order=acc['display_order'],
                is_active=bool(acc['is_active']),
            )
            for acc in accounts
        ]
    
    def initiate_report(self, request: GenerateReportRequest):
        """Initiate a new quarterly report."""
        try:
            data = self.report_service.initiate_report(request)
            return {
                "success": True,
                "message": MSG_REPORT_CREATED if data.get("created") else "Existing draft report opened",
                "data": data
            }
        except Exception as e:
            logger.error(f"Error initiating report: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def get_report_entry(self, report_id: int):
        """Get report entry form data."""
        try:
            data = self.report_service.get_report_entry_data(report_id)
            return {
                "success": True,
                "data": data
            }
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def save_balances(self, report_id: int, request: QuarterlyBalancesRequest):
        """Save quarterly balances and return calculations."""
        try:
            calculations = self.report_service.save_balances(report_id, request)
            return {
                "success": True,
                "message": MSG_BALANCES_SAVED,
                "data": calculations.model_dump()
            }
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error saving balances for report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def get_calculations(self, report_id: int):
        """Get current calculations for a report."""
        try:
            data = self.report_service.get_report_entry_data(report_id)
            # Reconstruct calculations from saved data
            from app.services.calculation_service import CalculationService
            
            calc_service = CalculationService()
            
            # Get account details
            account_schemas = self._account_schemas_for_client(data['client'].id)
            
            # Build balance dict from current balances
            balance_dict = {}
            for acc_id, bal_data in data.get('current_balances', {}).items():
                balance_dict[int(acc_id)] = bal_data['balance']
            
            # Calculate
            sacs_data = data.get('sacs_data')
            if sacs_data:
                sacs = self._sacs_from_saved_data(sacs_data)
                tcc = calc_service.calculate_tcc(account_schemas, balance_dict)
                
                from app.common.types.responses.calculation_preview import CalculationPreview
                calculations = CalculationPreview(sacs=sacs, tcc=tcc)
                return {
                    "success": True,
                    "data": calculations.model_dump()
                }
            
            raise HTTPException(status_code=400, detail="No calculations saved yet")
        except HTTPException:
            raise
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting calculations for report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def finalize_report(self, report_id: int):
        """Finalize a report."""
        try:
            self.report_service.finalize_report(report_id)
            return {
                "success": True,
                "message": MSG_REPORT_FINALIZED
            }
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except MissingRequiredBalancesError as e:
            raise HTTPException(status_code=422, detail=MSG_MISSING_REQUIRED_BALANCES)
        except Exception as e:
            logger.error(f"Error finalizing report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def download_sacs_pdf(self, report_id: int, download: bool = False):
        """View or download SACS PDF for a report."""
        try:
            # Get report and client data
            data = self.report_service.get_report_entry_data(report_id)
            client = data['client']
            sacs_data = data.get('sacs_data')
            
            if not sacs_data:
                raise HTTPException(status_code=400, detail="Save balances before generating PDFs")
            
            sacs = self._sacs_from_saved_data(sacs_data)
            
            # Generate PDF
            from datetime import date
            pdf_bytes = self.pdf_service.generate_sacs_pdf(client, sacs, date.fromisoformat(data['report_date']))
            
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={"Content-Disposition": self._content_disposition("SACS", report_id, download)}
            )
        except HTTPException:
            raise
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except ReportGenerationError as e:
            raise HTTPException(status_code=500, detail=MSG_PDF_GENERATION_ERROR)
        except Exception as e:
            logger.error(f"Error generating SACS PDF for report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_PDF_GENERATION_ERROR)
    
    def download_tcc_pdf(self, report_id: int, download: bool = False):
        """View or download TCC PDF for a report."""
        try:
            # Get report and client data
            data = self.report_service.get_report_entry_data(report_id)
            client = data['client']
            sacs_data = data.get('sacs_data')
            
            if not sacs_data:
                raise HTTPException(status_code=400, detail="Save balances before generating PDFs")
            
            # Get account details
            account_schemas = self._account_schemas_for_client(client.id)
            
            # Build balance dict
            balance_dict = {}
            for acc_id, bal_data in data.get('current_balances', {}).items():
                balance_dict[int(acc_id)] = bal_data['balance']
            
            # Reconstruct TCC calculation
            from app.services.calculation_service import CalculationService
            calc_service = CalculationService()
            tcc = calc_service.calculate_tcc(account_schemas, balance_dict)
            
            # Generate PDF
            from datetime import date
            pdf_bytes = self.pdf_service.generate_tcc_pdf(
                client,
                tcc,
                account_schemas,
                balance_dict,
                date.fromisoformat(data['report_date']),
                data.get('current_balances', {}),
            )
            
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={"Content-Disposition": self._content_disposition("TCC", report_id, download)}
            )
        except HTTPException:
            raise
        except ReportNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_REPORT_NOT_FOUND)
        except ReportGenerationError as e:
            raise HTTPException(status_code=500, detail=MSG_PDF_GENERATION_ERROR)
        except Exception as e:
            logger.error(f"Error generating TCC PDF for report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_PDF_GENERATION_ERROR)
    
    def get_report_history(self, client_id: int):
        """Get report history for a client."""
        try:
            history = self.report_service.get_report_history(client_id)
            return {
                "success": True,
                "data": [item.model_dump() for item in history]
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting report history for client {client_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
