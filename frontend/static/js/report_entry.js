/* Report entry and balance form handling */

let currentReportId = null;
let currentReportDate = null;
let currentClientAccounts = [];
let currentPreviousBalances = {};

async function initializeReportEntry() {
    const reportId = getQueryParam('id');
    if (!reportId) {
        showError('No report ID provided');
        return;
    }
    
    currentReportId = reportId;
    await loadReportData(reportId);
}

async function loadReportData(reportId) {
    try {
        const { response, data } = await fetchJSON(`/reports/${reportId}`);
        
        if (!response.ok || !data || !data.success) {
            document.getElementById('loadingIndicator').style.display = 'none';
            showError(getApiErrorMessage(data, 'Failed to load report'));
            return;
        }
        
        const reportData = data.data;
        currentClientAccounts = reportData.accounts || [];
        currentReportDate = reportData.report_date;
        currentPreviousBalances = reportData.previous_balances || {};
        
        // Populate form with data
        populateReportForm(reportData);
        
        // Set up live calculations
        setupLiveCalculations(reportData);

        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('reportContent').style.display = 'grid';
        updatePdfLinks(Boolean(reportData.sacs_data));
    } catch (error) {
        console.error('Error loading report:', error);
        document.getElementById('loadingIndicator').style.display = 'none';
        showError('Error loading report data');
    }
}

function populateReportForm(reportData) {
    // SACS fields
    const reportDateInput = document.getElementById('report_date');
    const salaryInput = document.getElementById('monthly_salary');
    const expenseInput = document.getElementById('monthly_expense_budget');
    const deductibleInput = document.getElementById('insurance_deductibles_total');
    const privateReserveInput = document.getElementById('private_reserve_balance');
    const schwabInput = document.getElementById('schwab_investment_balance');

    if (reportDateInput) {
        reportDateInput.value = reportData.report_date || '';
    }

    if (salaryInput) {
        salaryInput.value = reportData.client.monthly_salary || '';
    }

    if (expenseInput) {
        expenseInput.value = reportData.client.monthly_expense_budget || '';
    }

    if (deductibleInput) {
        deductibleInput.value = reportData.client.insurance_deductibles_total || 0;
    }
    
    if (privateReserveInput && reportData.sacs_data) {
        privateReserveInput.value = reportData.sacs_data.private_reserve_balance ?? '';
    }
    
    if (schwabInput && reportData.sacs_data) {
        schwabInput.value = reportData.sacs_data.schwab_investment_balance ?? '';
    }
    
    // TCC fields - account balances
    const accountsContainer = document.getElementById('account_balances_container');
    if (accountsContainer) {
        let html = '';
        const currentBalances = reportData.current_balances || {};
        const previousBalances = reportData.previous_balances || {};
        
        if (!currentClientAccounts.length) {
            accountsContainer.innerHTML = '<p style="color: #888;">No accounts have been added for this client yet.</p>';
            return;
        }

        currentClientAccounts.forEach(account => {
            const currentBalance = currentBalances[account.id] || {};
            const previousBalance = previousBalances[account.id] || {};
            
            const displayName = `${account.label}${account.account_last4 ? ` (${account.account_last4})` : ''}`;
            
            html += `
                <div class="account-row">
                    <div class="account-row-header">
                        <span class="account-row-label">${escapeHtml(displayName)}</span>
                        <span class="account-row-last4">${escapeHtml(account.account_type)}</span>
                    </div>
                    <div class="account-row-inputs">
                        <div>
                            <label style="font-size: 11px;">Balance</label>
                            <input 
                                type="number" 
                                step="0.01" 
                                id="balance_${account.id}"
                                data-account-id="${account.id}"
                                value="${currentBalance.balance ?? ''}"
                                placeholder="Enter balance"
                                onchange="updateCalculations()"
                            />
                        </div>
                        <div>
                            <label style="font-size: 11px;">As of</label>
                            <input 
                                type="date" 
                                id="balance_date_${account.id}"
                                value="${currentBalance.balance_date || reportData.report_date || ''}"
                            />
                        </div>
                        <div class="account-actions">
                            <button type="button" class="use-last-button" onclick="useLastBalance(${account.id})">Use Last</button>
                            <label class="stale-toggle">
                                <input type="checkbox" id="is_stale_${account.id}" ${currentBalance.is_stale ? 'checked' : ''}>
                                Stale
                            </label>
                        </div>
                    </div>
                    ${previousBalance.balance !== undefined ? `<small style="color: #888;">Previous: ${formatCurrency(previousBalance.balance)}</small>` : ''}
                </div>
            `;
        });
        
        accountsContainer.innerHTML = html;
    }
}

