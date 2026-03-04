import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_and_save_model():
    """Trains the model using real dataset and saves it along with feature columns."""
    print("Loading dataset...")
    # Load the specific dataset that has the merged info
    df = pd.read_csv(os.path.join('Datasets', 'yield_df.csv'))
    
    # --- Preprocessing ---
    # 1. Drop unused columns (like Area if we aren't using it for general model, Year is usually not a feature for future prediction unless time-series)
    # Keeping it simple as per plan: Area is too high cardinality for now without heavy encoding, Year is not good for general future prediction in this simple model.
    
    # 2. Convert Yield from hg/ha to tons/ha
    # 1 hg/ha = 0.0001 tons/ha
    df['Yield_tons_per_ha'] = df['hg/ha_yield'] * 0.0001
    
    # 3. Features Selection
    # X features: 'average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes', 'Item' (Crop)
    # y target: 'Yield_tons_per_ha'
    
    X = df[['average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes', 'Item']]
    y = df['Yield_tons_per_ha']
    
    # 4. One-Hot Encoding for Categorical Variables (Item/Crop)
    X = pd.get_dummies(X, columns=['Item'], prefix='Item')
    
    # Save the column names to ensure the prediction input has the exact same columns
    model_columns = list(X.columns)
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Model R^2: {score:.2f}")
    print(f"Model RMSE: {rmse:.2f} tons/ha")
    
    # Saving
    os.makedirs('models', exist_ok=True)
    
    model_path = os.path.join('models', 'rf_yield_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    columns_path = os.path.join('models', 'model_columns.joblib')
    joblib.dump(model_columns, columns_path)
    print(f"Model columns saved to {columns_path}")

if __name__ == "__main__":
    train_and_save_model()
