// static/js/main.js

// --- Get references to DOM elements ---
const form = document.getElementById('upload-form');
const resultsArea = document.getElementById('results');
const loadingIndicator = document.getElementById('loading');
const fileInput = document.getElementById('bottle-input');
const submitButton = document.getElementById('submit-button');
const historyList = document.getElementById('history-list');
const historyToggle = document.getElementById('history-toggle');
const historySidebar = document.getElementById('history-sidebar');
const closeHistory = document.getElementById('close-history');
const historyOverlay = document.getElementById('history-overlay');
const themeToggle = document.getElementById('theme-toggle');
const cameraButton = document.getElementById('camera-button');
const cameraModal = document.getElementById('camera-modal');
const closeCamera = document.getElementById('close-camera');
const cameraPreview = document.getElementById('camera-preview');
const cameraCanvas = document.getElementById('camera-canvas');
const takePhotoButton = document.getElementById('take-photo');
let analysisHistory = [];
let stream = null;

// Theme Management
function handleTransition(e, isDark) {
    const overlay = document.getElementById('theme-transition');
    const rect = themeToggle.getBoundingClientRect();
    const x = e ? (e.clientX - rect.left) : (rect.width / 2);
    const y = e ? (e.clientY - rect.top) : (rect.height / 2);
    
    overlay.style.setProperty('--x', x + 'px');
    overlay.style.setProperty('--y', y + 'px');
    
    overlay.classList.add('active');
    
    setTimeout(() => {
        setTheme(isDark);
        setTimeout(() => {
            overlay.classList.remove('active');
        }, 500);
    }, 50);
}

function setTheme(isDark) {
    const html = document.documentElement;
    const body = document.body;
    if (isDark) {
        html.classList.add('dark');
        body.classList.add('dark');
        localStorage.theme = 'dark';
    } else {
        html.classList.remove('dark');
        body.classList.remove('dark');
        localStorage.theme = 'light';
    }
}

// History Management Functions
function addToHistory(data) {
    // Add the result to history
    analysisHistory.unshift({
        name: data.name || 'Unknown Bottle',
        msrp: data.avg_msrp || 'N/A',
        confidence: data._match_good_matches || 0,
        timestamp: new Date().toLocaleTimeString()
    });

    // Update the history UI
    updateHistoryUI();
}

function updateHistoryUI() {
    if (historyList) {
        historyList.innerHTML = analysisHistory.map(item => `
            <div class="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg shadow">
                <div class="font-bold text-gray-800 dark:text-gray-200 mb-2">${item.name}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                    <div>Avg MSRP: $${typeof item.msrp === 'number' ? item.msrp.toFixed(2) : item.msrp}</div>
                    <div>Match Confidence: ${item.confidence} keypoints matched</div>
                    <div class="text-xs mt-1">${item.timestamp}</div>
                </div>
            </div>
        `).join('');
    }
}

function toggleHistory() {
    historySidebar.classList.toggle('translate-x-full');
    historyOverlay.classList.toggle('hidden');
    document.body.classList.toggle('overflow-hidden');
}

// Camera functionality
async function startCamera() {
    try {
        // First check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API is not supported in your browser');
        }

        // Request camera access with options
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        });

        // Set up the video stream
        cameraPreview.srcObject = stream;
        await cameraPreview.play(); // Ensure video starts playing
        cameraModal.classList.remove('hidden');
        cameraModal.classList.add('flex');
    } catch (err) {
        console.error('Error accessing camera:', err);
        if (err.name === 'NotAllowedError') {
            alert('Camera access was denied. Please grant camera permissions to use this feature.');
        } else if (err.name === 'NotFoundError') {
            alert('No camera found on your device.');
        } else {
            alert('Could not access camera: ' + err.message);
        }
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    cameraPreview.srcObject = null;
    cameraModal.classList.add('hidden');
    cameraModal.classList.remove('flex');
}