function setupLiveCalculations(reportData) {
    // Add event listeners to all input fields
    const inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('input', updateCalculations);
    });
    
    updateCalculations();
}

async function updateCalculations() {
    try {
        // Get form values
        const inflow = parseFloat(document.getElementById('monthly_salary').value || 0);
        const outflow = parseFloat(document.getElementById('monthly_expense_budget').value || 0);
        const insurance = parseFloat(document.getElementById('insurance_deductibles_total').value || 0);
        const privateReserve = parseFloat(document.getElementById('private_reserve_balance').value || 0);
        const schwab = parseFloat(document.getElementById('schwab_investment_balance').value || 0);
        
        // Get account balances
        const balances = {};
        currentClientAccounts.forEach(account => {
            const inputElement = document.getElementById(`balance_${account.id}`);
            if (inputElement) {
                balances[account.id] = parseFloat(inputElement.value || 0);
            }
        });
        
        // Calculate
        const sacs = calculateSACS(inflow, outflow, insurance, privateReserve, schwab);
        const tcc = calculateTCC(currentClientAccounts, balances);
        
        // Update preview
        updatePreview(sacs, tcc);
        
        // Check completeness
        checkCompletion(balances);
    } catch (error) {
        console.error('Calculation error:', error);
    }
}

function updatePreview(sacs, tcc) {
    const previewDiv = document.getElementById('calculation_preview');
    if (!previewDiv) return;
    
    let html = `
        <div class="preview-section">
            <div class="preview-title">SACS Summary</div>
            <div class="preview-item">
                <span class="preview-label">Monthly Inflow</span>
                <span class="preview-value">${formatCurrency(sacs.inflow)}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Monthly Outflow</span>
                <span class="preview-value">${formatCurrency(sacs.outflow)}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Excess</span>
                <span class="preview-value ${sacs.excess > 0 ? 'positive' : 'negative'}">${formatCurrency(sacs.excess)}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Private Reserve Target</span>
                <span class="preview-value">${formatCurrency(sacs.private_reserve_target)}</span>
            </div>
            <div class="preview-note">(6 x Monthly Expense Budget + Insurance Deductibles)</div>
        </div>
        
        <div class="preview-section">
            <div class="preview-title">TCC Summary</div>
            <div class="preview-item">
                <span class="preview-label">Total Net Worth</span>
                <span class="preview-value">${formatCurrency(tcc.grand_total)}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Total Liabilities</span>
                <span class="preview-value">${formatCurrency(tcc.liabilities_total)}</span>
            </div>
        </div>
    `;
    
    previewDiv.innerHTML = html;
}

function checkCompletion(balances) {
    const missingFields = getMissingReportFields();
    if (missingFields.length === 0) {
        setValidationMessage('');
    }
    return missingFields.length === 0;
}

function getMissingReportFields() {
    const missingFields = [];

    const requiredInputs = [
        { id: 'private_reserve_balance', label: 'Private Reserve Balance' },
    ];

    requiredInputs.forEach(({ id, label }) => {
        const input = document.getElementById(id);
        if (input && input.value === '') {
            input.classList.add('field-incomplete');
            missingFields.push({ input, label });
        } else if (input) {
            input.classList.remove('field-incomplete');
        }
    });

    currentClientAccounts.forEach(account => {
        const input = document.getElementById(`balance_${account.id}`);
        if (input && input.value === '') {
            input.classList.add('field-incomplete');
            missingFields.push({ input, label: `${account.label} balance` });
        } else if (input) {
            input.classList.remove('field-incomplete');
        }
    });

    return missingFields;
}

