// static/js/main.js

// --- Get references to DOM elements ---
const form = document.getElementById('upload-form');
const resultsArea = document.getElementById('results-area');
const loadingIndicator = document.getElementById('loading-indicator');
const fileInput = document.getElementById('bottle-input');
const submitButton = document.getElementById('submit-button');

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
    resultContainer.className = 'bg-white shadow-lg rounded-lg px-6 py-6 md:px-8'; // Padding and styling

    // Add Title
    const title = document.createElement('h2');
    title.className = 'text-2xl font-semibold mb-4 text-gray-800 border-b pb-2';
    title.textContent = 'Match Found!';
    resultContainer.appendChild(title);

    // Highlighted Name (if available)
    if (data.name) {
        const nameHeader = document.createElement('h3');
        nameHeader.className = 'text-xl font-bold mb-4 text-indigo-700';
        nameHeader.textContent = data.name;
        resultContainer.appendChild(nameHeader);
    }

    // Create Definition List for details
    const detailsList = document.createElement('dl');
    // Responsive grid: 1 column on small screens, 2 on medium and up
    detailsList.className = 'grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 text-sm';

    // Loop through the data object properties
    for (const [key, value] of Object.entries(data)) {
        // Skip internal keys we added or keys we don't want displayed directly
        if (key.startsWith('_match_')) continue;
        if (key === 'name' && data.name) continue; // Skip name if already displayed as header

        // Format the key nicely (e.g., 'avg_msrp' -> 'Avg Msrp')
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const displayValue = (value !== null && value !== undefined && value !== '')
                             ? value
                             : '<span class="text-gray-500 italic">N/A</span>'; // Handle null/empty values

        // Create Term (dt) and Description (dd) elements
        const term = document.createElement('dt');
        term.className = 'font-medium text-gray-600';
        term.textContent = formattedKey;

        const description = document.createElement('dd');
        description.className = 'text-gray-900 mb-2 md:mb-0'; // Add bottom margin on mobile
        description.innerHTML = displayValue; // Use innerHTML to render the 'N/A' span correctly

        // Append to the list
        detailsList.appendChild(term);
        detailsList.appendChild(description);
    }

    // Add Match Confidence details separately at the end
    const confidenceTerm = document.createElement('dt');
    confidenceTerm.className = 'font-medium text-gray-600 mt-3 pt-3 border-t md:col-span-1'; // Spans one column, adds top border
    confidenceTerm.textContent = 'Match Confidence';

    const confidenceDesc = document.createElement('dd');
    confidenceDesc.className = 'text-gray-900 mt-3 pt-3 border-t md:col-span-1'; // Spans one column, adds top border
    confidenceDesc.textContent = `${data._match_good_matches || 'N/A'} good keypoints matched`;

    detailsList.appendChild(confidenceTerm);
    detailsList.appendChild(confidenceDesc);


    // Append the list to the container and the container to the results area
    resultContainer.appendChild(detailsList);
    resultsArea.appendChild(resultContainer);
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