async function takePhoto() {
    if (!stream) {
        console.error('No active camera stream');
        return;
    }

    const context = cameraCanvas.getContext('2d');
    cameraCanvas.width = cameraPreview.videoWidth;
    cameraCanvas.height = cameraPreview.videoHeight;
    context.drawImage(cameraPreview, 0, 0, cameraCanvas.width, cameraCanvas.height);
    
    // Convert canvas to blob
    try {
        const blob = await new Promise((resolve) => {
            cameraCanvas.toBlob(resolve, 'image/jpeg', 0.95);
        });
        
        const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
        
        // Create FormData and append file
        const formData = new FormData();
        formData.append('bottle_image', file);
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        submitButton.disabled = true;
    
        try {
            const response = await fetch('/identify', {
                method: 'POST',
                body: formData
            });
            
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const result = await response.json();
                if (response.ok && result.success) {
                    displayResults(result.data);
                } else {
                    displayError(result.error || 'An unknown error occurred while processing the image.');
                }
            } else {
                const errorText = await response.text();
                console.error("Received non-JSON response:", errorText);
                displayError(`Server returned an unexpected response (Status: ${response.status}). Please check server logs.`);
            }
        } catch (error) {
            console.error('Error:', error);
            displayError('An error occurred while processing the image.');
        } finally {
            loadingIndicator.style.display = 'none';
            submitButton.disabled = false;
            stopCamera();
        }
    } catch (error) {
        console.error('Error creating blob:', error);
        displayError('Failed to capture image from camera.');
    }
}

// --- Add event listener for form submission ---
form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior (page reload)

    // --- Basic Validation ---
    if (!fileInput.files || fileInput.files.length === 0) {
        displayError("Please select an image file first.");
        return; // Stop if no file is selected
    }

    // --- UI Updates: Show Loading State ---
    resultsArea.innerHTML = ''; // Clear any previous results or errors
    loadingIndicator.style.display = 'block'; // Show the loading spinner/text
    submitButton.disabled = true; // Disable the button to prevent multiple submissions
    submitButton.textContent = 'Identifying...'; // Optional: Change button text

    // --- Prepare Form Data for Sending ---
    const formData = new FormData();
    formData.append('bottle_image', fileInput.files[0]); // 'bottle_image' must match the name Flask expects

    // --- Send Data to Backend API ---
    try {
        const response = await fetch('/identify', { // URL of your Flask API endpoint
            method: 'POST',
            body: formData,
            // Note: 'Content-Type': 'multipart/form-data' header is usually set automatically by the browser when using FormData with fetch
        });

        // --- Process Backend Response ---
        const contentType = response.headers.get("content-type");
        // Check if the response is valid JSON
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const result = await response.json(); // Parse the JSON response body

            if (response.ok && result.success) {
                // Call function to display successful results
                displayResults(result.data);
            } else {
                // Call function to display error message from backend
                displayError(result.error || 'An unknown error occurred while processing the image.');
            }
        } else {
             // Handle cases where the server returns non-JSON (e.g., HTML error page)
             const errorText = await response.text();
             console.error("Received non-JSON response:", errorText);
             displayError(`Server returned an unexpected response (Status: ${response.status}). Please check server logs.`);
        }
        
    } catch (error) {
        // --- Handle Network Errors ---
        console.error('Fetch Error:', error);
        displayError('Failed to connect to the identification server. Please check your network connection or contact support.');
    } finally {
        // --- UI Updates: Hide Loading State (always runs) ---
        loadingIndicator.style.display = 'none'; // Hide the loading spinner/text
        submitButton.disabled = false; // Re-enable the button
        submitButton.textContent = 'Identify Bottle'; // Restore original button text
        // Optional: Clear the file input after submission for better UX
        // fileInput.value = '';
    }
});

/**
 * Displays the identified bottle details in the results area.
 * @param {object} data - The bottle details object received from the backend.
 */
