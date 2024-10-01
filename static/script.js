//This file uses the open source javascipt library Leaflet (2019). Leaflet — an open-source JavaScript library for interactive maps.
// [online] Leafletjs.com. Available at: https://leafletjs.com/.

var map;
var mapModal = document.getElementById('map-modal');
var useMapButton = document.getElementById('use-map-button');
var closeMapButton = document.getElementById('close-map');

useMapButton.onclick = function() {
    mapModal.style.display = "block";

    if (!map) {
        map = L.map('map').setView([51.505, -0.09], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        var marker;
        map.on('click', function(e) {
            if (marker) {
                map.removeLayer(marker);
            }
            marker = L.marker(e.latlng).addTo(map);
            document.getElementById('latitude').value = e.latlng.lat;
            document.getElementById('longitude').value = e.latlng.lng;
            closeMap();  // Automatically close the map after selecting a location
        });
    }
    setTimeout(function() {
        map.invalidateSize(); // Fix map rendering issue when opening modal
    }, 100);
};

closeMapButton.onclick = function() {
    closeMap();
};

function closeMap() {
    mapModal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == mapModal) {
        closeMap();
    }
}
