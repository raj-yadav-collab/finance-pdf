import sqlite3
from datetime import datetime
from typing import Optional
from app.common.constants.common import DB_DATE_FORMAT, DB_DATETIME_FORMAT


class ReportRepository:
    """Repository for quarterly report database operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_report(self, report_data: dict) -> dict:
        """Create a new quarterly report."""
        conn = self._get_connection()
        try:
            now = datetime.utcnow().strftime(DB_DATETIME_FORMAT)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO quarterly_reports (
                    client_id, report_date, status, created_at
                ) VALUES (?, ?, ?, ?)
            """, (
                report_data['client_id'],
                report_data['report_date'],
                report_data.get('status', 'draft'),
                now
            ))
            
            report_id = cursor.lastrowid
            conn.commit()
            
            return self.get_report_by_id(report_id)
        finally:
            conn.close()
    
    def get_report_by_id(self, report_id: int) -> Optional[dict]:
        """Get a report by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quarterly_reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_reports_for_client(self, client_id: int) -> list[dict]:
        """Get all reports for a client, ordered by date descending."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM quarterly_reports 
                WHERE client_id = ?
                ORDER BY report_date DESC
            """, (client_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_last_report_for_client(self, client_id: int) -> Optional[dict]:
        """Get the most recent final report for a client."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM quarterly_reports 
                WHERE client_id = ? AND status = 'final'
                ORDER BY report_date DESC
                LIMIT 1
            """, (client_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_draft_report_for_client_date(self, client_id: int, report_date: str) -> Optional[dict]:
        """Get a draft report for a client on a specific date."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM quarterly_reports 
                WHERE client_id = ? AND report_date = ? AND status = 'draft'
                LIMIT 1
            """, (client_id, report_date))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def save_balances(self, report_id: int, balances: list[dict]) -> None:
        """Save account balances for a report."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Delete existing balances for this report
            cursor.execute("DELETE FROM report_balances WHERE report_id = ?", (report_id,))
            
            # Insert new balances
            for balance in balances:
                cursor.execute("""
                    INSERT INTO report_balances (
                        report_id, account_id, balance, cash_balance,
                        balance_date, is_stale, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id,
                    balance['account_id'],
                    balance['balance'],
                    balance.get('cash_balance'),
                    balance.get('balance_date'),
                    balance.get('is_stale', 0),
                    balance.get('notes')
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def save_sacs_data(self, report_id: int, sacs_data: dict) -> None:
        """Save SACS calculation data for a report."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Delete existing SACS data for this report
            cursor.execute("DELETE FROM report_sacs_data WHERE report_id = ?", (report_id,))
            
            # Insert new SACS data
            cursor.execute("""
                INSERT INTO report_sacs_data (
                    report_id, inflow, outflow, excess,
                    private_reserve_balance, schwab_investment_balance,
                    private_reserve_target
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                sacs_data['inflow'],
                sacs_data['outflow'],
                sacs_data['excess'],
                sacs_data['private_reserve_balance'],
                sacs_data.get('schwab_investment_balance'),
                sacs_data['private_reserve_target']
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_balances_for_report(self, report_id: int) -> list[dict]:
        """Get all account balances for a report."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM report_balances 
                WHERE report_id = ?
                ORDER BY account_id
            """, (report_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_sacs_data_for_report(self, report_id: int) -> Optional[dict]:
        """Get SACS calculation data for a report."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM report_sacs_data 
                WHERE report_id = ?
            """, (report_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def finalize_report(self, report_id: int) -> None:
        """Mark a report as final."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE quarterly_reports 
                SET status = 'final'
                WHERE id = ?
            """, (report_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_previous_balances(self, client_id: int) -> list[dict]:
        """Get the most recent balances for a client (last quarter reference)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rb.* FROM report_balances rb
                JOIN quarterly_reports qr ON rb.report_id = qr.id
                WHERE qr.client_id = ? AND qr.status = 'final'
                ORDER BY qr.report_date DESC
                LIMIT (SELECT COUNT(DISTINCT id) FROM accounts WHERE client_id = ? AND is_active = 1)
            """, (client_id, client_id))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
