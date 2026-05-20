import logging
from fastapi import HTTPException
from app.services.client_service import ClientService
from app.common.constants.messages import MSG_INTERNAL_ERROR

logger = logging.getLogger(__name__)


class DashboardController:
    """Controller for dashboard endpoints."""
    
    def __init__(self, client_service: ClientService):
        self.client_service = client_service
    
    def get_dashboard(self):
        """Get dashboard summary with all clients and their last report info."""
        try:
            clients = self.client_service.get_all_clients()
            return {
                "success": True,
                "data": {
                    "clients": [client.model_dump() for client in clients],
                    "total_clients": len(clients)
                }
            }
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            raise HTTPException(status_code=500, detail=MSG_INTERNAL_ERROR)
