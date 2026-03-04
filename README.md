# 🌍 TERRA (Terra Efficiency, Revenue, and Resource Analytics)

TERRA is an AI-powered platform designed to transform multispectral satellite data and environmental insights into precise crop yield forecasts and recommendations. By optimizing resource usage such as water and fertilizers, TERRA bridges the gap between environmental sustainability and farm profitability through advanced predictive modeling.

## 🚀 Features

*   **🌱 Crop Yield Estimation**: Predicts crop yields accurately using machine learning models based on environmental inputs (rainfall, temperature, pesticide usage, and crop type).
*   **🌾 Crop Recommendation System**: Recommends the most suitable crops for specific soil and weather conditions (N, P, K, pH, temperature, humidity, rainfall).
*   **🛰️ Real-Time Environmental Data**: Integrates **Google Earth Engine (GEE)** to fetch live weather (temperature, humidity, rainfall) and multispectral satellite data.
*   **🌍 Soil Insights**: Utilizes the SoilGrids API to gather location-based soil characteristics.
*   **📰 Live Agriculture News Feed**: Keeps farmers and users updated with the latest in food, environment, and agriculture using NewsData.io.
*   **💬 Community Forums**: A dedicated space for users to create threads, ask questions, and share farming practices.
*   **🔐 User Authentication**: Secure user registration and login system.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **Database**: MongoDB (flask-pymongo)
*   **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib
*   **Authentication**: Flask-Login, Flask-Bcrypt
*   **External APIs**:
    *   Google Earth Engine (GEE) API
    *   NewsData.io API
    *   SoilGrids API

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/TERRA.git
    cd TERRA
    ```

2.  **Set Up a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install Required Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up MongoDB**
    Ensure you have MongoDB installed and running locally on the default port (`localhost:27017`), or update the `MONGO_URI` in `app.py` to point to your MongoDB Atlas cluster.

5.  **Configure API Keys**
    *   **Google Earth Engine**: Place your GEE service account credentials in a file named `gee_credentials.json` in the root directory.
    *   **NewsData.io**: Update the `api_key` variable in `app.py` under the `/api/latest-news` route if you wish to use your own.

6.  **Run the Application**
    ```bash
    python app.py
    ```

7.  **Access the Dashboard**
    Open your browser and navigate to `http://localhost:5000`

## 📂 Project Structure

*   `app.py`: Main Flask application handling routing, authentication, and API integrations.
*   `model_loader.py`: Handles loading and serving predictions from the trained machine learning models.
*   `train_model.py` / `train_recommender.py`: Scripts for training the ML models.
*   `gee_utils.py`: Utilities for interacting with the Google Earth Engine API.
*   `soil_utils.py`: Utilities for fetching data from the SoilGrids API.
*   `models/`: Directory containing serialized `.pkl` machine learning models.
*   `templates/`: HTML files for the application frontend.
*   `static/`: CSS styling, JavaScript files, and images.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
