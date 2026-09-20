"""
MongoDB client initialization.

Reads connection details from environment variables so the app can point
to MongoDB Atlas (or any other MongoDB instance) via the .env file,
instead of a hardcoded localhost URL.
"""

import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("MONGODB_DB_NAME", "intelliquery")

if not MONGO_URL:
    raise ValueError(
        "MONGODB_URL is not set. Add your MongoDB Atlas connection string "
        "to the .env file, e.g.:\n"
        "MONGODB_URL=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority"
    )

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]