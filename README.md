# Live Aircraft Radar

A real-time ADS-B aircraft radar built with Python and Folium. It fetches live flight telemetry from the [adsb.lol API](https://adsb.lol) and plots active aircraft within a **463 km (250 NM)** radius around Hyderabad, India, featuring an interactive airline filter sidebar, live per-airline flight counts, directional aircraft icons, and automatic 10-second updates.

<img width="1876" height="1080" alt="Screenshot 2026-11-19 004019" src="https://github.com/user-attachments/assets/2f67b604-9c2a-44b2-b5ac-396baac07e7b" />

## Features

- **463 km Regional Coverage:** Monitors live air traffic across a 463 km radius (926 km diameter) centered on Rajiv Gandhi International Airport (HYD), complete with a dashed radar range ring.

- **Interactive Airline Filter & Live Counts:** Includes an interactive layer control panel in the top-right corner with color-coded checkboxes and real-time flight counts for each airline (IndiGo, Air India, Air India Express, Akasa Air, SpiceJet, Emirates, Qatar Airways, British Airways, Singapore Airlines, and Other/Cargo/Private), allowing you to toggle specific carriers on or off instantly.

- **Directional Aircraft Icons:** Renders custom SVG airplane markers dynamically rotated to match each flight's true compass heading.

- **Live Telemetry Popups:** Hover over any aircraft for a quick altitude summary or click to inspect full flight details (Airline, Callsign, Aircraft Type, Barometric Altitude, Ground Speed, and Compass Heading).

- **Auto-Refreshing Radar Loop:** Polls live ADS-B data every 10 seconds and serves the interactive OpenStreetMap view locally over HTTP with zero API keys required.

## Tech Stack

- **Language:** Python 3
- **Libraries:** `requests`, `folium`, `http.server`
- **Data Source:** [adsb.lol v2 API](https://adsb.lol)

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd live-aircraft-radar
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the radar:**
   ```bash
   python radar.py
   ```
   The script starts a local server at `http://localhost:8000/live_flights.html` and automatically opens the live radar in your browser. Press `Ctrl + C` in the terminal to stop.

## Configuration

You can customize the radar center, range, refresh interval, and airline colors at the top of `radar.py`:

```python
HYD_LAT = 17.2403        # Center latitude (Shamshabad Airport, Hyderabad)
HYD_LON = 78.4294        # Center longitude
RADIUS_KM = 463          # Radar radius in kilometers (max 463 km / 250 NM)
REFRESH_SECONDS = 10     # Map refresh interval in seconds
```

## License

This project is open source and available under the [MIT License](LICENSE).
