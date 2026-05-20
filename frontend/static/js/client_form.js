/* Client form handling */

function initializeClientForm() {
    const firstNameInput = document.getElementById('first_name_1');
    const lastNameInput = document.getElementById('last_name_1');
    const dobInput = document.getElementById('dob_1');
    const marriedToggle = document.getElementById('is_married');
    const client2Section = document.getElementById('client_2_section');
    
    if (marriedToggle) {
        marriedToggle.addEventListener('change', function() {
            if (this.checked) {
                client2Section.style.display = 'block';
            } else {
                client2Section.style.display = 'none';
            }
        });
    }
    
    if (dobInput) {
        dobInput.addEventListener('change', function() {
            updateAge('age_1', this.value);
        });
    }
    
    const dob2Input = document.getElementById('dob_2');
    if (dob2Input) {
        dob2Input.addEventListener('change', function() {
            updateAge('age_2', this.value);
        });
    }
}

function updateAge(ageElementId, dobStr) {
    if (!dobStr) {
        const emptyAgeElement = document.getElementById(ageElementId);
        if (emptyAgeElement) {
            emptyAgeElement.value = '';
            emptyAgeElement.textContent = '';
        }
        return;
    }

    const today = new Date();
    const dob = new Date(dobStr + 'T00:00:00Z');
    let age = today.getFullYear() - dob.getFullYear();
    const monthDiff = today.getMonth() - dob.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
        age--;
    }
    
    const ageElement = document.getElementById(ageElementId);
    if (ageElement) {
        ageElement.value = age;
        ageElement.textContent = age;
    }
}

function validateClientForm() {
    const required = ['first_name_1', 'last_name_1', 'dob_1', 'ssn_last4_1', 'monthly_salary', 'monthly_expense_budget'];
    
    for (const fieldId of required) {
        const field = document.getElementById(fieldId);
        if (!field || !field.value.trim()) {
            showError(`Please fill in ${getFieldLabel(fieldId)}.`);
            return false;
        }
    }

    const ssn1 = document.getElementById('ssn_last4_1').value.trim();
    if (!/^\d{4}$/.test(ssn1)) {
        showError('Client 1 SSN must be exactly 4 digits.');
        return false;
    }

    const monthlySalary = parseFloat(document.getElementById('monthly_salary').value);
    const monthlyBudget = parseFloat(document.getElementById('monthly_expense_budget').value);
    const deductibles = parseFloat(document.getElementById('insurance_deductibles_total').value || 0);

    if (!(monthlySalary > 0) || !(monthlyBudget > 0) || deductibles < 0) {
        showError('Income and budget must be greater than zero. Deductibles cannot be negative.');
        return false;
    }

    const married = document.getElementById('is_married');
    if (married && married.checked) {
        const spouseFields = ['first_name_2', 'last_name_2', 'dob_2', 'ssn_last4_2'];
        for (const fieldId of spouseFields) {
            const field = document.getElementById(fieldId);
            if (!field || !field.value.trim()) {
                showError(`Please fill in ${getFieldLabel(fieldId)}.`);
                return false;
            }
        }

        const ssn2 = document.getElementById('ssn_last4_2').value.trim();
        if (!/^\d{4}$/.test(ssn2)) {
            showError('Client 2 SSN must be exactly 4 digits.');
            return false;
        }
    }
    
    return true;
}

function getFieldLabel(fieldId) {
    const label = document.querySelector(`label[for="${fieldId}"]`);
    if (label) {
        return label.textContent.replace('*', '').trim();
    }
    return fieldId.replaceAll('_', ' ');
}

function valueOrNull(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) {
        return null;
    }

    const value = field.value.trim();
    return value === '' ? null : value;
}

function numberOrNull(fieldId) {
    const value = valueOrNull(fieldId);
    return value === null ? null : parseFloat(value);
}

async function submitClientForm(isUpdate = false, clientId = null) {
    if (!validateClientForm()) {
        return;
    }
    
    const formData = {
        first_name_1: valueOrNull('first_name_1'),
        last_name_1: valueOrNull('last_name_1'),
        dob_1: valueOrNull('dob_1'),
        ssn_last4_1: valueOrNull('ssn_last4_1'),
        monthly_salary: numberOrNull('monthly_salary'),
        monthly_expense_budget: numberOrNull('monthly_expense_budget'),
        insurance_deductibles_total: numberOrNull('insurance_deductibles_total') || 0,
    };
    
    // Handle married client
    const married = document.getElementById('is_married');
    if (married && married.checked) {
        formData.first_name_2 = valueOrNull('first_name_2');
        formData.last_name_2 = valueOrNull('last_name_2');
        formData.dob_2 = valueOrNull('dob_2');
        formData.ssn_last4_2 = valueOrNull('ssn_last4_2');
    }
    
    try {
        const url = isUpdate ? `/clients/${clientId}` : '/clients';
        const method = isUpdate ? 'PUT' : 'POST';
        
        const { response, data } = await fetchJSON(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok && data && data.success) {
            showSuccess(data.message || 'Client saved successfully');
            setTimeout(() => {
                window.location.href = `/client_detail.html?id=${data.data.id}`;
            }, 1000);
        } else {
            showError(getApiErrorMessage(data, 'Failed to save client'));
        }
    } catch (error) {
        console.error('Error saving client:', error);
        showError('Error saving client');
    }
}
