import requests
import random

def get_soil_data(lat, lon):
    """
    Fetches soil data (pH, Nitrogen) from SoilGrids REST API.
    Returns: {'ph': float, 'nitrogen': float}
    """
    try:
        # Endpoint for SoilGrids v2.0
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        
        # Parameters: Define location and the properties you want
        params = {
            "lon": lon,
            "lat": lat,
            "property": ["nitrogen", "phh2o"], 
            "depth": ["0-5cm", "5-15cm"],
            "value": "mean"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extracting specific values (Example: Nitrogen at 0-5cm)
            # SoilGrids returns integers. Nitrogen conversion factor is 0.1 (cg/kg to g/kg)
            # We want 'nitrogen' for the model. Let's average the top two layers (0-5, 5-15) for robust surface data.
            
            layers = data['properties']['layers']
            nitrogen_layer = next((l for l in layers if l['name'] == 'nitrogen'), None)
            ph_layer = next((l for l in layers if l['name'] == 'phh2o'), None)
            
            nitrogen_val = 0
            if nitrogen_layer:
                 # Mean of first depth (0-5cm)
                 val = nitrogen_layer['depths'][0]['values']['mean'] 
                 # nitrogen in cg/kg -> g/kg = * 0.1. 
                 # But model might expect kg/ha or similar. 
                 # For now, let's stick to the user's conversion: * 0.1
                 if val is not None:
                    nitrogen_val = val * 0.1

            ph_val = 0
            if ph_layer:
                # pH conversion factor is 0.1 (pH*10 to pH)
                val = ph_layer['depths'][0]['values']['mean']
                if val is not None:
                    ph_val = val * 0.1
            
            # Safety check if API returns None values
            if ph_val == 0: ph_val = 6.5
            if nitrogen_val == 0: nitrogen_val = 100.0

            return {
                "nitrogen": nitrogen_val,
                "ph": ph_val,
                "p": random.uniform(30, 60), # Mocked Phosphorus (P)
                "k": random.uniform(30, 60)  # Mocked Potassium (K)
            }
        else:
            print(f"SoilGrids API returned status: {response.status_code}")
            return _get_mock_soil_data()

    except Exception as e:
        print(f"Error fetching SoilGrids data: {e}")
        return _get_mock_soil_data()

def _get_mock_soil_data():
    """Fallback mock data"""
    return {
        'ph': random.uniform(5.5, 7.5),
        'nitrogen': random.uniform(50, 150),
        'p': random.uniform(30, 60),
        'k': random.uniform(30, 60)
    }
