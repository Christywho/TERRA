from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import random
from model_loader import model_loader
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# The default URI points to local. If a cloud URI is provided, we must ensure it can connect securely.
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/terra_db')
app.config['MONGO_URI'] = mongo_uri

# Initialize PyMongo. Atlas requires TLS, which PyMongo usually infers from the +srv schema,
# but passing tlsAllowInvalidCertificates can help if Render's internal DNS acts up.
try:
    mongo = PyMongo(app, tlsAllowInvalidCertificates=True)
except Exception as e:
    print(f"PyMongo Initialization Error: {e}")
    mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- User Model ---
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None


# --- Mock Data Generators (Placeholders for Real APIs) ---

from gee_utils import get_weather_data, get_satellite_data
from soil_utils import get_soil_data

# NOTE: Soil Data is now fetched via SoilGrids API in soil_utils.py.

# --- Optimization Engine ---

def generate_recommendations(predicted_yield, target_yield, soil_data):
    recommendations = []
    
    if predicted_yield < target_yield:
        recommendations.append("Yield is below target. Consider the following interventions:")
        
        if soil_data['nitrogen'] < 100:
            deficit = 100 - soil_data['nitrogen']
            recommendations.append(f"- Apply Nitrogen fertilizer: ~{deficit:.1f} kg/ha deficit.")
        
        if soil_data['ph'] < 6.0:
            recommendations.append("- Soil is acidic. Consider lime application to raise pH.")
        elif soil_data['ph'] > 7.5:
            recommendations.append("- Soil is alkaline. Consider gypsum application.")
            
        recommendations.append("- Check irrigation schedule based on rainfall forecast.")
    else:
        recommendations.append("Yield is on track. Maintain current practices.")
        
    return recommendations

# --- Routes ---
import requests
import time

# Simple cache for News API to avoid quota exhaustion (200 reqs/day)
NEWS_CACHE = None
NEWS_CACHE_TIME = 0

@app.route('/api/latest-news')
def get_latest_news():
    global NEWS_CACHE, NEWS_CACHE_TIME
    
    # Refresh cache if older than 4 hours (14400 seconds)
    if not NEWS_CACHE or time.time() - NEWS_CACHE_TIME > 14400:
        api_key = "pub_e50e7284d6a348119638352e049f7fb8"
        url = f"https://newsdata.io/api/1/news?apikey={api_key}&country=in&language=en&category=food,environment&q=agriculture%20OR%20farming"
        
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get('status') == 'success' and 'results' in data:
                formatted_news = []
                for article in data['results'][:3]:  # Top 3 articles
                    desc = article.get('description', '')
                    if desc:
                        desc = (desc[:120] + '...') if len(desc) > 120 else desc
                    else:
                        desc = 'Read the full story to learn more about this latest update in the agricultural sector.'
                        
                    formatted_news.append({
                        'title': article.get('title', 'Agricultural Update'),
                        'description': desc,
                        'url': article.get('link', '#'),
                        'image': article.get('image_url') or 'https://images.unsplash.com/photo-1596733430284-cdff12cf7c14',
                        'category': article.get('category', ['Agriculture'])[0].title()
                    })
                
                # Update Cache
                NEWS_CACHE = formatted_news
                NEWS_CACHE_TIME = time.time()
                
        except Exception as e:
            print(f"Error fetching news: {e}")
            if NEWS_CACHE:
                pass # Use stale cache on error
            else:
                return jsonify({'error': 'Failed to fetch news'}), 500

    return jsonify({'news': NEWS_CACHE})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estimator')
@login_required 
def estimator_page():
    return render_template('estimator.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/recommendation')
@login_required
def recommendation_page():
    return render_template('recommendation.html')

@app.route('/crops')
def crop_info():
    return render_template('crops.html')

from datetime import datetime

@app.route('/forums')
def forums():
    # Fetch all threads, sort by newest first
    threads = list(mongo.db.threads.find().sort('created_at', -1))
    return render_template('forums.html', threads=threads)

