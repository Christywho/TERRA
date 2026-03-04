from soil_utils import get_soil_data
import sys

# Test coordinates (Bangalore roughly)
lat = 12.97
lon = 77.59

print(f"Testing get_soil_data for Lat: {lat}, Lon: {lon}")

try:
    soildata = get_soil_data(lat, lon)
    print("Soil Data retrieved:", soildata)
    
    if 'ph' in soildata and 'nitrogen' in soildata:
        print("SUCCESS: 'ph' and 'nitrogen' fields are present.")
        print(f"Values - pH: {soildata['ph']}, Nitrogen: {soildata['nitrogen']}")
    else:
        print("FAIL: Missing keys.")
        sys.exit(1)

except Exception as e:
    print(f"FAIL: Function raised exception: {e}")
    sys.exit(1)
