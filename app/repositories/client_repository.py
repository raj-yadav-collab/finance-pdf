import sqlite3
from datetime import datetime
from typing import Optional
from app.common.constants.common import DB_DATE_FORMAT, DB_DATETIME_FORMAT


class ClientRepository:
    """Repository for client database operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_clients(self) -> list[dict]:
        """Get all clients with their last report date."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = """
            SELECT 
                c.id,
                c.first_name_1,
                c.last_name_1,
                c.first_name_2,
                c.last_name_2,
                MAX(qr.report_date) as last_report_date,
                MAX(qr.id) as last_report_id
            FROM clients c
            LEFT JOIN quarterly_reports qr ON c.id = qr.client_id AND qr.status = 'final'
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_client_by_id(self, client_id: int) -> Optional[dict]:
        """Get a client by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def create_client(self, client_data: dict) -> dict:
        """Create a new client."""
        conn = self._get_connection()
        try:
            now = datetime.utcnow().strftime(DB_DATETIME_FORMAT)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO clients (
                    first_name_1, last_name_1, dob_1, ssn_last4_1,
                    first_name_2, last_name_2, dob_2, ssn_last4_2,
                    monthly_salary, monthly_expense_budget, 
                    insurance_deductibles_total,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_data['first_name_1'],
                client_data['last_name_1'],
                client_data['dob_1'],
                client_data['ssn_last4_1'],
                client_data.get('first_name_2'),
                client_data.get('last_name_2'),
                client_data.get('dob_2'),
                client_data.get('ssn_last4_2'),
                client_data['monthly_salary'],
                client_data['monthly_expense_budget'],
                client_data.get('insurance_deductibles_total', 0),
                now,
                now
            ))
            
            client_id = cursor.lastrowid
            conn.commit()
            
            return self.get_client_by_id(client_id)
        finally:
            conn.close()
    
    def update_client(self, client_id: int, client_data: dict) -> Optional[dict]:
        """Update an existing client."""
        conn = self._get_connection()
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            field_mapping = {
                'first_name_1': 'first_name_1',
                'last_name_1': 'last_name_1',
                'dob_1': 'dob_1',
                'ssn_last4_1': 'ssn_last4_1',
                'first_name_2': 'first_name_2',
                'last_name_2': 'last_name_2',
                'dob_2': 'dob_2',
                'ssn_last4_2': 'ssn_last4_2',
                'monthly_salary': 'monthly_salary',
                'monthly_expense_budget': 'monthly_expense_budget',
                'insurance_deductibles_total': 'insurance_deductibles_total',
            }
            
            for key, db_field in field_mapping.items():
                if key in client_data:
                    update_fields.append(f"{db_field} = ?")
                    values.append(client_data[key])
            
            if not update_fields:
                return self.get_client_by_id(client_id)
            
            now = datetime.utcnow().strftime(DB_DATETIME_FORMAT)
            update_fields.append("updated_at = ?")
            values.append(now)
            values.append(client_id)
            
            cursor = conn.cursor()
            query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return self.get_client_by_id(client_id)
        finally:
            conn.close()
    
    def delete_client(self, client_id: int) -> bool:
        """Soft-delete a client (mark as inactive)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # For now, just delete the client and cascade
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