function setValidationMessage(message) {
    const messageElement = document.getElementById('report_validation_message');
    if (!messageElement) {
        return;
    }

    messageElement.textContent = message;
    messageElement.style.display = message ? 'block' : 'none';
}

function validateReportForm() {
    const missingFields = getMissingReportFields();

    if (missingFields.length > 0) {
        const names = missingFields.map(field => field.label).join(', ');
        setValidationMessage(`Please fill these required fields before generating PDFs: ${names}.`);
        showError('Please fill the highlighted required fields before generating PDFs.');
        missingFields[0].input.focus();
        return false;
    }

    setValidationMessage('');
    return true;
}

function useLastBalance(accountId) {
    const previousBalance = currentPreviousBalances[accountId];
    const input = document.getElementById(`balance_${accountId}`);
    const dateInput = document.getElementById(`balance_date_${accountId}`);

    if (!previousBalance || previousBalance.balance === undefined) {
        showError('No previous balance is available for this account.');
        return;
    }

    if (input) {
        input.value = previousBalance.balance;
    }

    if (dateInput && previousBalance.balance_date) {
        dateInput.value = previousBalance.balance_date;
    }

    updateCalculations();
}

async function saveBalancesAndGenerate() {
    if (!validateReportForm()) {
        return;
    }

    const generateBtn = document.getElementById('save_and_generate_button');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.classList.add('is-saving');
        generateBtn.textContent = 'Saving...';
    }

    try {
        const report_date = document.getElementById('report_date').value || currentReportDate;
        const private_reserve_balance = parseFloat(document.getElementById('private_reserve_balance').value);
        const schwabValue = document.getElementById('schwab_investment_balance').value;
        const schwab_investment_balance = schwabValue ? parseFloat(schwabValue) : null;
        
        const account_balances = [];
        currentClientAccounts.forEach(account => {
            const balanceInput = document.getElementById(`balance_${account.id}`);
            const dateInput = document.getElementById(`balance_date_${account.id}`);
            const staleInput = document.getElementById(`is_stale_${account.id}`);
            
            if (balanceInput && balanceInput.value) {
                account_balances.push({
                    account_id: account.id,
                    balance: parseFloat(balanceInput.value),
                    balance_date: dateInput && dateInput.value ? dateInput.value : null,
                    is_stale: staleInput ? staleInput.checked : false
                });
            }
        });
        
        const payload = {
            report_date: report_date,
            private_reserve_balance: private_reserve_balance,
            schwab_investment_balance: schwab_investment_balance,
            account_balances: account_balances
        };
        
        const { response, data } = await fetchJSON(`/reports/${currentReportId}/balances`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok && data && data.success) {
            updatePreview(data.data.sacs, data.data.tcc);
            updatePdfLinks(true);
            showSuccess('PDFs are ready to view or download.');
        } else {
            showError(getApiErrorMessage(data, 'Failed to save balances'));
        }
    } catch (error) {
        console.error('Error saving balances:', error);
        showError('Error saving balances');
    } finally {
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.classList.remove('is-saving');
            generateBtn.textContent = 'Save & Generate PDFs';
        }
    }
}

function updatePdfLinks(show) {
    const downloads = document.getElementById('pdf_downloads');
    if (!downloads) {
        return;
    }

    downloads.style.display = show ? 'grid' : 'none';

    const links = {
        view_sacs_button: `/reports/${currentReportId}/pdf/sacs`,
        download_sacs_button: `/reports/${currentReportId}/pdf/sacs?download=true`,
        view_tcc_button: `/reports/${currentReportId}/pdf/tcc`,
        download_tcc_button: `/reports/${currentReportId}/pdf/tcc?download=true`,
    };

    Object.entries(links).forEach(([id, href]) => {
        const link = document.getElementById(id);
        if (link) {
            link.href = href;
        }
    });
}
