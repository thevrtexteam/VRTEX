# ==============================
# VRTEX BOT - LAYER 1 (CORE)
# ==============================

# -------- IMPORTS --------
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import os
import motor.motor_asyncio
from datetime import datetime


# -------- CONFIG --------
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

BOT_NAME = "VRTEX"
BOT_VERSION = "1.0"


# -------- DATABASE --------
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.vrtex

users_collection = db.users
servers_collection = db.servers


# -------- USER SETUP --------
async def setup_user(user_id: int):
    user = await users_collection.find_one({"user_id": user_id})

    if not user:
        await users_collection.insert_one({
            "user_id": user_id,
            "balance": 0,
            "bank": 0,
            "job": None,
            "job_level": 1,
            "work_streak": 0,
            "last_work": None,
            "inventory": [],
            "created_at": datetime.utcnow()
        })


# -------- SERVER SETUP --------
async def setup_server(guild_id: int):
    server = await servers_collection.find_one({"guild_id": guild_id})

    if not server:
        await servers_collection.insert_one({
            "guild_id": guild_id,
            "prefix": "!",
            "vrt_ex_plus": False,
            "created_at": datetime.utcnow()
        })

# ==============================
# VRTEX BOT – LAYER 2 (DATA FETCHING & CACHE)
# ==============================
# -------- IN-MEMORY CACHE --------
cached_users = {}
cached_servers = {}


# -------- FETCH ALL USERS --------
async def fetch_all_users():
    """
    Fetch all users from MongoDB and store them in memory.
    This ensures user data is restored after every redeploy.
    """
    cached_users.clear()

    cursor = users_collection.find({})
    async for user in cursor:
        cached_users[user["user_id"]] = user

    print(f"[CACHE] Loaded {len(cached_users)} users")


# -------- FETCH ALL SERVERS --------
async def fetch_all_servers():
    """
    Fetch all servers from MongoDB and store them in memory.
    """
    cached_servers.clear()

    cursor = servers_collection.find({})
    async for server in cursor:
        cached_servers[server["guild_id"]] = server

    print(f"[CACHE] Loaded {len(cached_servers)} servers")


# -------- FETCH EVERYTHING --------
async def fetch_all_data():
    """
    Fetch all bot-related data into memory.
    Called once when the bot starts.
    """
    await fetch_all_users()
    await fetch_all_servers()
    print("[CACHE] All data successfully loaded")


# -------- GET USER (FROM CACHE) --------
async def get_user(user_id: int):
    """
    Return user data from cache.
    If user doesn't exist, create and cache them.
    """
    if user_id not in cached_users:
        new_user = {
            "user_id": user_id,
            "balance": 0,
            "bank": 0,
            "job": None,
            "job_level": 1,
            "work_streak": 0,
            "last_work": None,
            "inventory": [],
            "created_at": datetime.utcnow()
        }

        await users_collection.insert_one(new_user)
        cached_users[user_id] = new_user

    return cached_users[user_id]


# -------- GET SERVER (FROM CACHE) --------
async def get_server(guild_id: int):
    """
    Return server data from cache.
    If server doesn't exist, create and cache it.
    """
    if guild_id not in cached_servers:
        new_server = {
            "guild_id": guild_id,
            "prefix": "!",
            "vrt_ex_plus": False,
            "setup_completed": False,
            "created_at": datetime.utcnow()
        }

        await servers_collection.insert_one(new_server)
        cached_servers[guild_id] = new_server

    return cached_servers[guild_id]
