import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/terra_db')

try:
    print("Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client.get_default_database()
    
    print("Clearing old mock data...")
    db.threads.delete_many({"author": "TERRA_Expert"})
    db.replies.delete_many({"author": "TERRA_Expert"})

    expert_id = ObjectId()
    farmer_id = ObjectId()
    
    mock_threads = [
        {
            "title": "Best companion crops for Tomatoes in summer?",
            "category": "Crops",
            "content": "I'm planning my summer rotation and I have a large patch of tomatoes. What are the best companion crops to plant nearby to deter pests?",
            "author": "TERRA_Expert",
            "author_id": expert_id,
            "created_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "title": "Dealing with nitrogen deficiency in sandy soil",
            "category": "Soil",
            "content": "My recent soil test shows very low nitrogen. My soil is quite sandy and drains quickly. Does anyone have recommendations for organic amendments that won't wash away in the first heavy rain?",
            "author": "TERRA_Expert",
            "author_id": expert_id,
            "created_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "title": "Welcome to the TERRA Community Forums!",
            "category": "General",
            "content": "Welcome everyone! This is a space for farmers and agricultural enthusiasts to share knowledge, ask questions, and discuss the future of sustainable farming. Feel free to introduce yourselves below!",
            "author": "TERRA_Expert",
            "author_id": expert_id,
            "created_at": datetime.utcnow() - timedelta(days=10)
        }
    ]

    print("Inserting threads...")
    result = db.threads.insert_many(mock_threads)
    thread_ids = result.inserted_ids

    mock_replies = [
        {
            "thread_id": thread_ids[0],
            "content": "Basil and marigolds are classics! Basil helps repel tomato hornworms, and marigolds deter nematodes in the soil. Plus, they look great together.",
            "author": "TERRA_Expert",
            "author_id": farmer_id,
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "thread_id": thread_ids[1],
            "content": "I recommend using blood meal or planting a cover crop of clover. Clover fixes nitrogen from the air into the soil and acts as living mulch to prevent leaching.",
            "author": "TERRA_Expert",
            "author_id": farmer_id,
            "created_at": datetime.utcnow() - timedelta(days=3)
        }
    ]

    print("Inserting replies...")
    db.replies.insert_many(mock_replies)

    print(f"Successfully inserted {len(mock_threads)} threads and {len(mock_replies)} replies!")

except Exception as e:  
    print(f"Error seeding database: {e}")
