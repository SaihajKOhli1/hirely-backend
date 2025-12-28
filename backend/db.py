"""
MongoDB connection using Motor (async MongoDB driver).
"""
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "hirely")

# Global client instance
client: AsyncIOMotorClient = None


async def get_db():
    """
    Get MongoDB database instance.
    
    Returns:
        Database: MongoDB database instance
    """
    global client
    if client is None:
        # Use certifi for SSL certificate verification
        client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    return client[DB_NAME]


async def close_connection():
    """
    Close MongoDB connection.
    """
    global client
    if client:
        client.close()
        client = None