@app.route('/forums/new', methods=['POST'])
@login_required
def new_thread():
    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')
    
    if title and category and content:
        mongo.db.threads.insert_one({
            'title': title,
            'category': category,
            'content': content,
            'author': current_user.username,
            'author_id': ObjectId(current_user.id),
            'created_at': datetime.utcnow()
        })
        flash('Thread created successfully!', 'success')
    else:
        flash('Please fill in all fields.', 'danger')
        
    return redirect(url_for('forums'))

@app.route('/forums/thread/<thread_id>')
def view_thread(thread_id):
    try:
        thread = mongo.db.threads.find_one({'_id': ObjectId(thread_id)})
        if not thread:
            flash('Thread not found.', 'danger')
            return redirect(url_for('forums'))
            
        # Fetch replies sorting by oldest first (chronological conversation)
        replies = list(mongo.db.replies.find({'thread_id': ObjectId(thread_id)}).sort('created_at', 1))
        
        return render_template('thread.html', thread=thread, replies=replies)
    except:
        flash('Invalid thread ID.', 'danger')
        return redirect(url_for('forums'))

@app.route('/forums/thread/<thread_id>/reply', methods=['POST'])
@login_required
def new_reply(thread_id):
    content = request.form.get('content')
    
    if content:
        mongo.db.replies.insert_one({
            'thread_id': ObjectId(thread_id),
            'content': content,
            'author': current_user.username,
            'author_id': ObjectId(current_user.id),
            'created_at': datetime.utcnow()
        })
        flash('Reply added successfully!', 'success')
    else:
        flash('Reply cannot be empty.', 'danger')
        
    return redirect(url_for('view_thread', thread_id=thread_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Check if user exists
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })
        flash('Account created! You can now login', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = mongo.db.users.find_one({'username': username})
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        crop_input = data.get('crop_type') 
        target_yield = float(data.get('target_yield', 5.0)) 

        # 1. Fetch Environmental Data (Now using GEE utilities)
        weather = get_weather_data(lat, lon)
        satellite = get_satellite_data(lat, lon)
        
        # Soil still mock for now as we don't have global soil API connected
        soil = get_soil_data(lat, lon)

        # 2. Prepare Features for Model
        crop_mapping = {
            'wheat': 'Wheat',
            'rice': 'Rice, paddy',
            'corn': 'Maize',
            'soybean': 'Soybeans',
            'potatoes': 'Potatoes',
            'sorghum': 'Sorghum',
            'cassava': 'Cassava',
            'sweet potatoes': 'Sweet potatoes',
            'yams': 'Yams',
            'plantains': 'Plantains and others'
        }
        
        model_crop_name = crop_mapping.get(crop_input.lower(), 'Wheat') 
        estimated_pesticides = 100.0 

        features_for_model = {
            'average_rain_fall_mm_per_year': weather['rainfall'],
            'avg_temp': weather['temp'],
            'pesticides_tonnes': estimated_pesticides,
            'crop_type': model_crop_name
        }

        # 3. Predict Yield
        prediction = model_loader.predict(features_for_model)

        # 4. Generate Recommendations
        recommendations = generate_recommendations(prediction, target_yield, soil)

        response = {
            'predicted_yield': round(prediction, 2),
            'unit': 'tons/ha',
            'environmental_data': {
                'weather': weather,
                'soil': soil,
                'satellite': satellite
            },
            'recommendations': recommendations
        }
        
        return jsonify(response)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        # User manual inputs + auto-fetched weather
        features = {
            'N': float(data.get('N')),
            'P': float(data.get('P')),
            'K': float(data.get('K')),
            'temperature': float(data.get('temperature')),
            'humidity': float(data.get('humidity')),
            'ph': float(data.get('ph')),
            'rainfall': float(data.get('rainfall'))
        }
        
        recommended_crop = model_loader.recommend_crop(features)
        
        return jsonify({'recommended_crop': recommended_crop})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint to fetch weather for recommendation page autofill
@app.route('/get_weather', methods=['POST'])
def get_weather():
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        weather = get_weather_data(lat, lon)
        # Weather dict now contains temp, rainfall, and humidity (fetched or mock)
        
        return jsonify(weather)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint to fetch soil data for recommendation page autofill
@app.route('/get_soil', methods=['POST'])
def get_soil():
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        soil = get_soil_data(lat, lon)
        return jsonify(soil)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