function displayResults(data) {
    // Clear previous content
    resultsArea.innerHTML = '';

    // Create the main container for results with Tailwind classes
    const resultContainer = document.createElement('div');
    resultContainer.className = 'bg-white dark:bg-gray-800 shadow-lg rounded-lg px-6 py-6 md:px-8'; // Added dark mode support

    // Add Title
    const title = document.createElement('h2');
    title.className = 'text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-200 border-b pb-2';
    title.textContent = 'Match Found!';
    resultContainer.appendChild(title);

    // Highlighted Name (if available)
    if (data.name) {
        const nameHeader = document.createElement('h3');
        nameHeader.className = 'text-xl font-bold mb-4 text-indigo-700 dark:text-indigo-400';
        nameHeader.textContent = data.name;
        resultContainer.appendChild(nameHeader);
    }

    // Create Definition List for details
    const detailsList = document.createElement('dl');
    detailsList.className = 'grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 text-sm';

    // Loop through the data object properties
    for (const [key, value] of Object.entries(data)) {
        // Skip internal keys we added or keys we don't want displayed directly
        if (key.startsWith('_match_')) continue;
        if (key === 'name' && data.name) continue;

        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const displayValue = (value !== null && value !== undefined && value !== '')
                             ? value
                             : '<span class="text-gray-500 dark:text-gray-400 italic">N/A</span>';

        const term = document.createElement('dt');
        term.className = 'font-medium text-gray-600 dark:text-gray-400';
        term.textContent = formattedKey;

        const description = document.createElement('dd');
        description.className = 'text-gray-900 dark:text-gray-200 mb-2 md:mb-0';
        description.innerHTML = displayValue;

        detailsList.appendChild(term);
        detailsList.appendChild(description);
    }

    // Add Match Confidence details separately at the end
    const confidenceTerm = document.createElement('dt');
    confidenceTerm.className = 'font-medium text-gray-600 dark:text-gray-400 mt-3 pt-3 border-t md:col-span-1';
    confidenceTerm.textContent = 'Match Confidence';

    const confidenceDesc = document.createElement('dd');
    confidenceDesc.className = 'text-gray-900 dark:text-gray-200 mt-3 pt-3 border-t md:col-span-1';
    confidenceDesc.textContent = `${data._match_good_matches || 'N/A'} good keypoints matched`;

    detailsList.appendChild(confidenceTerm);
    detailsList.appendChild(confidenceDesc);

    // Append the list to the container and the container to the results area
    resultContainer.appendChild(detailsList);
    resultsArea.appendChild(resultContainer);

    // Add to history
    addToHistory(data);
}

/**
 * Displays an error message in the results area.
 * @param {string} errorMessage - The error message to display.
 */
function displayError(errorMessage) {
     // Clear previous content
    resultsArea.innerHTML = '';

    // Create error message container with Tailwind classes
    const errorContainer = document.createElement('div');
    errorContainer.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative shadow'; // Styling for error box
    errorContainer.setAttribute('role', 'alert');

    const errorTitle = document.createElement('strong');
    errorTitle.className = 'font-bold mr-2';
    errorTitle.textContent = 'Identification Failed:';
    errorContainer.appendChild(errorTitle);

    const errorMessageSpan = document.createElement('span');
    errorMessageSpan.className = 'block sm:inline'; // Responsive display
    errorMessageSpan.textContent = errorMessage;
    errorContainer.appendChild(errorMessageSpan);

    // Append the error message to the results area
    resultsArea.appendChild(errorContainer);
}

// Event Listeners
if (cameraButton) cameraButton.addEventListener('click', startCamera);
if (closeCamera) closeCamera.addEventListener('click', stopCamera);
if (takePhotoButton) takePhotoButton.addEventListener('click', takePhoto);

if (themeToggle) {
    themeToggle.addEventListener('click', (e) => {
        handleTransition(e, !document.documentElement.classList.contains('dark'));
    });
}

if (historyToggle) {
    historyToggle.addEventListener('click', toggleHistory);
}

if (closeHistory) {
    closeHistory.addEventListener('click', toggleHistory);
}

if (historyOverlay) {
    historyOverlay.addEventListener('click', toggleHistory);
}

// Initial theme setup
if (localStorage.theme === 'light') {
    setTheme(false);
} else {
    setTheme(true);
}

// Clean up camera when page is unloaded
window.addEventListener('beforeunload', stopCamera);
