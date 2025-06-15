import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simple Backend API",
    description="A simple FastAPI backend deployed on ECS",
    version="1.0.0",
)

# Add CORS middleware to allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server (if using Vite)
        # Add your frontend domain here when deployed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Hello from FastAPI on ECS!",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/users")
async def get_users():
    # Mock users data
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Lubhna", "email": "lubhna@example.com"},  # Fixed name
        ]
    }


@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    # Mock user data
    if user_id in [1, 2, 3]:
        users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
            3: {"id": 3, "name": "Lubhna", "email": "lubhna@example.com"},  # Fixed name
        }
        return users[user_id]
    return {"error": "User not found"}
