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

        // Get the container to hold all the helpy cards
        const helpyCardsContainer = document.getElementById('helpyCardsContainer');
        helpyCardsContainer.innerHTML = ''; // Clear existing cards before adding new ones

        // Loop through each Helpy and create a card for it
        for (const helpyName in data) {
            const helpyData = data[helpyName];
            
            // Determine the direction based on rotation
            let rotationDirection = '';
            switch (helpyData.transform.rotation) {
                case 0:
                    rotationDirection = 'North';
                    break;
                case 1:
                    rotationDirection = 'East';
                    break;
                case 2:
                    rotationDirection = 'South';
                    break;
                case 3:
                    rotationDirection = 'West';
                    break;
                default:
                    rotationDirection = 'toward the 4th dimension'; // Easter egg for unexpected rotation values
                    break;
            }
            
            // Create card element
            const card = document.createElement('div');
            card.classList.add('helpy-card');
            
            // Add card content
            card.innerHTML = `
                <h3>${helpyName}</h3>
                <p><strong>State:</strong> ${helpyData.state}</p>
                <p><strong>World Position:</strong> X: ${helpyData.transform.position.x}, Y: ${helpyData.transform.position.y}, Z: ${helpyData.transform.position.z}</p>
                <p><strong>Facing:</strong> ${rotationDirection}</p>
                <p><strong>Last Seen:</strong> ${helpyData.LastSeen}</p>
            `;
            
            // Append the card to the container
            helpyCardsContainer.appendChild(card);
        }
    };

    eventSource.onerror = function(error) {
        console.error('Error with SSE:', error);
        eventSource.close();  // Close the connection on error
    };
});
