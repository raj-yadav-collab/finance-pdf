import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from app.routes.client_route import router as client_router
from app.routes.report_route import router as report_router
from app.routes.dashboard_route import router as dashboard_router
from app.middleware.middleware import error_handler_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
app.middleware("http")(error_handler_middleware)


def init_database():
    """Initialize SQLite database with tables."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name_1    TEXT NOT NULL,
            last_name_1     TEXT NOT NULL,
            dob_1           TEXT NOT NULL,
            ssn_last4_1     TEXT NOT NULL,
            first_name_2    TEXT,
            last_name_2     TEXT,
            dob_2           TEXT,
            ssn_last4_2     TEXT,
            monthly_salary  REAL NOT NULL,
            monthly_expense_budget REAL NOT NULL,
            private_reserve_target REAL,
            insurance_deductibles_total REAL DEFAULT 0,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        )
    """)
    
    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id       INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            account_type    TEXT NOT NULL,
            label           TEXT NOT NULL,
            account_last4   TEXT,
            interest_rate   REAL,
            property_address TEXT,
            display_order   INTEGER DEFAULT 0,
            is_active       INTEGER DEFAULT 1
        )
    """)
    
    # Create quarterly_reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quarterly_reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id       INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            report_date     TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'draft',
            created_at      TEXT NOT NULL
        )
    """)
    
    # Create report_balances table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_balances (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id       INTEGER NOT NULL REFERENCES quarterly_reports(id) ON DELETE CASCADE,
            account_id      INTEGER NOT NULL REFERENCES accounts(id),
            balance         REAL NOT NULL,
            cash_balance    REAL,
            balance_date    TEXT,
            is_stale        INTEGER DEFAULT 0,
            notes           TEXT
        )
    """)
    
    # Create report_sacs_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_sacs_data (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id               INTEGER NOT NULL UNIQUE REFERENCES quarterly_reports(id) ON DELETE CASCADE,
            inflow                  REAL NOT NULL,
            outflow                 REAL NOT NULL,
            excess                  REAL NOT NULL,
            private_reserve_balance REAL NOT NULL,
            schwab_investment_balance REAL,
            private_reserve_target  REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {config.DATABASE_PATH}")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()
    logger.info(f"Application started: {config.APP_NAME} v{config.APP_VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Application shutting down")


# Register route routers
app.include_router(client_router)
app.include_router(report_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
    }


@app.get("/")
async def root():
    """Serve the frontend dashboard."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{page_name}.html")
async def frontend_page(page_name: str):
    """Serve root-level frontend HTML pages used by the vanilla JS app."""
    allowed_pages = {
        "index",
        "client_detail",
        "client_new",
        "report_entry",
        "report_history",
    }
    if page_name not in allowed_pages:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not Found")

    return FileResponse(FRONTEND_DIR / f"{page_name}.html")


# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    logger.info("Static files mounted")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Mount full frontend directory so HTML pages can be served via the backend
try:
    app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend_files")
    logger.info("Frontend directory mounted at /frontend")
except Exception as e:
    logger.warning(f"Could not mount frontend directory: {e}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG,
        reload=config.DEBUG,
    )
