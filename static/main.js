// Function to toggle dark mode
function toggleDarkMode() {
    // Toggle dark mode class on the body
    document.body.classList.toggle('dark-mode');

    // Save the current theme in localStorage
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
}

// Check if there's a saved theme in localStorage and apply it
window.onload = function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const eventSource = new EventSource('/sse');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // Assuming you have an element with id 'jsonDisplay' to show the data
        document.getElementById('jsonDisplay').textContent = JSON.stringify(data, null, 2);
    };

    eventSource.onerror = function(error) {
        console.error('Error with SSE:', error);
        eventSource.close();  // Close the connection on error
    };
});
