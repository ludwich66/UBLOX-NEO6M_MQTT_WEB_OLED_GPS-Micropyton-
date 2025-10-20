"""
==============================================
GPS Weather Station UBLOX NEO-6M + ESP32
Version: 1 (Final Release) OLED OK
Date: 19-10-2025
Hardware: HELTEC ESP32 WiFi LoRa V2
GPS: UBLOX NEO-6M (Modul GY-NEO6MV2)
Display: OLED 1.3" 128x64 I2C SH1106
==============================================

FEATURES V1 (FINAL):
- GPS Tracking mit UBLOX NEO-6M (GPRMC + GPGGA)
- MQTT Publishing (QoS 1) mit Auto-Reconnect
- Async Web Server (Non-Blocking)
- Robust WiFi/MQTT Reconnection mit Hysterese
- OLED Display mit Screensaver
- Hemisphären-Anzeige (N/S, E/W)
- Home Assistant Integration

ANTI-RECONNECT-LOOP:
- Hysterese: 3 Fehler vor Reconnect
- Backoff: 60s nach fehlgeschlagenem Reconnect
- Smart Connection Management

WEB INTERFACE:
http://ESP32-IP/        → Dashboard
http://ESP32-IP/api     → JSON API
http://ESP32-IP/status  → System Status

==============================================
HOME ASSISTANT CONFIGURATION (configuration.yaml)
==============================================

# GPS Weather Station V1 - MQTT Integration
# Device: UBLOX_NEO6M_0001
# Topic: gps/data

mqtt:
  sensor:
    # ========================================
    # HAUPTSENSOR mit Attributen
    # ========================================
    - name: "GPS Tracker UBLOX"
      state_topic: "gps/data"
      value_template: "{{ value_json.device }}"
      json_attributes_topic: "gps/data"
      icon: "mdi:crosshairs-gps"
      unique_id: "gps_tracker_ublox_main"
    
    # ========================================
    # ZEIT & DATUM
    # ========================================
    - name: "GPS UTC Zeit"
      state_topic: "gps/data"
      value_template: "{{ value_json.time.utc }}"
      icon: "mdi:clock"
      unique_id: "gps_utc_time"
      
    - name: "GPS UTC Datum"
      state_topic: "gps/data" 
      value_template: "{{ value_json.time.date }}"
      icon: "mdi:calendar"
      unique_id: "gps_utc_date"
      
    - name: "GPS Wochentag"
      state_topic: "gps/data"
      value_template: "{{ value_json.time.weekday }}"
      icon: "mdi:calendar-week"
      unique_id: "gps_weekday"
    
    # ========================================
    # POSITION (mit Hemisphären)
    # ========================================
    - name: "GPS Latitude"
      state_topic: "gps/data"
      value_template: "{{ value_json.position.lat }}"
      unit_of_measurement: "°"
      icon: "mdi:latitude"
      unique_id: "gps_latitude"
      
    - name: "GPS Longitude"
      state_topic: "gps/data"
      value_template: "{{ value_json.position.lon }}"
      unit_of_measurement: "°"
      icon: "mdi:longitude"
      unique_id: "gps_longitude"
    
    - name: "GPS Höhe"
      state_topic: "gps/data"
      value_template: "{{ value_json.position.alt }}"
      unit_of_measurement: "m"
      icon: "mdi:altimeter"
      device_class: "distance"
      unique_id: "gps_altitude"
      
    - name: "GPS Hemisphäre Breitengrad"
      state_topic: "gps/data"
      value_template: "{{ value_json.position.lat_hemisphere }}"
      icon: "mdi:compass-rose"
      unique_id: "gps_lat_hemisphere"
      
    - name: "GPS Hemisphäre Längengrad"
      state_topic: "gps/data"
      value_template: "{{ value_json.position.lon_hemisphere }}"
      icon: "mdi:compass-rose"
      unique_id: "gps_lon_hemisphere"
    
    # ========================================
    # NAVIGATION
    # ========================================
    - name: "GPS Geschwindigkeit"
      state_topic: "gps/data"
      value_template: "{{ value_json.navigation.speed_kmh | round(1) }}"
      unit_of_measurement: "km/h"
      icon: "mdi:speedometer"
      device_class: "speed"
      unique_id: "gps_speed_kmh"
    
    - name: "GPS Kurs"
      state_topic: "gps/data"
      value_template: "{{ value_json.navigation.course | round(0) }}"
      unit_of_measurement: "°"
      icon: "mdi:compass"
      unique_id: "gps_course"
    
    # ========================================
    # STATUS & QUALITÄT
    # ========================================
    - name: "GPS Satelliten"
      state_topic: "gps/data"
      value_template: "{{ value_json.status.satellites }}"
      icon: "mdi:satellite-variant"
      unique_id: "gps_satellites"
    
    - name: "GPS HDOP"
      state_topic: "gps/data"
      value_template: "{{ value_json.status.hdop | round(2) }}"
      icon: "mdi:signal"
      unique_id: "gps_hdop"
    
    - name: "GPS Fix Quality"
      state_topic: "gps/data"
      value_template: >
        {% set quality = value_json.status.fix_quality | int %}
        {% if quality == 0 %}Kein Fix
        {% elif quality == 1 %}GPS Fix
        {% elif quality == 2 %}DGPS Fix
        {% else %}Unbekannt
        {% endif %}
      icon: "mdi:target"
      unique_id: "gps_fix_quality_text"
    
    # ========================================
    # SYSTEM MONITORING
    # ========================================
    - name: "GPS WiFi Reconnects"
      state_topic: "gps/data"
      value_template: "{{ value_json.system.wifi_reconnects | default(0) }}"
      icon: "mdi:wifi-refresh"
      unique_id: "gps_wifi_reconnects"
    
    - name: "GPS MQTT Reconnects"
      state_topic: "gps/data"
      value_template: "{{ value_json.system.mqtt_reconnects | default(0) }}"
      icon: "mdi:server-network"
      unique_id: "gps_mqtt_reconnects"

  # ========================================
  # BINARY SENSOREN
  # ========================================
  binary_sensor:
    - name: "GPS Signal Verfügbar"
      state_topic: "gps/data"
      value_template: "{{ value_json.status.valid }}"
      payload_on: true
      payload_off: false
      icon: "mdi:satellite-variant"
      device_class: "connectivity"
      unique_id: "gps_signal_available"

# ========================================
# DEVICE TRACKER für Karten-Anzeige
# ========================================
device_tracker:
  - platform: mqtt_json
    name: "GPS Tracker UBLOX"
    state_topic: "gps/data"
    json_attributes_topic: "gps/data"
    icon: "mdi:crosshairs-gps"

# ========================================
# TEMPLATE SENSOREN
# ========================================
template:
  - sensor:
      # Formatierte Position mit Hemisphären
      - name: "GPS Position Formatiert"
        state: >
          {% set lat = states('sensor.gps_latitude') | float %}
          {% set lon = states('sensor.gps_longitude') | float %}
          {% set lat_hem = states('sensor.gps_hemisphere_breitengrad') %}
          {% set lon_hem = states('sensor.gps_hemisphere_langengrad') %}
          {{ "%.6f"|format(lat|abs) }}{{ lat_hem }}, {{ "%.6f"|format(lon|abs) }}{{ lon_hem }}
        icon: "mdi:map-marker"
      
      # Reconnect-Rate pro Stunde
      - name: "GPS Reconnect Rate"
        state: >
          {% set wifi_r = states('sensor.gps_wifi_reconnects') | int %}
          {% set mqtt_r = states('sensor.gps_mqtt_reconnects') | int %}
          {% set total = wifi_r + mqtt_r %}
          {{ total }}
        unit_of_measurement: "reconnects"
        icon: "mdi:reload"

# ========================================
# AUTOMATIONEN
# ========================================
automation:
  # Warnung bei GPS-Signal-Verlust
  - alias: "GPS Signal Verloren"
    trigger:
      - platform: state
        entity_id: binary_sensor.gps_signal_verfugbar
        from: 'on'
        to: 'off'
        for: '00:05:00'
    action:
      - service: notify.mobile_app
        data:
          message: "GPS Signal seit 5 Minuten verloren!"
          title: "GPS Tracker Warnung"
  
  # Warnung bei hoher Reconnect-Rate
  - alias: "GPS Hohe Reconnect-Rate"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gps_reconnect_rate
        above: 50
    action:
      - service: notify.mobile_app
        data:
          message: "GPS Tracker hat {{ states('sensor.gps_reconnect_rate') }} Reconnects!"
          title: "GPS Verbindungsprobleme"

==============================================
"""

