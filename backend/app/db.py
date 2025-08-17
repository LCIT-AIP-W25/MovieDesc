# backend/app/db.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Load Mongo URI from .env
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set in .env")

# Create MongoDB client
client = MongoClient(MONGO_URI)

# Use a specific database (you can name it anything)
db = client["echomind_db"]

# Collections
responses_collection = db["model_responses"]
users_collection = db["users"]
