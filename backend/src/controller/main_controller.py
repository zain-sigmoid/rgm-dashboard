"""
This module defines the primary application controller for the FastAPI backend.
It is responsible for initializing the FastAPI application instance, registering
API routers, configuring middleware (e.g., CORS), and setting up global event
handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Setup Successfull"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Docschat FastAPI server running!"}
