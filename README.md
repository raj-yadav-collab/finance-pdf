# AW Client Report Portal

A web portal for financial planning firms to manage client data, enter quarterly balances, auto-calculate financials, and generate polished SACS (cashflow) and TCC (net worth) PDF reports.

## Features

- **Client Management**: Store and manage client profiles with basic and financial information
- **Account Tracking**: Organize accounts by type (retirement, non-retirement, trust, liabilities)
- **Quarterly Reporting**: Enter quarterly balance data with live calculation preview
- **PDF Generation**: Auto-generate professional SACS and TCC PDF reports
- **Calculation Engine**: Automatic computation of net worth, cashflow, and financial metrics

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: SQLite
- **PDF Generation**: ReportLab
- **Frontend**: HTML + CSS + vanilla JavaScript

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AW_PDF_flow

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, uses defaults)
cp .env.example .env

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### Database

The SQLite database (`clients.db`) is automatically initialized on first startup.

## Project Structure

```
.
├── main.py                      # FastAPI app entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── clients.db                   # SQLite database
├── app/
│   ├── routes/                 # API route definitions
│   ├── controllers/            # Request handlers
│   ├── services/               # Business logic
│   ├── repositories/           # Database access
│   ├── middleware/             # HTTP middleware
│   ├── utils/                  # Utilities and dependencies
│   └── common/                 # Shared types and constants
└── frontend/                   # HTML/CSS/JS frontend
```

## API Endpoints

### Clients

- `GET /clients` - List all clients
- `POST /clients` - Create new client
- `GET /clients/{client_id}` - Get client details
- `PUT /clients/{client_id}` - Update client
- `DELETE /clients/{client_id}` - Delete client
- `POST /clients/{client_id}/accounts` - Add account
- `PUT /clients/{client_id}/accounts/{account_id}` - Update account
- `DELETE /clients/{client_id}/accounts/{account_id}` - Delete account

### Reports

- `POST /reports/initiate` - Start new quarterly report
- `GET /reports/{report_id}` - Get report entry form data
- `PUT /reports/{report_id}/balances` - Save balances
- `GET /reports/{report_id}/calculations` - Get calculated values
- `POST /reports/{report_id}/finalize` - Mark report as final
- `GET /reports/{report_id}/pdf/sacs` - Download SACS PDF
- `GET /reports/{report_id}/pdf/tcc` - Download TCC PDF
- `GET /clients/{client_id}/reports` - Get report history

### Dashboard

- `GET /dashboard` - Get dashboard summary

## Development

Run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

## License

Proprietary
