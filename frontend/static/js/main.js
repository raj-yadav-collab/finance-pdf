/* Main utilities and helpers */

// Determine API base URL. If frontend is served from a dev static server
// (like Live Server on port 5500) we default API_BASE to localhost:8000.
const API_BASE = window.API_BASE || (location.port && location.port !== '' && location.port !== String(window.__BACKEND_PORT__ || '')
    ? (location.port === '5500' ? 'http://localhost:8000' : '')
    : '');

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00Z');
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-error';
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

async function fetchJSON(url, options = {}) {
    try {
        // Prepend API_BASE for relative API calls when configured
        const target = (API_BASE && url.startsWith('/')) ? `${API_BASE}${url}` : url;
        const response = await fetch(target, options);
        const contentType = response.headers.get('content-type') || '';
        const data = contentType.includes('application/json') ? await response.json() : null;
        return { response, data };
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

function getApiErrorMessage(data, fallback = 'Request failed') {
    if (!data) {
        return fallback;
    }

    if (data.message) {
        return data.message;
    }

    if (typeof data.detail === 'string') {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {
        return data.detail.map(error => {
            const field = Array.isArray(error.loc) ? error.loc[error.loc.length - 1] : 'field';
            return `${field}: ${error.msg}`;
        }).join(' | ');
    }

    if (data.error) {
        return data.error;
    }

    return fallback;
}
