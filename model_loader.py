import joblib
import os
import pandas as pd
import numpy as np

class ModelLoader:
    _instance = None
    _model = None
    _model_columns = None
    _recommender = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        try:
            # Yield Model
            model_path = os.path.join('models', 'rf_yield_model.joblib')
            self._model = joblib.load(model_path)
            
            columns_path = os.path.join('models', 'model_columns.joblib')
            self._model_columns = joblib.load(columns_path)
            
            # Recommendation Model
            rec_path = os.path.join('models', 'recommender_model.joblib')
            self._recommender = joblib.load(rec_path)
            
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Error loading models: {e}")
            # Ensure we don't crash if one fails, but log it
            if self._model is None: self._model = None
            if self._recommender is None: self._recommender = None

    def predict(self, features):
        """
        Predicts yield based on input features.
        """
        if self._model is None or self._model_columns is None:
            self._load_model()
            if self._model is None:
                raise ValueError("Yield Model not loaded.")
        
        df = pd.DataFrame(columns=self._model_columns)
        df.loc[0] = 0 
        
        df.at[0, 'average_rain_fall_mm_per_year'] = features.get('average_rain_fall_mm_per_year', 0)
        df.at[0, 'avg_temp'] = features.get('avg_temp', 0)
        df.at[0, 'pesticides_tonnes'] = features.get('pesticides_tonnes', 0)
        
        crop = features.get('crop_type')
        if crop:
            col_name = f"Item_{crop}"
            if col_name in df.columns:
                df.at[0, col_name] = 1
        
        df = df[self._model_columns]
        prediction = self._model.predict(df)
        return prediction[0]

    def recommend_crop(self, features):
        """
        Predicts best crop based on Soil/Weather.
        features: dict with keys [N, P, K, temperature, humidity, ph, rainfall]
        """
        if self._recommender is None:
            self._load_model()
            if self._recommender is None:
                raise ValueError("Recommender Model not loaded.")
                
        # Feature order matches training: N, P, K, temperature, humidity, ph, rainfall
        data = [[
            features.get('N'),
            features.get('P'),
            features.get('K'),
            features.get('temperature'),
            features.get('humidity'),
            features.get('ph'),
            features.get('rainfall')
        ]]
        
        prediction = self._recommender.predict(data)
        return prediction[0]

# Global instance
model_loader = ModelLoader()
