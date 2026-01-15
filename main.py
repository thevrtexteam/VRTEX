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

# -------------------- DATA FETCH SYSTEM --------------------

cached_users = {}
cached_servers = {}

async def fetch_all_users():
    global cached_users
    users = await users_collection.find().to_list(length=None)
    
    for user in users:
        cached_users[user["user_id"]] = user

    print(f"[DATA] Loaded {len(cached_users)} users")


async def fetch_all_servers():
    global cached_servers
    servers = await servers_collection.find().to_list(length=None)
    
    for server in servers:
        cached_servers[server["guild_id"]] = server

    print(f"[DATA] Loaded {len(cached_servers)} servers")


async def fetch_all_data():
    await fetch_all_users()
    await fetch_all_servers()