import machine
import time
import network
import json
import socket
import uasyncio as asyncio
from umqtt.simple import MQTTClient
from sh1106 import SH1106_I2C
from machine import UART, I2C, Pin
# #heltec
# VERSION = "1"
# DEVICE_ID = "0001"
# LED_PIN = 25
# BUTTON_PIN = 0
# SDA_PIN = 4
# SCL_PIN = 15
# UART_RX_PIN = 12
# UART_TX_PIN = 13

#esp32 wroom devkit1
VERSION = "1wroom"
DEVICE_ID = "0001"
LED_PIN = 2        # D2 esp32 wroom devkit1
BUTTON_PIN = 0     # D0 esp32 wroom devkit1 boot
SDA_PIN = 21       # D21 esp32 wroom devkit1 oled
SCL_PIN = 22       # D22 esp32 wroom devkit1 oled
UART_RX_PIN = 16   # D16 uart2
UART_TX_PIN = 17   # D17 uart2

SCREENSAVER_TIMEOUT = 123 #seconds
MQTT_QOS = 1
MQTT_KEEPALIVE = 60
WEB_SERVER_PORT = 80
WEB_SERVER_ENABLE = True

# Optimierte Reconnection
WIFI_CHECK_INTERVAL = 30000
MQTT_CHECK_INTERVAL = 30000
MQTT_PING_INTERVAL = 30000
CONNECTION_TIMEOUT = 20
WIFI_FAIL_THRESHOLD = 3
MQTT_FAIL_THRESHOLD = 3
RECONNECT_BACKOFF = 60000
MAX_RECONNECT_ATTEMPTS = 20

