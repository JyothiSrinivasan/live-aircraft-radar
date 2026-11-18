import requests
import folium
import webbrowser
import threading
import time
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

HYD_LAT = 17.2403
HYD_LON = 78.4294
RADIUS_KM = 463
RADIUS_NM = min(250, int(round(RADIUS_KM / 1.852)))
REFRESH_SECONDS = 60

# Map 3-letter ICAO airline callsign prefixes to (Airline Name, Hex Color)
AIRLINE_COLORS = {
    "IGO": ("IndiGo", "#1d4ed8"),            # Blue
    "AIC": ("Air India", "#dc2626"),         # Red
    "AXB": ("Air India Express", "#ea580c"), # Orange
    "AKJ": ("Akasa Air", "#7e22ce"),         # Purple
    "SEJ": ("SpiceJet", "#eab308"),          # Gold/Yellow
    "UAE": ("Emirates", "#059669"),          # Green
    "QTR": ("Qatar Airways", "#881337"),     # Maroon
    "BAW": ("British Airways", "#0284c7"),   # Sky Blue
    "SIA": ("Singapore Airlines", "#d97706") # Amber
}
DEFAULT_AIRLINE = ("Other / Cargo / Private", "#475569")  # Slate Gray

def get_airline_info(callsign):
    prefix = callsign[:3].upper() if len(callsign) >= 3 else ""
    return AIRLINE_COLORS.get(prefix, DEFAULT_AIRLINE)

def get_live_aircraft(lat, lon, radius_nm=250):
    subdomain = "api"
    domain = "adsb.lol"
    version = "v2"
    endpoint = "point"
    
    url = f"https://{subdomain}.{domain}/{version}/{endpoint}/{lat}/{lon}/{radius_nm}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-ADS-B-Tracker/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        aircraft_list = []
        for ac in data.get("ac", []):
            if "lat" in ac and "lon" in ac:
                aircraft_list.append({
                    "icao24": ac.get("hex", "N/A"),
                    "callsign": ac.get("flight", "N/A").strip() or "N/A",
                    "aircraft_type": ac.get("t", "N/A"),
                    "latitude": ac["lat"],
                    "longitude": ac["lon"],
                    "altitude_ft": ac.get("alt_baro", "N/A"),
                    "speed_knots": ac.get("gs", "N/A"),
                    "heading": ac.get("track") or 0
                })
        return aircraft_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {e}")
        return []

def create_rotated_plane_icon(heading, color):
    html = f"""
    <div style="transform: rotate({heading}deg); width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;">
        <svg viewBox="0 0 24 24" width="26" height="26" fill="{color}" stroke="black" stroke-width="1">
            <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
        </svg>
    </div>
    """
    return folium.DivIcon(
        html=html,
        icon_size=(28, 28),
        icon_anchor=(14, 14)
    )

def plot_flights_on_map(flights, center_lat, center_lon):
    flight_map = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    # Draw the 463 km radar boundary circle around Shamshabad Airport
    folium.Circle(
        location=[center_lat, center_lon],
        radius=RADIUS_KM * 1000,
        color="#334155",
        weight=1.5,
        dash_array="6, 6",
        fill=False,
        tooltip=f"{RADIUS_KM} km Radar Range"
    ).add_to(flight_map)

    # Group flights by airline so each carrier gets its own toggleable filter layer
    grouped_flights = {}
    all_airlines = list(AIRLINE_COLORS.values()) + [DEFAULT_AIRLINE]
    for name, color in all_airlines:
        grouped_flights[name] = {"color": color, "planes": []}

    for plane in flights:
        airline_name, plane_color = get_airline_info(plane["callsign"])
        grouped_flights[airline_name]["planes"].append(plane)

    # Create a FeatureGroup layer for each airline with a color badge and live flight count
    for airline_name, info in grouped_flights.items():
        color = info["color"]
        planes = info["planes"]
        count = len(planes)

        layer_label = (
            f'<span style="display:inline-block; width:10px; height:10px; '
            f'background:{color}; border:1px solid #000; border-radius:50%; '
            f'margin-right:6px;"></span>{airline_name} ({count})'
        )
        feature_group = folium.FeatureGroup(name=layer_label, show=True)

        for plane in planes:
            callsign = plane["callsign"]
            heading = plane["heading"]

            popup_text = (
                f"<b>Airline:</b> {airline_name}<br>"
                f"<b>Callsign:</b> {callsign}<br>"
                f"<b>Type:</b> {plane['aircraft_type']}<br>"
                f"<b>Altitude:</b> {plane['altitude_ft']} ft<br>"
                f"<b>Speed:</b> {plane['speed_knots']} kts<br>"
                f"<b>Heading:</b> {heading}°"
            )

            folium.Marker(
                location=[plane["latitude"], plane["longitude"]],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"{airline_name} ({callsign}) | {plane['altitude_ft']} ft",
                icon=create_rotated_plane_icon(heading, color)
            ).add_to(feature_group)

        feature_group.add_to(flight_map)

    # Add the interactive filter panel (kept open by default with collapsed=False)
    folium.LayerControl(position="topright", collapsed=False).add_to(flight_map)

    #auto_refresh_tag = f'<meta http-equiv="refresh" content="{REFRESH_SECONDS}">'
    #flight_map.get_root().header.add_child(folium.Element(auto_refresh_tag))

    flight_map.save("live_flights_temp.html")
    os.replace("live_flights_temp.html", "live_flights.html")

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_local_server(port=8000):
    server = HTTPServer(("localhost", port), QuietHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=start_local_server, daemon=True).start()
    time.sleep(1)

    url = "http://localhost:8000/live_flights.html"
    browser_opened = False

    print(f"Starting live radar ({RADIUS_KM} km around Shamshabad). Press Ctrl+C to stop.\n")

    try:
        while True:
            flights = get_live_aircraft(HYD_LAT, HYD_LON, radius_nm=RADIUS_NM)
            plot_flights_on_map(flights, HYD_LAT, HYD_LON)
            print(f"[{time.strftime('%H:%M:%S')}] Updated map with {len(flights)} active aircraft.")

            if not browser_opened:
                webbrowser.open(url)
                browser_opened = True

            time.sleep(REFRESH_SECONDS)

    except KeyboardInterrupt:
        print("\nRadar stopped.")
