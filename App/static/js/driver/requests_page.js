var pendingMarkers = [];
var tempLeafletMarkers = {};

async function getPendingMarkers() {
  const res = await fetch("/api/driver/pending-stops");
  const json = await res.json();

  return json;
}

async function loadPendingMarkers() {
  pendingMarkers = await getPendingMarkers();

  //Fly to center of markers
  if (pendingMarkers.length > 0) {
    const latLngs = pendingMarkers.map((m) => [m.lat, m.lng]);
    const bounds = L.latLngBounds(latLngs);

    const center = bounds.getCenter();
    map.flyTo(center, 17);
  }

  //Add markers to map and allow you to click to focus on it
  pendingMarkers.forEach(function (marker) {
    let mapMarker = L.marker([marker.lat, marker.lng], {
      icon: newMarkerIcon,
    }).addTo(map);

    tempLeafletMarkers[marker.stop_id] = mapMarker;
    mapMarker.on("click", function (e) {
      if (currentlySelectedMarker) {
        //This is done to get correct icon to display for previous selected marker
        const isNewMarker = pendingMarkers.find(
          (m) =>
            m.lat == currentlySelectedMarker._latlng.lat &&
            m.lng == currentlySelectedMarker._latlng.lng,
        );

        if (isNewMarker != undefined)
          currentlySelectedMarker.setIcon(newMarkerIcon);
        else currentlySelectedMarker.setIcon(markerIcon);
      }

      // Set this marker as selected
      mapMarker.setIcon(selectedMarkerIcon);
      currentlySelectedMarker = mapMarker;

      map.flyTo([marker.lat, marker.lng], 17);
      const waypoints = [
        breadVanDummyMarker.getLatLng(),
        ...markers.map((m) => L.latLng(m.lat, m.lng)),
        L.latLng(marker.lat, marker.lng),
      ];
      buildRoute(waypoints);
    });
  });
}

//This function is used in the frontend to go to the selected marker
function goToMarker(markerId) {
  const marker = pendingMarkers.find(
    (m) => Number(m.stop_id) === Number(markerId),
  );

  const leafletMarker = tempLeafletMarkers[markerId];

  if (!marker) return;

  if (currentlySelectedMarker) {
    //This is done to get correct icon to display for previous selected marker
    const isNewMarker = pendingMarkers.find(
      (m) =>
        m.lat == currentlySelectedMarker._latlng.lat &&
        m.lng == currentlySelectedMarker._latlng.lng,
    );

    if (isNewMarker != undefined)
      currentlySelectedMarker.setIcon(newMarkerIcon);
    else currentlySelectedMarker.setIcon(markerIcon);
  }

  // Set this marker as selected
  leafletMarker.setIcon(selectedMarkerIcon);
  currentlySelectedMarker = leafletMarker;

  map.flyTo([marker.lat, marker.lng], 17);

  const waypoints = [
    breadVanDummyMarker.getLatLng(),
    ...markers.map((m) => L.latLng(m.lat, m.lng)),
    L.latLng(marker.lat, marker.lng),
  ];

  buildRoute(waypoints);
}

//Execution of code
(async () => {
  await loadPendingMarkers();
})();