# OLED Lines
POS_LINE_0 = 0   # not used defect pixels
POS_LINE_1 = 10
POS_LINE_2 = 20
POS_LINE_3 = 30
POS_LINE_4 = 40
POS_LINE_5 = 50

SSID = "FritzBoxFonWLAN"
PASSWORD = "3373695987550335"
MQTT_SERVER = "192.168.178.35"
MQTT_CLIENT_ID = "ESP32_GPS_V" + str(VERSION)
MQTT_TOPIC = "gps/data"

class GPSWeatherStation:
    def __init__(self):
        self.led = Pin(LED_PIN, Pin.OUT)
        self.led.value(1)
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self.i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
        self.oled = SH1106_I2C(128, 64, self.i2c)
        self.uart = UART(1, baudrate=9600, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))
        
        self.gps_data = {
            'utc_time': '--:--:--', 'utc_date': '--/--/--', 'weekday': '--',
            'latitude': 0.0, 'longitude': 0.0, 'altitude': 0.0,
            'lat_hemisphere': '', 'lon_hemisphere': '',
            'speed_knots': 0.0, 'speed_kmh': 0.0, 'course': 0.0,
            'rmc_status': 'V', 'fix_quality': 0, 'satellites': 0, 'hdop': 0.0,
            'valid': False, 'has_rmc': False, 'has_gga': False
        }
        
        self.wifi_connected = False
        self.mqtt_connected = False
        self.mqtt_client = None
        self.last_wifi_check = 0
        self.last_mqtt_check = 0
        self.last_mqtt_ping = 0
        self.last_reconnect_attempt = 0
        
        self.wifi_consecutive_fails = 0
        self.mqtt_consecutive_fails = 0
        self.connection_failures = 0
        self.max_failures = MAX_RECONNECT_ATTEMPTS
        
        self.wifi_reconnects = 0
        self.mqtt_reconnects = 0
        self.last_success_time = time.ticks_ms()
        
        self.web_server = None
        self.web_server_running = False
        self.boot_time = time.ticks_ms()
        self.web_requests = 0
        self.mqtt_publishes = 0
        
        self.display_on = True
        self.last_user_activity = time.ticks_ms()
        self.button_pressed = False
        
        self.json_cache = None
        self.json_cache_time = 0
        
        self.init_display()
        print(f"GPS Weather Station V{VERSION} (Final Release)")

    def calculate_weekday(self, day, month, year):
        try:
            if month < 3: month += 12; year -= 1
            k = year % 100; j = year // 100
            h = (day + ((13 * (month + 1)) // 5) + k + (k // 4) + (j // 4) - 2 * j) % 7
            return ['Sa', 'So', 'Mo', 'Di', 'Mi', 'Do', 'Fr'][h]
        except: return '--'

    def parse_rmc_sentence(self, sentence):
        try:
            parts = sentence.split(',')
            if len(parts) < 12 or not parts[0].endswith('RMC'): return False
            if len(parts[1]) >= 6:
                self.gps_data['utc_time'] = f"{parts[1][:2]}:{parts[1][2:4]}:{parts[1][4:6]}"
            self.gps_data['rmc_status'] = parts[2] if parts[2] else 'V'
            if parts[3] and parts[4]:
                lat_raw = float(parts[3])
                latitude = int(lat_raw/100) + (lat_raw%100)/60
                self.gps_data['lat_hemisphere'] = parts[4]
                if parts[4] == 'S': latitude = -latitude
                self.gps_data['latitude'] = latitude
            if parts[5] and parts[6]:
                lon_raw = float(parts[5])
                longitude = int(lon_raw/100) + (lon_raw%100)/60
                self.gps_data['lon_hemisphere'] = parts[6]
                if parts[6] == 'W': longitude = -longitude
                self.gps_data['longitude'] = longitude
            if parts[7]:
                self.gps_data['speed_knots'] = float(parts[7])
                self.gps_data['speed_kmh'] = float(parts[7]) * 1.852
            if parts[8]: self.gps_data['course'] = float(parts[8])
            if len(parts[9]) >= 6:
                day, month, year = parts[9][:2], parts[9][2:4], "20" + parts[9][4:6]
                self.gps_data['utc_date'] = f"{day}/{month}/{year[-2:]}"
                try: self.gps_data['weekday'] = self.calculate_weekday(int(day), int(month), int(year))
                except: pass
            self.gps_data['has_rmc'] = True
            self.gps_data['valid'] = (parts[2] == 'A')
            self.json_cache = None
            return True
        except: return False

    def parse_gga_sentence(self, sentence):
        try:
            parts = sentence.split(',')
            if len(parts) < 15 or not parts[0].endswith('GGA'): return False
            self.gps_data['fix_quality'] = int(parts[6]) if parts[6] else 0
            self.gps_data['satellites'] = int(parts[7]) if parts[7] else 0
            if parts[8]: self.gps_data['hdop'] = float(parts[8])
            if parts[9]: self.gps_data['altitude'] = float(parts[9])
            self.gps_data['has_gga'] = True
            if not self.gps_data['has_rmc']:
                self.gps_data['valid'] = (self.gps_data['fix_quality'] > 0)
            self.json_cache = None
            return True
        except: return False

    def init_display(self):
        self.oled.fill(0)
        self.oled.text(f"GPS V{VERSION} FINAL", 0, POS_LINE_1, 1)
        self.oled.text(f"UBLOX NEO-6M", 0, POS_LINE_2, 1)
        self.oled.text(f"2025-10-19", 0, POS_LINE_3, 1)
        self.oled.text(f"Ready...", 0, POS_LINE_4, 1)
        
        self.oled.show()
        self.last_user_activity = time.ticks_ms()

    def update_display(self):
        if not self.display_on: return
        self.oled.fill(0)
        w = "W+" if self.wifi_connected else f"W{self.wifi_consecutive_fails}" # W = WLAN
        m = "M+" if self.mqtt_connected else f"M{self.mqtt_consecutive_fails}" # M = MQTT
        h = "WS+" if self.web_server_running else "WS-"                        # WS = WEBSERVER
        self.oled.text(f"{self.gps_data['utc_time']} {w}{m}{h}", 0, POS_LINE_1, 1)
        self.oled.text(f"{self.gps_data['utc_date']} {self.gps_data['weekday']} R:{self.wifi_reconnects+self.mqtt_reconnects}", 0, POS_LINE_2, 1)
        if self.gps_data['valid']:
            self.oled.text(f"SAT:{self.gps_data['satellites']} HDP:{self.gps_data['hdop']:.1f} ", 0, POS_LINE_3, 1)
            self.oled.text(f"LAT:{abs(self.gps_data['latitude']):.6f} {self.gps_data['lat_hemisphere']}", 0, POS_LINE_4, 1)
            self.oled.text(f"LON:{abs(self.gps_data['longitude']):.6f} {self.gps_data['lon_hemisphere']}", 0, POS_LINE_5, 1)
        else:
            self.oled.text("NO GPS FIX", 0, POS_LINE_3, 1)
        self.oled.show()

    def generate_html_page(self):
        """Kompakte HTML - V37e Final mit Altitude statt Speed"""
        current_time = time.ticks_ms()
        uptime_sec = (current_time - self.boot_time) // 1000
        uptime = f"{uptime_sec//3600:02d}:{(uptime_sec%3600)//60:02d}:{uptime_sec%60:02d}"
        fix = "GPS Fix" if self.gps_data['valid'] else "No Fix"
        total_r = self.wifi_reconnects + self.mqtt_reconnects
        rate = (total_r * 3600) / max(uptime_sec, 1) if uptime_sec > 0 else 0
        
        html = """<!DOCTYPE html><html><head><title>GPS V37e</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font:14px Arial;margin:10px;background:#f0f0f0}
.c{max-width:800px;margin:0 auto;background:white;padding:15px;border-radius:8px}
h1{text-align:center;color:#2c3e50;margin:10px 0}
.s{display:flex;flex-wrap:wrap;gap:8px;margin:15px 0}
.si{background:#ecf0f1;padding:8px;border-radius:5px;flex:1;min-width:120px;text-align:center}
.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin:15px 0}
.d{background:#e8f5e8;padding:10px;border-radius:5px;border-left:4px solid #27ae60}
.d2{background:#e3f2fd;border-left:4px solid #2196f3}
.d3{background:#fff3e0;border-left:4px solid #ff9800}
.d4{background:#fce4ec;border-left:4px solid #e91e63}
.l{font-weight:bold;color:#2c3e50;font-size:11px}
.v{font-size:13px;color:#27ae60;font-weight:bold}
.b{background:#3498db;color:white;border:none;padding:8px 15px;border-radius:5px;margin:5px}
</style>
<script>
function r(){fetch('/api').then(r=>r.json()).then(d=>{
document.getElementById('t').textContent=d.time.utc;
document.getElementById('lat').textContent=d.position.lat.toFixed(6)+' '+d.position.lat_hemisphere;
document.getElementById('lon').textContent=d.position.lon.toFixed(6)+' '+d.position.lon_hemisphere;
document.getElementById('alt').textContent=d.position.alt.toFixed(1)+' m';
document.getElementById('sat').textContent=d.status.satellites;
document.getElementById('wfail').textContent=d.system.wifi_consecutive_fails||0;
document.getElementById('mfail').textContent=d.system.mqtt_consecutive_fails||0;
})}
setInterval(r,5000);window.onload=r;
</script>
</head><body><div class="c">"""
        
        html += f"<h1>GPS Tracker V{VERSION}</h1>"
        html += f"<p style='text-align:center;color:#7f8c8d'>UBLOX NEO-6M {DEVICE_ID}</p>"
        
        html += "<div class='s'>"
        html += f"<div class='si'><div class='l'>Status:</div><div class='v'>{fix}</div></div>"
        html += f"<div class='si'><div class='l'>Uptime:</div><div class='v'>{uptime}</div></div>"
        html += f"<div class='si'><div class='l'>Reconnects:</div><div class='v'>{total_r}</div></div>"
        html += f"<div class='si'><div class='l'>Rate/h:</div><div class='v'>{rate:.1f}</div></div>"
        html += "</div>"
        
        html += "<div class='g'>"
        html += f"<div class='d'><div class='l'>UTC Zeit:</div><div class='v' id='t'>{self.gps_data['utc_time']}</div></div>"
        html += f"<div class='d d2'><div class='l'>Latitude:</div><div class='v' id='lat'>{abs(self.gps_data['latitude']):.6f} {self.gps_data['lat_hemisphere']}</div></div>"
        html += f"<div class='d d2'><div class='l'>Longitude:</div><div class='v' id='lon'>{abs(self.gps_data['longitude']):.6f} {self.gps_data['lon_hemisphere']}</div></div>"
        html += f"<div class='d d3'><div class='l'>Altitude:</div><div class='v' id='alt'>{self.gps_data['altitude']:.1f} m</div></div>"
        html += f"<div class='d d4'><div class='l'>Satelliten:</div><div class='v' id='sat'>{self.gps_data['satellites']}</div></div>"
        html += f"<div class='d d4'><div class='l'>WiFi Fails:</div><div class='v' id='wfail'>{self.wifi_consecutive_fails}</div></div>"
        html += f"<div class='d d4'><div class='l'>MQTT Fails:</div><div class='v' id='mfail'>{self.mqtt_consecutive_fails}</div></div>"
        html += "</div>"
        
        html += "<div style='text-align:center;margin:15px 0'>"
        html += "<button class='b' onclick='r()'>Refresh</button>"
        html += "<br><small>Auto 5s | <a href='/api'>JSON API</a></small></div>"
        html += "</div></body></html>"
        
        return html

    def create_json_payload(self):
        current_time = time.ticks_ms()
        if self.json_cache and time.ticks_diff(current_time, self.json_cache_time) < 500:
            return self.json_cache
        payload = {
            "device": f"UBLOX_NEO6M_{DEVICE_ID}",
            "time": {"utc": self.gps_data['utc_time'], "date": self.gps_data['utc_date'], "weekday": self.gps_data['weekday']},
            "position": {"lat": self.gps_data['latitude'], "lat_hemisphere": self.gps_data['lat_hemisphere'], 
                        "lon": self.gps_data['longitude'], "lon_hemisphere": self.gps_data['lon_hemisphere'], 
                        "alt": self.gps_data['altitude']},
            "navigation": {"speed_kmh": self.gps_data['speed_kmh'], "course": self.gps_data['course']},
            "status": {"rmc_status": self.gps_data['rmc_status'], "fix_quality": self.gps_data['fix_quality'], 
                      "satellites": self.gps_data['satellites'], "hdop": self.gps_data['hdop'], "valid": self.gps_data['valid']},
            "system": {"version": VERSION, "uptime_ms": time.ticks_diff(current_time, self.boot_time), 
                      "web_requests": self.web_requests, "wifi_reconnects": self.wifi_reconnects,
                      "mqtt_reconnects": self.mqtt_reconnects, "wifi_consecutive_fails": self.wifi_consecutive_fails,
                      "mqtt_consecutive_fails": self.mqtt_consecutive_fails}
        }
        self.json_cache = json.dumps(payload)
        self.json_cache_time = current_time
        return self.json_cache

    async def handle_web_request(self, client_socket, addr):
        try:
            request_data = b""
            client_socket.settimeout(3)
            while True:
                try:
                    chunk = client_socket.recv(256)
                    if not chunk: break
                    request_data += chunk
                    if b'\r\n\r\n' in request_data: break
                except: break
            if not request_data: return
            request_str = request_data.decode('utf-8')
            lines = request_str.split('\n')
            if not lines: return
            method, path, protocol = lines[0].split(' ')
            self.web_requests += 1
            if path in ['/', '/index.html']:
                content = self.generate_html_page()
                content_type = 'text/html'
            elif path == '/api':
                content = self.create_json_payload()
                content_type = 'application/json'
            else:
                content = '{"error":"Not Found"}'
                content_type = 'application/json'
            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
            client_socket.send(response_header.encode())
            for i in range(0, len(content), 512):
                client_socket.send(content[i:i+512].encode())
                await asyncio.sleep_ms(5)
        except: pass
        finally:
            try: client_socket.close()
            except: pass

    async def web_server_task(self):
        if not WEB_SERVER_ENABLE: return
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', WEB_SERVER_PORT))
            server_socket.listen(2)
            server_socket.setblocking(False)
            self.web_server = server_socket
            self.web_server_running = True
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                print(f"Web Server: http://{wlan.ifconfig()[0]}")
            while True:
                try:
                    client_socket, addr = server_socket.accept()
                    asyncio.create_task(self.handle_web_request(client_socket, addr))
                except OSError:
                    await asyncio.sleep_ms(100)
        except: self.web_server_running = False

    def check_screensaver(self):
        current_time = time.ticks_ms()
        if self.display_on and time.ticks_diff(current_time, self.last_user_activity) > SCREENSAVER_TIMEOUT * 1000:
            self.display_on = False
            self.oled.fill(0); self.oled.show()
        if not self.button.value() and not self.button_pressed:
            self.button_pressed = True
            if not self.display_on:
                self.display_on = True
                self.last_user_activity = time.ticks_ms()
                self.update_display()
            time.sleep(0.3)
        elif self.button.value(): self.button_pressed = False

    def check_wifi_connection(self):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_wifi_check) < WIFI_CHECK_INTERVAL:
            return
        self.last_wifi_check = current_time
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            self.wifi_consecutive_fails += 1
            if self.wifi_consecutive_fails >= WIFI_FAIL_THRESHOLD:
                if time.ticks_diff(current_time, self.last_reconnect_attempt) < RECONNECT_BACKOFF:
                    return
                self.wifi_connected = False
                self.mqtt_connected = False
                if self.mqtt_client:
                    try: self.mqtt_client.disconnect()
                    except: pass
                    self.mqtt_client = None
                self.last_reconnect_attempt = current_time
                if self.connect_wifi():
                    self.wifi_reconnects += 1
                    self.wifi_consecutive_fails = 0
                    print(f"WiFi reconnected (#{self.wifi_reconnects})")
                else:
                    self.connection_failures += 1
        else:
            self.wifi_consecutive_fails = 0
            if not self.wifi_connected:
                self.wifi_connected = True
                self.led.value(0)

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if wlan.isconnected(): self.wifi_connected = True; return True
        wlan.connect(SSID, PASSWORD)
        timeout = CONNECTION_TIMEOUT
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1); timeout -= 1
        if wlan.isconnected(): self.wifi_connected = True; self.led.value(0); return True
        else: self.wifi_connected = False; return False

    def check_mqtt_connection(self):
        if not self.wifi_connected: return
        current_time = time.ticks_ms()
        if (self.mqtt_connected and time.ticks_diff(current_time, self.last_mqtt_ping) > MQTT_PING_INTERVAL):
            if self.mqtt_ping():
                self.last_mqtt_ping = current_time
                self.mqtt_consecutive_fails = 0
            else:
                self.mqtt_consecutive_fails += 1
                if self.mqtt_consecutive_fails >= MQTT_FAIL_THRESHOLD:
                    self.mqtt_connected = False
        if (not self.mqtt_connected and time.ticks_diff(current_time, self.last_mqtt_check) > MQTT_CHECK_INTERVAL):
            self.last_mqtt_check = current_time
            if time.ticks_diff(current_time, self.last_reconnect_attempt) < RECONNECT_BACKOFF:
                return
            self.last_reconnect_attempt = current_time
            if self.setup_mqtt():
                self.mqtt_reconnects += 1
                self.mqtt_consecutive_fails = 0
                print(f"MQTT reconnected (#{self.mqtt_reconnects})")
            else:
                self.connection_failures += 1

    def mqtt_ping(self):
        try: 
            if self.mqtt_client: self.mqtt_client.ping(); return True
        except: return False

    def setup_mqtt(self):
        if not self.wifi_connected: return False
        try:
            if self.mqtt_client: 
                try: self.mqtt_client.disconnect()
                except: pass
                self.mqtt_client = None
            self.mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=MQTT_KEEPALIVE)
            self.mqtt_client.connect()
            self.mqtt_connected = True
            self.last_mqtt_ping = time.ticks_ms()
            return True
        except:
            self.mqtt_connected = False
            self.mqtt_client = None
            return False

    def publish_gps_data(self):
        if not self.mqtt_connected: return False
        try:
            self.mqtt_client.publish(MQTT_TOPIC, self.create_json_payload(), qos=MQTT_QOS)
            self.mqtt_publishes += 1
            return True
        except:
            self.mqtt_connected = False
            return False

    def process_uart_data(self):
        if not self.uart.any(): return False
        try:
            raw_data = self.uart.readline()
            if not raw_data: return False
            line = raw_data.decode('ascii').strip()
            if 'RMC' in line: return self.parse_rmc_sentence(line)
            elif 'GGA' in line: return self.parse_gga_sentence(line)
        except: pass
        return False

    def handle_critical_failures(self):
        if self.connection_failures >= self.max_failures:
            print("CRITICAL: Reset")
            machine.reset()

    async def main_loop(self):
        last_display_update = 0
        last_mqtt_publish = 0
        print(f"=== GPS Weather Station V{VERSION} Running ===")
        while True:
            try:
                current_time = time.ticks_ms()
                self.handle_critical_failures()
                self.check_wifi_connection()
                self.check_mqtt_connection()
                self.process_uart_data()
                self.check_screensaver()
                if self.display_on and time.ticks_diff(current_time, last_display_update) > 500:
                    self.update_display()
                    last_display_update = current_time
                interval = 15000 if self.gps_data['valid'] else 45000
                if time.ticks_diff(current_time, last_mqtt_publish) > interval:
                    self.publish_gps_data()
                    last_mqtt_publish = current_time
                await asyncio.sleep_ms(100)
            except Exception as e:
                print(f"Main error: {e}")
                self.connection_failures += 1
                await asyncio.sleep_ms(2000)

    def run(self):
        print(f"GPS Weather Station V{VERSION} (Final Release)")
        print(f"Device ID: {DEVICE_ID}")
        print(f"Anti-Loop Reconnection Active")
        if self.connect_wifi():
            self.setup_mqtt()
        async def run_all():
            await asyncio.gather(self.web_server_task(), self.main_loop())
        try:
            asyncio.run(run_all())
        except KeyboardInterrupt:
            print("Stopped by user")

if __name__ == "__main__":
    try:
        GPSWeatherStation().run()
    except Exception as e:
        print(f"Error: {e}")
        machine.reset()