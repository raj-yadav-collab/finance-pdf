# Logging messages
LOG_CLIENT_CREATED = "Client created: client_id={client_id}"
LOG_CLIENT_UPDATED = "Client updated: client_id={client_id}"
LOG_CLIENT_DELETED = "Client deleted: client_id={client_id}"
LOG_ACCOUNT_CREATED = "Account created: account_id={account_id}, client_id={client_id}"
LOG_ACCOUNT_UPDATED = "Account updated: account_id={account_id}"
LOG_ACCOUNT_DELETED = "Account deleted: account_id={account_id}"
LOG_REPORT_CREATED = "Report created: report_id={report_id}, client_id={client_id}"
LOG_REPORT_FINALIZED = "Report finalized: report_id={report_id}"
LOG_BALANCES_SAVED = "Balances saved: report_id={report_id}"
LOG_PDF_GENERATED = "PDF generated: report_id={report_id}, type={pdf_type}"
LOG_PDF_GENERATION_FAILED = "PDF generation failed: report_id={report_id}, error={error}"
LOG_CALCULATION_ERROR = "Calculation error: {error}"
LOG_DATABASE_ERROR = "Database error: {error}"
LOG_INVALID_REQUEST = "Invalid request: {error}"

# Error logs
LOG_ERROR_PROCESSING_REQUEST = "Error processing request: {endpoint}, error={error}"
