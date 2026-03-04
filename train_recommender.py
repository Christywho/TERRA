import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def train_and_save_recommender():
    """Trains the crop recommendation model and saves it."""
    print("Loading dataset...")
    df = pd.read_csv(os.path.join('Datasets', 'Crop_recommendation.csv'))
    
    # Features: N, P, K, temperature, humidity, ph, rainfall
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label'] # Target: Crop Name
    
    print(f"Dataset shape: {df.shape}")
    print(f"Unique crops: {y.nunique()}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.4f}")
    # print(classification_report(y_test, y_pred)) # Optional: detailed report
    
    # Saving
    os.makedirs('models', exist_ok=True)
    model_path = os.path.join('models', 'recommender_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_recommender()
