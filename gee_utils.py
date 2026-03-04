try:
    import ee
except ImportError:
    ee = None
import os
import random
import datetime

# Flag to track if GEE is initialized
GEE_INITIALIZED = False

try:
    # Try to load credentials
    credentials_path = os.path.join(os.getcwd(), 'gee_credentials.json')
    if ee is not None and os.path.exists(credentials_path):
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/earthengine'])
        ee.Initialize(scoped_credentials)
        GEE_INITIALIZED = True
        print("Google Earth Engine initialized successfully.")
    else:
        if ee is None:
            print("Earth Engine API not installed. Using mock data.")
        else:
            print("GEE Credentials not found. Using mock data.")
except Exception as e:
    print(f"Error initializing GEE: {e}.")
    print("Using mock data.")
    GEE_INITIALIZED = False

def get_weather_data(lat, lon):
    """
    Fetches real weather data from GEE if available, else returns mock data.
    Returns: {'temp': float (C), 'rainfall': float (mm)}
    """
    if GEE_INITIALIZED:
        try:
            # Using ERA5 for Temperature (latest available)
            # ERA5 Daily Aggregates - taking mean of last 30 days for "Average Temp" roughly
            # Note: ERA5 has a lag. We'll try to get data from a month ago.
            
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=30)
            
            # ERA5 - 'mean_2m_air_temperature' is in Kelvin
            # We also need 'dewpoint_temperature_2m' to calculate Relative Humidity
            dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")\
                        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))\
                        .select(['temperature_2m', 'dewpoint_temperature_2m'])\
                        .mean()
            
            # Reduce region to get value at point
            point = ee.Geometry.Point([lon, lat])
            
            weather_dict = dataset.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=10000
            ).getInfo()
            
            temp_k = weather_dict.get('temperature_2m')
            dewpoint_k = weather_dict.get('dewpoint_temperature_2m')
            
            # Helper to calculate RH from Temp and Dewpoint (August-Roche-Magnus approximation)
            humidity_val = 50.0 # Default fallback
            if temp_k is not None and dewpoint_k is not None:
                temp_c = temp_k - 273.15
                dew_c = dewpoint_k - 273.15
                # Formula: 100 * (exp((17.625 * Td)/(243.04 + Td)) / exp((17.625 * T)/(243.04 + T)))
                import math
                def saturation_vapor_pressure(t):
                    return 6.1094 * math.exp((17.625 * t) / (243.04 + t))
                
                es = saturation_vapor_pressure(temp_c)
                actual_vapor_pressure = saturation_vapor_pressure(dew_c)
                humidity_val = 100 * (actual_vapor_pressure / es)

            
            # CHIRPS for Rainfall (Pentad) - Sum of last year to get "Average Annual Rainfall" approximation
            # Or just fetch long term climatic average if we want "Average Rainfall" feature
            # Let's take last 365 days sum
            
            rain_start = end_date - datetime.timedelta(days=365)
            rain_dataset = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")\
                            .filterDate(rain_start.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))\
                            .select('precipitation')\
                            .sum()
                            
            rain_dict = rain_dataset.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=5000
            ).getInfo()
            
            rainfall_mm = rain_dict.get('precipitation')
            
            if temp_k is not None and rainfall_mm is not None:
                return {
                    'temp': temp_k - 273.15, # Kelvin to Celsius
                    'rainfall': rainfall_mm,
                    'humidity': humidity_val
                }
            
        except Exception as e:
            print(f"Error fetching GEE Weather data: {e}. Falling back to mock.")
            
    # Fallback / Mock
    return {
        'temp': random.uniform(20, 35),
        'rainfall': random.uniform(500, 1500),
        'humidity': random.uniform(40, 90)
    }

def get_satellite_data(lat, lon):
    """
    Fetches NDVI from Sentinel-2 if GEE available.
    Returns: {'ndvi': float}
    """
    if GEE_INITIALIZED:
        try:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=90) # Last 3 months to find a cloud-free image
            
            # Sentinel-2 Surface Reflectance
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
                  .filterBounds(ee.Geometry.Point([lon, lat]))\
                  .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))\
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))\
                  .sort('CLOUDY_PIXEL_PERCENTAGE')\
                  .first()
            
            if s2:
                # Calculate NDVI: (NIR - Red) / (NIR + Red)
                # Band 8 is NIR, Band 4 is Red
                ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
                
                point = ee.Geometry.Point([lon, lat])
                ndvi_val = ndvi.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=point,
                    scale=10
                ).getInfo().get('NDVI')
                
                if ndvi_val is not None:
                    return {'ndvi': ndvi_val}
                    
        except Exception as e:
            print(f"Error fetching GEE Satellite data: {e}. Falling back to mock.")

    # Fallback
    return {
        'ndvi': random.uniform(0.3, 0.8)
    }
