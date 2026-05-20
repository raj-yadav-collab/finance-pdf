from datetime import date
from app.repositories.client_repository import ClientRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.report_repository import ReportRepository
from app.services.calculation_service import CalculationService
from app.common.custom_exceptions.client_not_found import ClientNotFoundError
from app.common.custom_exceptions.report_not_found import ReportNotFoundError
from app.common.custom_exceptions.missing_required_balances import (
    MissingRequiredBalancesError,
)
from app.common.types.requests.generate_report_request import GenerateReportRequest
from app.common.types.requests.quarterly_balances_request import QuarterlyBalancesRequest
from app.common.types.responses.calculation_preview import CalculationPreview
from app.common.types.responses.report_history_item import ReportHistoryItem
from app.common.types.responses.client_details import ClientDetails
from app.common.enums.report_status import ReportStatus
from app.services.client_service import ClientService


class ReportService:
    """Service for quarterly report management and calculations."""
    
    def __init__(
        self,
        client_repo: ClientRepository,
        account_repo: AccountRepository,
        report_repo: ReportRepository,
        client_service: ClientService,
    ):
        self.client_repo = client_repo
        self.account_repo = account_repo
        self.report_repo = report_repo
        self.client_service = client_service
        self.calc_service = CalculationService()
    
    def initiate_report(self, request: GenerateReportRequest) -> dict:
        """
        Initiate a new quarterly report for a client.
        
        Creates a draft report, loads client info, loads previous balances as reference.
        """
        # Verify client exists
        client = self.client_repo.get_client_by_id(request.client_id)
        if not client:
            raise ClientNotFoundError(request.client_id)
        
        created = True

        # Re-open an existing draft for this client/date instead of creating a
        # duplicate. This keeps the Generate Report action safe to click twice.
        existing = self.report_repo.get_draft_report_for_client_date(
            request.client_id, request.report_date.isoformat()
        )
        if existing:
            report = existing
            created = False
        else:
            # Create the draft report only when Generate Report is clicked and
            # there is not already a draft for the selected date.
            report_data = {
                'client_id': request.client_id,
                'report_date': request.report_date.isoformat(),
                'status': 'draft',
            }
            report = self.report_repo.create_report(report_data)
        
        # Get client details and previous balances for pre-fill
        client_details = self.client_service.get_client_details(request.client_id)
        previous_balances = self.report_repo.get_previous_balances(request.client_id)
        
        # Build previous balance reference
        previous_by_account = {}
        for bal in previous_balances:
            previous_by_account[bal['account_id']] = {
                'balance': bal['balance'],
                'cash_balance': bal.get('cash_balance'),
                'balance_date': bal.get('balance_date'),
            }
        
        return {
            'report_id': report['id'],
            'report_date': report['report_date'],
            'created': created,
            'client': client_details,
            'accounts': client_details.accounts,
            'previous_balances': previous_by_account,
        }
    
    def get_report_entry_data(self, report_id: int) -> dict:
        """Get current report state and previous quarter reference data."""
        report = self.report_repo.get_report_by_id(report_id)
        if not report:
            raise ReportNotFoundError(report_id)
        
        client_details = self.client_service.get_client_details(report['client_id'])
        current_balances = self.report_repo.get_balances_for_report(report_id)
        sacs_data = self.report_repo.get_sacs_data_for_report(report_id)
        previous_balances = self.report_repo.get_previous_balances(report['client_id'])
        
        # Build balance references
        current_by_account = {}
        for bal in current_balances:
            current_by_account[bal['account_id']] = {
                'balance': bal['balance'],
                'cash_balance': bal.get('cash_balance'),
                'balance_date': bal.get('balance_date'),
                'is_stale': bal.get('is_stale', 0),
            }
        
        previous_by_account = {}
        for bal in previous_balances:
            previous_by_account[bal['account_id']] = {
                'balance': bal['balance'],
                'cash_balance': bal.get('cash_balance'),
                'balance_date': bal.get('balance_date'),
            }
        
        return {
            'report_id': report_id,
            'report_date': report['report_date'],
            'status': report['status'],
            'client': client_details,
            'accounts': client_details.accounts,
            'current_balances': current_by_account,
            'previous_balances': previous_by_account,
            'sacs_data': sacs_data,
        }
    
    def save_balances(
        self, report_id: int, request: QuarterlyBalancesRequest
    ) -> CalculationPreview:
        """
        Save entered balances for a report and trigger calculations.
        
        Returns live-calculated SACS and TCC values.
        """
        report = self.report_repo.get_report_by_id(report_id)
        if not report:
            raise ReportNotFoundError(report_id)
        
        # Save the balance entries
        balance_entries = []
        balance_dict = {}
        
        for entry in request.account_balances:
            balance_date = (
                entry.balance_date.isoformat()
                if entry.balance_date
                else request.report_date.isoformat()
            )
            
            balance_entries.append({
                'account_id': entry.account_id,
                'balance': entry.balance,
                'cash_balance': entry.cash_balance,
                'balance_date': balance_date,
                'is_stale': 1 if entry.is_stale else 0,
            })
            
            balance_dict[entry.account_id] = entry.balance
        
        self.report_repo.save_balances(report_id, balance_entries)
        
        # Get client info for calculations
        client = self.client_repo.get_client_by_id(report['client_id'])
        accounts = self.account_repo.get_accounts_for_client(report['client_id'])
        
        # Calculate SACS
        sacs = self.calc_service.calculate_sacs(
            inflow=client['monthly_salary'],
            outflow=client['monthly_expense_budget'],
            private_reserve_balance=request.private_reserve_balance,
            insurance_deductibles_total=client['insurance_deductibles_total'],
            schwab_investment_balance=request.schwab_investment_balance,
        )
        
        # Save SACS data
        sacs_data = {
            'inflow': sacs.inflow,
            'outflow': sacs.outflow,
            'excess': sacs.excess,
            'private_reserve_balance': sacs.private_reserve_balance,
            'schwab_investment_balance': sacs.schwab_investment_balance,
            'private_reserve_target': sacs.private_reserve_target,
        }
        self.report_repo.save_sacs_data(report_id, sacs_data)
        
        # Calculate TCC
        from app.common.types.database_schemas.account_schema import AccountSchema
        
        account_schemas = [
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
        
        tcc = self.calc_service.calculate_tcc(account_schemas, balance_dict)
        
        return CalculationPreview(sacs=sacs, tcc=tcc)
    
    def finalize_report(self, report_id: int) -> None:
        """
        Mark a report as final.
        
        Validates that all required balances are present.
        """
        report = self.report_repo.get_report_by_id(report_id)
        if not report:
            raise ReportNotFoundError(report_id)
        
        # Validate completeness
        accounts = self.account_repo.get_accounts_for_client(report['client_id'])
        account_ids = [acc['id'] for acc in accounts if acc['is_active']]
        
        current_balances = self.report_repo.get_balances_for_report(report_id)
        entered = {bal['account_id']: bal['balance'] for bal in current_balances}
        
        missing = self.calc_service.validate_completeness(account_ids, entered)
        if missing:
            raise MissingRequiredBalancesError(missing)
        
        # Mark as final
        self.report_repo.finalize_report(report_id)
    
    def get_report_history(self, client_id: int) -> list[ReportHistoryItem]:
        """Get report history for a client."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        reports = self.report_repo.get_reports_for_client(client_id)
        
        return [
            ReportHistoryItem(
                id=rep['id'],
                report_date=rep['report_date'],
                status=ReportStatus(rep['status']),
                created_at=rep['created_at'],
            )
            for rep in reports
        ]
