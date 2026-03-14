const API_BASE = 'http://localhost:5000/api';

// DOM Elements
const searchInput = document.getElementById('customerSearch');
const searchResults = document.getElementById('searchResults');
const welcomeState = document.getElementById('welcomeState');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const dashboard = document.getElementById('predictionDashboard');

// Data Elements
const predictedSpendNum = document.getElementById('predictedSpend');
const displayCustId = document.getElementById('displayCustId');
const metricRecency = document.getElementById('metricRecency');
const metricFrequency = document.getElementById('metricFrequency');
const metricMonetary = document.getElementById('metricMonetary');
const metricAOV = document.getElementById('metricAOV');

// State
let customers = [];
let searchTimeout;

// Initialize Icons
lucide.createIcons();

// Initial Load
async function fetchCustomers() {
    try {
        const response = await fetch(`${API_BASE}/customers?limit=1000`);
        const data = await response.json();
        if (data.customers) {
            customers = data.customers;
            console.log(`Loaded ${customers.length} customers for search.`);
        }
    } catch (e) {
        console.error("Failed to fetch customers:", e);
    }
}

// Search Logic
searchInput.addEventListener('input', (e) => {
    const value = e.target.value.toLowerCase().trim();
    clearTimeout(searchTimeout);

    if (value.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }

    searchTimeout = setTimeout(() => {
        const matches = customers.filter(c => c.toLowerCase().includes(value)).slice(0, 10);
        renderSearchResults(matches);
    }, 300);
});

// Close search results when clicking outside
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.add('hidden');
    }
});

function renderSearchResults(matches) {
    searchResults.innerHTML = '';

    if (matches.length === 0) {
        const div = document.createElement('div');
        div.className = 'search-item text-muted';
        div.textContent = 'No customers found';
        searchResults.appendChild(div);
    } else {
        matches.forEach(id => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.innerHTML = `<i data-lucide="user" class="icon sm text-primary"></i> ${id}`;
            div.addEventListener('click', () => selectCustomer(id));
            searchResults.appendChild(div);
        });
        lucide.createIcons();
    }

    searchResults.classList.remove('hidden');
}

function showState(stateElement) {
    [welcomeState, loadingState, errorState, dashboard].forEach(el => {
        if (el === stateElement) {
            el.classList.remove('hidden');
            el.classList.add('visible');
        } else {
            el.classList.add('hidden');
            el.classList.remove('visible');
        }
    });
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        // Easing out quint
        const easeOut = 1 - Math.pow(1 - progress, 5);
        const current = start + easeOut * (end - start);

        // Formatting
        if (Number.isInteger(end)) {
            obj.innerHTML = Math.floor(current).toLocaleString();
        } else {
            obj.innerHTML = current.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Fetch prediction and render
async function selectCustomer(id) {
    searchInput.value = id;
    searchResults.classList.add('hidden');
    showState(loadingState);

    try {
        const response = await fetch(`${API_BASE}/predict/${id}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }

        renderDashboard(data);
    } catch (e) {
        errorMessage.textContent = e.message;
        showState(errorState);
    }
}

function renderDashboard(data) {
    displayCustId.textContent = data.cust_id;

    // Animate numbers up for premium feel
    animateValue(predictedSpendNum, 0, data.prediction, 1500);
    animateValue(metricRecency, 0, data.metrics.recency, 1000);
    animateValue(metricFrequency, 0, data.metrics.frequency, 1000);
    animateValue(metricMonetary, 0, data.metrics.monetary, 1000);
    animateValue(metricAOV, 0, data.metrics.avg_order_value, 1000);

    showState(dashboard);
}

// Start
fetchCustomers();
