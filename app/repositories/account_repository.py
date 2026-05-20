import sqlite3
from typing import Optional
from app.common.enums.account_type import AccountType


class AccountRepository:
    """Repository for account database operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_accounts_for_client(self, client_id: int) -> list[dict]:
        """Get all accounts for a client, ordered by type and display_order."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE client_id = ? AND is_active = 1
                ORDER BY account_type, display_order
            """, (client_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_account_by_id(self, account_id: int) -> Optional[dict]:
        """Get an account by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def create_account(self, account_data: dict) -> dict:
        """Create a new account."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (
                    client_id, account_type, label, account_last4,
                    interest_rate, property_address, display_order, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_data['client_id'],
                account_data['account_type'],
                account_data['label'],
                account_data.get('account_last4'),
                account_data.get('interest_rate'),
                account_data.get('property_address'),
                account_data.get('display_order', 0),
                1
            ))
            
            account_id = cursor.lastrowid
            conn.commit()
            
            return self.get_account_by_id(account_id)
        finally:
            conn.close()
    
    def update_account(self, account_id: int, account_data: dict) -> Optional[dict]:
        """Update an existing account."""
        conn = self._get_connection()
        try:
            update_fields = []
            values = []
            
            field_mapping = {
                'account_type': 'account_type',
                'label': 'label',
                'account_last4': 'account_last4',
                'interest_rate': 'interest_rate',
                'property_address': 'property_address',
                'display_order': 'display_order',
            }
            
            for key, db_field in field_mapping.items():
                if key in account_data:
                    update_fields.append(f"{db_field} = ?")
                    values.append(account_data[key])
            
            if not update_fields:
                return self.get_account_by_id(account_id)
            
            values.append(account_id)
            cursor = conn.cursor()
            query = f"UPDATE accounts SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return self.get_account_by_id(account_id)
        finally:
            conn.close()
    
    def deactivate_account(self, account_id: int) -> bool:
        """Deactivate an account (soft delete)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET is_active = 0 WHERE id = ?", (account_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
