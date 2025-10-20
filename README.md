Use a GPS module in a weather station. The data is provided via MQTT JSON string, as an HTTP website, and directly on an OLED display.

**Hardware:**
* UBLOX NEO6M GPS (Modul GY-NEO6MV2) (UART)
* OLED DISPLAY 1.3" (I2C, 6LINES, SH1106)
* ESP32 WROOM-32 Devkit1
* ESP32 Button to Switch OLED on/off (Start=OLED on, Screensaver: on-time set in code {123sec.}, alive with Button)

**Mircopython-Code MP_1.6.1 (Assist w. Perplexity)**

see py code

**HomeAssistent Integration for MQTT Code**

see py code

**OLED Display** (i use only 5 lines, 1 line defect)

<img src="https://github.com/ludwich66/UBLOX-NEO6M_MQTT_WEB_OLED_GPS-Micropyton-/blob/main/IMG_0196.jpeg" alt="Logo" width="200" height="150"><img src="https://github.com/ludwich66/UBLOX-NEO6M_MQTT_WEB_OLED_GPS-Micropyton-/blob/main/IMG_0194.jpeg" alt="Logo" width="200" height="150">

W+ W- = WLAN

M+ M- = MQTT

WS+ WS- = Website

R = ReconnectCounter

Date & Time in UTC


**WebSite**

<img src="https://github.com/ludwich66/UBLOX-NEO6M_MQTT_WEB_OLED_GPS-Micropyton-/blob/main/GPS_Web.jpg" alt="Logo" width="400" height="300">

