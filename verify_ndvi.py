from gee_utils import get_satellite_data
import sys

# Test coordinates (Agricultural area)
lat = 20.0
lon = 78.0

print(f"Testing get_satellite_data for Lat: {lat}, Lon: {lon}")

try:
    data = get_satellite_data(lat, lon)
    print("Satellite Data retrieved:", data)
    
    if 'ndvi' in data:
        print("SUCCESS: 'ndvi' field is present.")
        val = data['ndvi']
        if isinstance(val, (int, float)):
             print(f"NDVI Value: {val}")
        else:
             print(f"FAIL: Value is not a number: {type(val)}")
             sys.exit(1)
    else:
        print("FAIL: 'ndvi' field is MISSING.")
        sys.exit(1)

except Exception as e:
    print(f"FAIL: Function raised exception: {e}")
    sys.exit(1)
