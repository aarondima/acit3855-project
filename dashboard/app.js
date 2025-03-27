// API endpoints
const PROCESSING_SERVICE_URL = 'http://localhost:8100';
const ANALYZER_SERVICE_URL = 'http://localhost:8101';

// Update frequency in milliseconds (3 seconds)
const UPDATE_INTERVAL = 3000;

// Function to format date
function formatDate(date) {
    return new Date(date).toLocaleString();
}

// Function to fetch processing stats
async function fetchProcessingStats() {
    try {
        const response = await fetch(`${PROCESSING_SERVICE_URL}/stats`);
        const data = await response.json();
        
        document.getElementById('totalEvents').textContent = data.num_events_received || 0;
        document.getElementById('failedEvents').textContent = data.num_failed_events || 0;
        document.getElementById('successEvents').textContent = 
            (data.num_events_received || 0) - (data.num_failed_events || 0);
        
        if (data.last_updated) {
            document.getElementById('lastUpdated').textContent = formatDate(data.last_updated);
        }
    } catch (error) {
        console.error('Error fetching processing stats:', error);
    }
}

// Function to fetch analyzer stats
async function fetchAnalyzerStats() {
    try {
        const response = await fetch(`${ANALYZER_SERVICE_URL}/stats`);
        const data = await response.json();
        
        document.getElementById('totalAnalyzed').textContent = data.num_events_analyzed || 0;
        document.getElementById('maxPrice').textContent = data.max_price ? `$${data.max_price.toFixed(2)}` : '-';
        document.getElementById('minPrice').textContent = data.min_price ? `$${data.min_price.toFixed(2)}` : '-';
    } catch (error) {
        console.error('Error fetching analyzer stats:', error);
    }
}

// Function to fetch a random event
async function fetchRandomEvent() {
    try {
        const response = await fetch(`${ANALYZER_SERVICE_URL}/events/random`);
        const data = await response.json();
        
        document.getElementById('randomEvent').textContent = 
            JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error fetching random event:', error);
    }
}

// Function to update all data
async function updateDashboard() {
    await Promise.all([
        fetchProcessingStats(),
        fetchAnalyzerStats(),
        fetchRandomEvent()
    ]);
}

// Initial update
updateDashboard();

// Set up periodic updates
setInterval(updateDashboard, UPDATE_INTERVAL);
