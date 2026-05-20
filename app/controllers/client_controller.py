import logging
from fastapi import HTTPException
from app.services.client_service import ClientService
from app.common.custom_exceptions.client_not_found import ClientNotFoundError
from app.common.custom_exceptions.account_not_found import AccountNotFoundError
from app.common.types.requests.create_client_request import CreateClientRequest
from app.common.types.requests.update_client_request import UpdateClientRequest
from app.common.types.requests.create_account_request import CreateAccountRequest
from app.common.constants.messages import *

logger = logging.getLogger(__name__)


class ClientController:
    """Controller for client-related HTTP requests."""
    
    def __init__(self, client_service: ClientService):
        self.client_service = client_service
    
    def list_clients(self):
        """List all clients."""
        try:
            clients = self.client_service.get_all_clients()
            return {
                "success": True,
                "data": [client.model_dump() for client in clients]
            }
        except Exception as e:
            logger.error(f"Error listing clients: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def get_client(self, client_id: int):
        """Get a specific client's details."""
        try:
            client = self.client_service.get_client_details(client_id)
            return {
                "success": True,
                "data": client.model_dump()
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting client {client_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def create_client(self, request: CreateClientRequest):
        """Create a new client."""
        try:
            client = self.client_service.create_client(request)
            return {
                "success": True,
                "message": MSG_CLIENT_CREATED,
                "data": client.model_dump()
            }
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def update_client(self, client_id: int, request: UpdateClientRequest):
        """Update an existing client."""
        try:
            client = self.client_service.update_client(client_id, request)
            return {
                "success": True,
                "message": MSG_CLIENT_UPDATED,
                "data": client.model_dump()
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating client {client_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def delete_client(self, client_id: int):
        """Delete a client."""
        try:
            self.client_service.delete_client(client_id)
            return {
                "success": True,
                "message": MSG_CLIENT_DELETED
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting client {client_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def add_account(self, client_id: int, request: CreateAccountRequest):
        """Add an account to a client."""
        try:
            account = self.client_service.add_account(client_id, request)
            return {
                "success": True,
                "message": MSG_ACCOUNT_CREATED,
                "data": account.model_dump()
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding account to client {client_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def update_account(self, client_id: int, account_id: int, request: CreateAccountRequest):
        """Update an account."""
        try:
            account = self.client_service.update_account(client_id, account_id, request)
            return {
                "success": True,
                "message": MSG_ACCOUNT_UPDATED,
                "data": account.model_dump()
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except AccountNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_ACCOUNT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating account {account_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
    
    def remove_account(self, client_id: int, account_id: int):
        """Remove an account from a client."""
        try:
            self.client_service.remove_account(client_id, account_id)
            return {
                "success": True,
                "message": MSG_ACCOUNT_DELETED
            }
        except ClientNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_CLIENT_NOT_FOUND)
        except AccountNotFoundError:
            raise HTTPException(status_code=404, detail=MSG_ACCOUNT_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error removing account {account_id}: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
