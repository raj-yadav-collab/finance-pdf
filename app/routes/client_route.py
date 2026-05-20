from fastapi import APIRouter, Depends
from app.controllers.client_controller import ClientController
from app.controllers.report_controller import ReportController
from app.common.types.requests.create_client_request import CreateClientRequest
from app.common.types.requests.update_client_request import UpdateClientRequest
from app.common.types.requests.create_account_request import CreateAccountRequest
from app.utils.dependencies import get_client_controller, get_report_controller

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
async def list_clients(controller: ClientController = Depends(get_client_controller)):
    """List all clients."""
    return controller.list_clients()


@router.post("")
async def create_client(
    request: CreateClientRequest, controller: ClientController = Depends(get_client_controller)
):
    """Create a new client."""
    return controller.create_client(request)


@router.get("/{client_id}")
async def get_client(client_id: int, controller: ClientController = Depends(get_client_controller)):
    """Get a specific client's details."""
    return controller.get_client(client_id)


@router.get("/{client_id}/reports")
async def get_report_history(
    client_id: int, controller: ReportController = Depends(get_report_controller)
):
    """Get report history for a client."""
    return controller.get_report_history(client_id)


@router.put("/{client_id}")
async def update_client(
    client_id: int,
    request: UpdateClientRequest,
    controller: ClientController = Depends(get_client_controller),
):
    """Update an existing client."""
    return controller.update_client(client_id, request)


@router.delete("/{client_id}")
async def delete_client(client_id: int, controller: ClientController = Depends(get_client_controller)):
    """Delete a client."""
    return controller.delete_client(client_id)


@router.post("/{client_id}/accounts")
async def add_account(
    client_id: int,
    request: CreateAccountRequest,
    controller: ClientController = Depends(get_client_controller),
):
    """Add an account to a client."""
    return controller.add_account(client_id, request)


@router.put("/{client_id}/accounts/{account_id}")
async def update_account(
    client_id: int,
    account_id: int,
    request: CreateAccountRequest,
    controller: ClientController = Depends(get_client_controller),
):
    """Update an account."""
    return controller.update_account(client_id, account_id, request)


@router.delete("/{client_id}/accounts/{account_id}")
async def remove_account(
    client_id: int,
    account_id: int,
    controller: ClientController = Depends(get_client_controller),
):
    """Remove an account from a client."""
    return controller.remove_account(client_id, account_id)
