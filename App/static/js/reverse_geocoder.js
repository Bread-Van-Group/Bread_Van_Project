async function reverseGeocode(lat, lng) {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`;

  try {
    const res = await fetch(url, {
      headers: {
        // Nominatim requires a User-Agent identifying your app
        "Accept-Language": "en",
      },
    });
    const data = await res.json();

    return data ?? "Address not found";
  } catch (err) {
    return "Error fetching address";
  }
}
