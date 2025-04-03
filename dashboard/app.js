const baseUrl = window.location.hostname === 'localhost' 
    ? 'http://localhost' 
    : `http://${window.location.hostname}`;

const PROCESSING_SERVICE_URL = `${baseUrl}/processing`;
const ANALYZER_SERVICE_URL = `${baseUrl}/analyzer`;

// Update frequency in milliseconds (3 seconds)
const UPDATE_INTERVAL = 3000;

// Function to format date
function formatDate(date) {
    return new Date(date).toLocaleString();
}

// Function to safely update an element's text content
function updateElementText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value !== undefined ? value : 'N/A';
    }
}

// Function to fetch processing stats
async function fetchProcessingStats() {
    try {
        const response = await fetch(`${PROCESSING_SERVICE_URL}/stats`);
        if (!response.ok) throw new Error('Failed to fetch processing stats');
        
        const data = await response.json();
        const totalEvents = (data.num_temperature_readings || 0) + (data.num_traffic_readings || 0);

        updateElementText('totalEvents', totalEvents);
        updateElementText('successEvents', totalEvents);
        updateElementText('failedEvents', '0'); // Placeholder since failures aren't tracked

        updateElementText('numTemperature', data.num_temperature_readings);
        updateElementText('maxTemperature', data.max_temperature);
        updateElementText('numTraffic', data.num_traffic_readings);
        updateElementText('maxTrafficDensity', data.max_traffic_density);
        
        if (data.last_updated) {
            updateElementText('lastUpdated', formatDate(data.last_updated));
        }
    } catch (error) {
        console.error('Error fetching processing stats:', error);
        ['totalEvents', 'successEvents', 'failedEvents'].forEach(id => updateElementText(id, 'Error'));
    }
}

// Function to fetch analyzer stats
async function fetchAnalyzerStats() {
    try {
        const response = await fetch(`${ANALYZER_SERVICE_URL}/stats`);
        if (!response.ok) throw new Error('Failed to fetch analyzer stats');

        const data = await response.json();
        const totalAnalyzed = (data.num_temperature || 0) + (data.num_traffic || 0);

        updateElementText('totalAnalyzed', totalAnalyzed);
        updateElementText('tempEvents', data.num_temperature);
        updateElementText('trafficEvents', data.num_traffic);
    } catch (error) {
        console.error('Error fetching analyzer stats:', error);
        ['totalAnalyzed', 'tempEvents', 'trafficEvents'].forEach(id => updateElementText(id, 'Error'));
    }
}

// Function to fetch a sample event from the analyzer
async function fetchSampleEvent() {
    try {
        const eventTypes = ["TemperatureEvent", "TrafficEvent"];
        const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
        const randomIndex = Math.floor(Math.random() * 10);

        let response = await fetch(`${ANALYZER_SERVICE_URL}/${randomType}?index=${randomIndex}`);
        let data;

        if (!response.ok) {
            const fallbackType = randomType === "TemperatureEvent" ? "TrafficEvent" : "TemperatureEvent";
            response = await fetch(`${ANALYZER_SERVICE_URL}/${fallbackType}?index=${randomIndex}`);
        }

        data = response.ok ? await response.json() : { message: "No events available" };

        updateElementText('randomEvent', JSON.stringify(data, null, 2));
    } catch (error) {
        console.error('Error fetching sample event:', error);
        updateElementText('randomEvent', JSON.stringify({ error: "Failed to fetch event data" }, null, 2));
    }
}

// Function to update all data
async function updateDashboard() {
    await Promise.all([
        fetchProcessingStats(),
        fetchAnalyzerStats(),
        fetchSampleEvent()
    ]);
}

// Initial update
updateDashboard();

// Set up periodic updates
setInterval(updateDashboard, UPDATE_INTERVAL);
