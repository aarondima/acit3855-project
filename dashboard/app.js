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

// Function to fetch processing stats
async function fetchProcessingStats() {
    try {
        const response = await fetch(`${PROCESSING_SERVICE_URL}/stats`);
        const data = await response.json();
       
        document.getElementById('totalEvents').textContent = 
            (data.num_temperature_readings || 0) + (data.num_traffic_readings || 0);
        
        // Since your processing service doesn't track failed events directly,
        // we'll leave this blank or use a placeholder
        document.getElementById('failedEvents').textContent = '0';
        
        document.getElementById('successEvents').textContent =
            (data.num_temperature_readings || 0) + (data.num_traffic_readings || 0);
       
        if (data.last_updated) {
            document.getElementById('lastUpdated').textContent = formatDate(data.last_updated);
        }
        
        // Display additional temperature and traffic metrics if available
        if (document.getElementById('numTemperature')) {
            document.getElementById('numTemperature').textContent = data.num_temperature_readings || 0;
        }
        
        if (document.getElementById('maxTemperature')) {
            document.getElementById('maxTemperature').textContent = data.max_temperature || 0;
        }
        
        if (document.getElementById('numTraffic')) {
            document.getElementById('numTraffic').textContent = data.num_traffic_readings || 0;
        }
        
        if (document.getElementById('maxTrafficDensity')) {
            document.getElementById('maxTrafficDensity').textContent = data.max_traffic_density || 0;
        }
    } catch (error) {
        console.error('Error fetching processing stats:', error);
        document.getElementById('totalEvents').textContent = 'Error';
        document.getElementById('failedEvents').textContent = 'Error';
        document.getElementById('successEvents').textContent = 'Error';
    }
}

// Function to fetch analyzer stats
async function fetchAnalyzerStats() {
    try {
        const response = await fetch(`${ANALYZER_SERVICE_URL}/stats`);
        const data = await response.json();
       
        // Update with analyzer stats - using the event counts from the analyzer service
        document.getElementById('totalAnalyzed').textContent = 
            (data.num_temperature || 0) + (data.num_traffic || 0);
        
        // Your analyzer doesn't track prices, so repurpose these fields
        // or replace with more relevant metrics
        document.getElementById('tempEvents').textContent = data.num_temperature || 0;
        document.getElementById('trafficEvents').textContent = data.num_traffic || 0;
        
        // You might want to rename these labels in your HTML to match the data
        // For example, change "Max Price" to "Temperature Events"
        // and "Min Price" to "Traffic Events"
    } catch (error) {
        console.error('Error fetching analyzer stats:', error);
        document.getElementById('totalAnalyzed').textContent = 'Error';
        document.getElementById('tempEvents').textContent = 'Error';
        document.getElementById('trafficEvents').textContent = 'Error';
    }
}

// Function to fetch a sample event from the analyzer
async function fetchSampleEvent() {
    try {
        const eventTypes = ["TemperatureEvent", "TrafficEvent"];  // Match backend route names
        const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
        const randomIndex = Math.floor(Math.random() * 10); // Adjust range as needed

        let response = await fetch(`http://localhost:8110/${randomType}?index=${randomIndex}`);
        let data;

        if (response.ok) {
            data = await response.json();
        } else {
            // Try the other event type if the first one fails
            const fallbackType = randomType === "TemperatureEvent" ? "TrafficEvent" : "TemperatureEvent";
            response = await fetch(`http://localhost:8110/${fallbackType}?index=${randomIndex}`);

            if (response.ok) {
                data = await response.json();
            } else {
                data = { message: "No events available" };
            }
        }

        document.getElementById('randomEvent').textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error fetching sample event:', error);
        document.getElementById('randomEvent').textContent = JSON.stringify({ error: "Failed to fetch event data" }, null, 2);
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