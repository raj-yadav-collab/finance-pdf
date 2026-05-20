from datetime import datetime, date
from app.repositories.client_repository import ClientRepository
from app.repositories.account_repository import AccountRepository
from app.common.custom_exceptions.client_not_found import ClientNotFoundError
from app.common.custom_exceptions.account_not_found import AccountNotFoundError
from app.common.types.requests.create_client_request import CreateClientRequest
from app.common.types.requests.update_client_request import UpdateClientRequest
from app.common.types.requests.create_account_request import CreateAccountRequest
from app.common.types.responses.client_summary import ClientSummary
from app.common.types.responses.client_details import ClientDetails, AccountInfo
from app.common.enums.account_type import AccountType


class ClientService:
    """Service for client management business logic."""
    
    def __init__(self, client_repo: ClientRepository, account_repo: AccountRepository):
        self.client_repo = client_repo
        self.account_repo = account_repo
    
    def get_all_clients(self) -> list[ClientSummary]:
        """Get all clients with their last report date."""
        clients = self.client_repo.get_all_clients()
        result = []
        
        for client in clients:
            display_name = self._format_display_name(
                client['first_name_1'],
                client['last_name_1'],
                client.get('first_name_2'),
                client.get('last_name_2'),
            )
            
            summary = ClientSummary(
                id=client['id'],
                display_name=display_name,
                last_report_date=client.get('last_report_date'),
                last_report_id=client.get('last_report_id'),
            )
            result.append(summary)
        
        return result
    
    def get_client_details(self, client_id: int) -> ClientDetails:
        """Get full client details with all accounts."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        accounts = self.account_repo.get_accounts_for_client(client_id)
        account_infos = [
            AccountInfo(
                id=acc['id'],
                account_type=AccountType(acc['account_type']),
                label=acc['label'],
                account_last4=acc.get('account_last4'),
                interest_rate=acc.get('interest_rate'),
                property_address=acc.get('property_address'),
                display_order=acc['display_order'],
            )
            for acc in accounts
        ]
        
        return ClientDetails(
            id=client['id'],
            first_name_1=client['first_name_1'],
            last_name_1=client['last_name_1'],
            dob_1=client['dob_1'],
            age_1=self._calculate_age(client['dob_1']),
            ssn_last4_1=client['ssn_last4_1'],
            first_name_2=client.get('first_name_2'),
            last_name_2=client.get('last_name_2'),
            dob_2=client.get('dob_2'),
            age_2=self._calculate_age(client['dob_2']) if client.get('dob_2') else None,
            ssn_last4_2=client.get('ssn_last4_2'),
            monthly_salary=client['monthly_salary'],
            monthly_expense_budget=client['monthly_expense_budget'],
            insurance_deductibles_total=client['insurance_deductibles_total'],
            accounts=account_infos,
        )
    
    def create_client(self, request: CreateClientRequest) -> ClientDetails:
        """Create a new client."""
        client_data = {
            'first_name_1': request.first_name_1,
            'last_name_1': request.last_name_1,
            'dob_1': request.dob_1.isoformat(),
            'ssn_last4_1': request.ssn_last4_1,
            'first_name_2': request.first_name_2,
            'last_name_2': request.last_name_2,
            'dob_2': request.dob_2.isoformat() if request.dob_2 else None,
            'ssn_last4_2': request.ssn_last4_2,
            'monthly_salary': request.monthly_salary,
            'monthly_expense_budget': request.monthly_expense_budget,
            'insurance_deductibles_total': request.insurance_deductibles_total,
        }
        
        created = self.client_repo.create_client(client_data)
        return self.get_client_details(created['id'])
    
    def update_client(
        self, client_id: int, request: UpdateClientRequest
    ) -> ClientDetails:
        """Update an existing client."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        # Build update data from request. Optional spouse fields may be
        # intentionally set to None to clear joint-client data.
        update_data = {}
        if request.first_name_1 is not None:
            update_data['first_name_1'] = request.first_name_1
        if request.last_name_1 is not None:
            update_data['last_name_1'] = request.last_name_1
        if request.dob_1 is not None:
            update_data['dob_1'] = request.dob_1.isoformat()
        if request.ssn_last4_1 is not None:
            update_data['ssn_last4_1'] = request.ssn_last4_1

        fields_set = request.model_fields_set
        if 'first_name_2' in fields_set:
            update_data['first_name_2'] = request.first_name_2
        if 'last_name_2' in fields_set:
            update_data['last_name_2'] = request.last_name_2
        if 'dob_2' in fields_set:
            update_data['dob_2'] = request.dob_2.isoformat() if request.dob_2 else None
        if 'ssn_last4_2' in fields_set:
            update_data['ssn_last4_2'] = request.ssn_last4_2

        if request.monthly_salary is not None:
            update_data['monthly_salary'] = request.monthly_salary
        if request.monthly_expense_budget is not None:
            update_data['monthly_expense_budget'] = request.monthly_expense_budget
        if request.insurance_deductibles_total is not None:
            update_data['insurance_deductibles_total'] = request.insurance_deductibles_total
        
        self.client_repo.update_client(client_id, update_data)
        return self.get_client_details(client_id)
    
    def delete_client(self, client_id: int) -> None:
        """Delete a client."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        self.client_repo.delete_client(client_id)
    
    def add_account(
        self, client_id: int, request: CreateAccountRequest
    ) -> AccountInfo:
        """Add an account to a client."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        account_data = {
            'client_id': client_id,
            'account_type': request.account_type.value,
            'label': request.label,
            'account_last4': request.account_last4,
            'interest_rate': request.interest_rate,
            'property_address': request.property_address,
            'display_order': request.display_order,
        }
        
        account = self.account_repo.create_account(account_data)
        return AccountInfo(
            id=account['id'],
            account_type=AccountType(account['account_type']),
            label=account['label'],
            account_last4=account.get('account_last4'),
            interest_rate=account.get('interest_rate'),
            property_address=account.get('property_address'),
            display_order=account['display_order'],
        )
    
    def update_account(
        self, client_id: int, account_id: int, request: CreateAccountRequest
    ) -> AccountInfo:
        """Update an account."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        account = self.account_repo.get_account_by_id(account_id)
        if not account or account['client_id'] != client_id:
            raise AccountNotFoundError(account_id)
        
        update_data = {
            'account_type': request.account_type.value,
            'label': request.label,
            'account_last4': request.account_last4,
            'interest_rate': request.interest_rate,
            'property_address': request.property_address,
            'display_order': request.display_order,
        }
        
        updated = self.account_repo.update_account(account_id, update_data)
        return AccountInfo(
            id=updated['id'],
            account_type=AccountType(updated['account_type']),
            label=updated['label'],
            account_last4=updated.get('account_last4'),
            interest_rate=updated.get('interest_rate'),
            property_address=updated.get('property_address'),
            display_order=updated['display_order'],
        )
    
    def remove_account(self, client_id: int, account_id: int) -> None:
        """Remove an account from a client."""
        client = self.client_repo.get_client_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)
        
        account = self.account_repo.get_account_by_id(account_id)
        if not account or account['client_id'] != client_id:
            raise AccountNotFoundError(account_id)
        
        self.account_repo.deactivate_account(account_id)
    
    @staticmethod
    def _calculate_age(dob: str | date) -> int:
        """Calculate age from date of birth."""
        if isinstance(dob, str):
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    
    @staticmethod
    def _format_display_name(
        first_1: str, last_1: str, first_2: str | None = None, last_2: str | None = None
    ) -> str:
        """Format display name for a client or couple."""
        if first_2 and last_2:
            return f"{first_1} & {first_2} {last_1}"
        return f"{first_1} {last_1}"
