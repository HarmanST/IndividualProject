document.addEventListener("DOMContentLoaded", function() {
    var map;
    var mapModal = document.getElementById('map-modal');
    var useMapButton = document.getElementById('use-map-button');
    var closeMapButton = document.getElementById('close-map');

    // Show the map modal when the "Use Map" button is clicked
    useMapButton.onclick = function() {
        mapModal.style.display = "block";

        // Initialize the map only once after the modal is displayed
        setTimeout(function() {
            if (!map) {
                map = L.map('map').setView([51.505, -0.09], 2); // Set initial map view
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                var marker;
                // Add a marker on the map where the user clicks
                map.on('click', function(e) {
                    if (marker) {
                        map.removeLayer(marker); // Remove existing marker if present
                    }
                    marker = L.marker(e.latlng).addTo(map); // Add a new marker at the clicked location
                    document.getElementById('latitude').value = e.latlng.lat; // Set latitude input value
                    document.getElementById('longitude').value = e.latlng.lng; // Set longitude input value
                    closeMap();  // Automatically close the map modal after selecting a location
                });
            } else {
                map.invalidateSize(); // Ensure the map is properly resized within the modal
            }
        }, 300); // Slight delay to ensure modal display before map initialization
    };

    // Close the map modal
    closeMapButton.onclick = function() {
        closeMap();
    };

    function closeMap() {
        mapModal.style.display = "none"; // Hide the map modal
    }

    // App selection modal handling
    var appModal = document.getElementById('app-modal');
    var selectAppsButton = document.getElementById('select-apps-button');
    var closeAppModalButton = document.getElementById('close-app-modal');
    var saveAppsButton = document.getElementById('save-apps-button');

    // Show the app selection modal
    selectAppsButton.onclick = function() {
        appModal.style.display = "block";
    };

    // Close the app selection modal
    closeAppModalButton.onclick = function() {
        appModal.style.display = "none";
    };

    // Save selected apps and update the hidden input field in the main form
    saveAppsButton.onclick = function() {
        var selectedApps = document.querySelectorAll('input[name="apps"]:checked');
        var appValues = Array.from(selectedApps).map(app => app.value); // Get the values of selected apps
        document.getElementById('selected-apps').value = appValues.join(',');  // Store selected apps as a comma-separated string in the hidden input field

        appModal.style.display = "none"; // Close the app modal
    };

    // Close the app modal if the user clicks outside of it
    window.onclick = function(event) {
        if (event.target == appModal) {
            appModal.style.display = "none";
        }
    };
});
