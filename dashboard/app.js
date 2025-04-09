
/* Configuration for API endpoints */
const baseUrl = window.location.hostname === 'localhost' 
    ? 'http://localhost' 
    : `http://${window.location.hostname}`;


const PROCESSING_SERVICE_URL = `${baseUrl}/processing`;
const ANALYZER_SERVICE_URL = `${baseUrl}/analyzer`;

// Update frequency in milliseconds (4 seconds)
const UPDATE_INTERVAL = 4000;

// Function to format date
function getLocaleDateStr() {
    return new Date().toLocaleString();
}


// Generalized fetch function with error handling
const makeRequest = async (url) => {
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log("Received data: ", data);
        return data;
    } catch (error) {
        updateErrorMessages(error.message);
        throw error;
    }
};

// Function to update error messages
const updateErrorMessages = (message) => {
    // Check if messages container exists, create it if it doesn't
    let messagesContainer = document.getElementById("messages");
    if (!messagesContainer) {
        messagesContainer = document.createElement("div");
        messagesContainer.id = "messages";
        messagesContainer.className = "container mt-3 alert alert-danger";
        messagesContainer.style.display = "none";
        document.body.insertBefore(messagesContainer, document.querySelector(".container").nextSibling);
    }

    const id = Date.now();
    console.log("Creation", id);
    let msg = document.createElement("div");
    msg.id = `error-${id}`;
    msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`;
    messagesContainer.style.display = "block";
    messagesContainer.prepend(msg);
    setTimeout(() => {
        const elem = document.getElementById(`error-${id}`);
        if (elem) { elem.remove(); }
        // If no more error messages, hide the container
        if (messagesContainer.children.length === 0) {
            messagesContainer.style.display = "none";
        }
    }, 7000);
};

// Function to update code display divs
const updateCodeDiv = (result, elemId) => {
    const element = document.getElementById(elemId);
    if (element) {
        element.innerText = JSON.stringify(result, null, 2);
    }
};

// Function to fetch processing stats
async function fetchProcessingStats() {
    try {

        const data = await makeRequest(`${PROCESSING_SERVICE_URL}/stats`);
        
        // Update main stats
        const totalEvents = (data.num_temperature_readings || 0) + (data.num_traffic_readings || 0);
        
        updateElementText('totalEvents', totalEvents);
        updateElementText('failedEvents', '0');
        updateElementText('successEvents', totalEvents);
        updateElementText('lastUpdated', getLocaleDateStr());
        
        // Update additional metrics
        updateElementText('maxTemperature', data.max_temperature || 0); 
        updateElementText('maxTrafficDensity', data.max_traffic_density || 0);
        
        // Update processing stats display if element exists
        updateCodeDiv(data, "processing-stats");
        
    } catch (error) {
        console.error('Error fetching processing stats:', error);
        updateElementText('totalEvents', 'Error');
        updateElementText('failedEvents', 'Error');
        updateElementText('successEvents', 'Error');

    }
}

// Function to fetch analyzer stats
async function fetchAnalyzerStats() {
    try {

        const data = await makeRequest(`${ANALYZER_SERVICE_URL}/stats`);
        
        // Update analyzer stats
        const totalAnalyzed = (data.num_temperature || 0) + (data.num_traffic || 0);
        
        updateElementText('totalAnalyzed', totalAnalyzed);
        updateElementText('tempEvents', data.num_traffic || 0); // Note: These seem swapped in the HTML
        updateElementText('trafficEvents', data.num_temperature || 0); // Note: These seem swapped in the HTML
        
        // Update analyzer stats display if element exists
        updateCodeDiv(data, "analyzer-stats");
        
    } catch (error) {
        console.error('Error fetching analyzer stats:', error);
        updateElementText('totalAnalyzed', 'Error');
        updateElementText('tempEvents', 'Error');
        updateElementText('trafficEvents', 'Error');
    }
}

// Helper function to safely update element text
function updateElementText(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    }
}

// Function to fetch random events
async function fetchRandomEvent() {
    try {
        // Get random event
        const randomType = Math.random() > 0.5 ? "TemperatureEvent" : "TrafficEvent";
        const randomIndex = Math.floor(Math.random() * 10);
        
        try {
            const randomData = await makeRequest(`${ANALYZER_SERVICE_URL}/${randomType}?index=${randomIndex}`);
            updateElementText('randomEvent', JSON.stringify(randomData, null, 2));
            
            // Update individual event displays if they exist
            if (randomType === "TemperatureEvent") {
                updateCodeDiv(randomData, "event-temperature");
            } else {
                updateCodeDiv(randomData, "event-traffic");
            }
            
        } catch (randomError) {
            console.error('Error fetching random event:', randomError);
            updateElementText('randomEvent', JSON.stringify({ error: "Failed to fetch event data" }, null, 2));
        }
        
    } catch (error) {
        console.error('Error in fetchRandomEvent:', error);

    }
}

// Function to update all data
async function updateDashboard() {
    // Update last updated timestamp - using the existing element in your HTML
    updateElementText('lastUpdated', getLocaleDateStr());
    
    await Promise.all([
        fetchProcessingStats(),
        fetchAnalyzerStats(),
        fetchSampleEvent()
    ]);
}

// Function to set up the dashboard
function setup() {
    // Initial update
    updateDashboard();
    
    // Set up periodic updates
    setInterval(updateDashboard, UPDATE_INTERVAL);
}

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', setup);