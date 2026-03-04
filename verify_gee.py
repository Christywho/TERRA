from gee_utils import get_weather_data
import sys

# Test coordinates (Random location)
lat = 20.0
lon = 78.0

print(f"Testing get_weather_data for Lat: {lat}, Lon: {lon}")

try:
    weather = get_weather_data(lat, lon)
    print("Weather retrieved:", weather)
    
    if 'humidity' in weather:
        print("SUCCESS: 'humidity' field is present.")
        hum = weather['humidity']
        if isinstance(hum, (int, float)):
             print(f"Value is valid number: {hum}")
        else:
             print(f"FAIL: Value is not a number: {type(hum)}")
             sys.exit(1)
    else:
        print("FAIL: 'humidity' field is MISSING.")
        sys.exit(1)

except Exception as e:
    print(f"FAIL: Function raised exception: {e}")
    sys.exit(1)
