import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, mean_absolute_percentage_error, accuracy_score, r2_score
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

def plot_confusion_matrix():
    print("Generating Confusion Matrix for Recommender Model...")
    df = pd.read_csv(os.path.join('Datasets', 'Crop_recommendation.csv'))
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model_path = os.path.join('models', 'recommender_model.joblib')
    model = joblib.load(model_path)
    
    y_pred = model.predict(X_test)
    
    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    plt.figure(figsize=(16, 14))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title('Classification Performance (Confusion Matrix) - Crop Recommendation')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300)
    plt.close()
    print("Saved confusion_matrix.png")

def plot_yield_comparison():
    print("Generating Actual vs Predicted Yield Line Graph...")
    df = pd.read_csv(os.path.join('Datasets', 'yield_df.csv'))
    
    df['Yield_tons_per_ha'] = df['hg/ha_yield'] * 0.0001
    
    X = df[['average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes', 'Item']]
    y = df['Yield_tons_per_ha']
    
    X = pd.get_dummies(X, columns=['Item'], prefix='Item')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model_path = os.path.join('models', 'rf_yield_model.joblib')
    model = joblib.load(model_path)
    
    y_pred = model.predict(X_test)
    
    mape = mean_absolute_percentage_error(y_test, y_pred)
    print(f"Yield Model MAPE: {mape:.2%}")
    
    results = pd.DataFrame({'Actual': y_test.values, 'Predicted': y_pred})
    results = results.sort_values(by='Actual').reset_index(drop=True)
    
    if len(results) > 200:
        indices = np.linspace(0, len(results)-1, 200).astype(int)
        results = results.iloc[indices].reset_index(drop=True)

    plt.figure(figsize=(14, 7))
    plt.plot(results.index, results['Actual'], label='Actual Yield', color='blue', linewidth=2)
    plt.plot(results.index, results['Predicted'], label='Predicted Yield', color='red', linestyle='--', alpha=0.7)
    plt.title(f'Actual vs. Predicted Yield (MAPE: {mape:.2%})')
    plt.xlabel('Sample Index (Sorted by Actual Yield)')
    plt.ylabel('Yield (tons/ha)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('yield_comparison.png', dpi=300)
    plt.close()
    print("Saved yield_comparison.png")

def plot_classification_comparison():
    print("Generating Classification Model Comparison...")
    df = pd.read_csv(os.path.join('Datasets', 'Crop_recommendation.csv'))
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Random Forest
    rf_model = joblib.load(os.path.join('models', 'recommender_model.joblib'))
    rf_acc = accuracy_score(y_test, rf_model.predict(X_test))
    
    # SVM
    print("Training SVM for classification...")
    svm_model = SVC(random_state=42)
    svm_model.fit(X_train_scaled, y_train)
    svm_acc = accuracy_score(y_test, svm_model.predict(X_test_scaled))
    
    # Logistic Regression (Simple Linear Model for Classification)
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(random_state=42, max_iter=2000)
    lr_model.fit(X_train_scaled, y_train)
    lr_acc = accuracy_score(y_test, lr_model.predict(X_test_scaled))
    
    models = ['Random Forest', 'SVM', 'Logistic Regression']
    accuracies = [rf_acc, svm_acc, lr_acc]
    
    plt.figure(figsize=(10, 6))
    bars = sns.barplot(x=models, y=accuracies, palette='viridis', hue=models, legend=False)
    plt.title('Classification Accuracy Comparison: Crop Recommendation')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1.1)
    
    for i, acc in enumerate(accuracies):
        plt.text(i, acc + 0.02, f'{acc:.2%}', ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('class_model_comparison.png', dpi=300)
    plt.close()
    print("Saved class_model_comparison.png")

def plot_regression_comparison():
    print("Generating Regression Model Comparison...")
    df = pd.read_csv(os.path.join('Datasets', 'yield_df.csv'))
    df['Yield_tons_per_ha'] = df['hg/ha_yield'] * 0.0001
    
    X = df[['average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes', 'Item']]
    y = df['Yield_tons_per_ha']
    X = pd.get_dummies(X, columns=['Item'], prefix='Item')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Random Forest
    rf_model = joblib.load(os.path.join('models', 'rf_yield_model.joblib'))
    rf_r2 = r2_score(y_test, rf_model.predict(X_test))
    
    # SVM - Subsample for training to speed up since yield_df can be large and SVR is O(n^2)
    print("Training SVR for regression...")
    if len(X_train_scaled) > 5000:
        # Subsample indices
        np.random.seed(42)
        idx = np.random.choice(len(X_train_scaled), 5000, replace=False)
        svm_model = SVR()
        svm_model.fit(X_train_scaled[idx], y_train.iloc[idx])
    else:
        svm_model = SVR()
        svm_model.fit(X_train_scaled, y_train)
        
    svm_r2 = r2_score(y_test, svm_model.predict(X_test_scaled))
    
    # Linear Regression
    print("Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    lr_r2 = r2_score(y_test, lr_model.predict(X_test_scaled))
    
    models = ['Random Forest', 'SVM (SVR)', 'Linear Regression']
    r2_scores = [rf_r2, svm_r2, lr_r2]
    
    plt.figure(figsize=(10, 6))
    bars = sns.barplot(x=models, y=r2_scores, palette='magma', hue=models, legend=False)
    plt.title('Regression R² Comparison: Yield Prediction')
    plt.ylabel('R² Score')
    plt.ylim(0, max(r2_scores) + 0.15)
    
    for i, r2 in enumerate(r2_scores):
        plt.text(i, r2 + 0.02, f'{r2:.3f}', ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('reg_model_comparison.png', dpi=300)
    plt.close()
    print("Saved reg_model_comparison.png")

if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')
    
    plot_confusion_matrix()
    plot_yield_comparison()
    plot_classification_comparison()  # New
    plot_regression_comparison()      # New
