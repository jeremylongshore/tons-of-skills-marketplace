#!/usr/bin/env python3
"""
Template for a basic WebSocket server using Socket.IO.

This script provides a foundation for building real-time bidirectional
communication applications. It includes error handling, example usage,
and follows PEP 8 style guidelines.
"""

import os
import logging
import re
import socketio
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_CONTROL_CHARS = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def sanitize_for_log(value):
    """
    Strips CR/LF/control characters from a user-controlled value before it is
    written to the log, preventing log-injection / forged log entries.

    Args:
        value: Any value destined for a log message.

    Returns:
        str: A single-line, control-character-free representation of value.
    """
    # Remove CR/LF with str.replace first (the pattern CodeQL recognizes as
    # a log-injection sanitizer), then strip the remaining control chars.
    text = str(value).replace("\r", "").replace("\n", "")
    return _CONTROL_CHARS.sub("", text)


# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")

# Create AIOHTTP application
app = web.Application()

# Bind Socket.IO to the application
sio.attach(app)


# Define event handlers
@sio.event
async def connect(sid, environ):
    """
    Handles a new client connection.

    Args:
        sid (str): Session ID of the client.
        environ (dict): Environment variables.
    """
    logging.info(f"Client connected: {sid}")
    try:
        await sio.emit("my_response", {"data": "Connected", "count": 0}, room=sid)
    except Exception as e:
        logging.error(f"Error emitting connect message: {e}")


@sio.event
async def disconnect(sid):
    """
    Handles a client disconnection.

    Args:
        sid (str): Session ID of the client.
    """
    logging.info(f"Client disconnected: {sid}")


@sio.event
async def my_message(sid, message):
    """
    Handles a custom message event.

    Args:
        sid (str): Session ID of the client.
        message (str): The received message.
    """
    logging.info(f"Received message from {sanitize_for_log(sid)}: {sanitize_for_log(message)}")
    try:
        await sio.emit("my_response", {"data": message}, room=sid)
    except Exception as e:
        logging.error(f"Error emitting my_response: {e}")


@sio.event
async def my_broadcast_event(sid, message):
    """
    Handles a broadcast event.

    Args:
        sid (str): Session ID of the client.
        message (str): The message to broadcast.
    """
    logging.info(f"Received broadcast request from {sanitize_for_log(sid)}: {sanitize_for_log(message)}")
    try:
        await sio.emit("my_response", {"data": message})  # Broadcast to all clients
    except Exception as e:
        logging.error(f"Error emitting broadcast message: {e}")


@sio.event
async def join_room(sid, room):
    """
    Handles a request to join a room.

    Args:
        sid (str): Session ID of the client.
        room (str): The room to join.
    """
    logging.info(f"Client {sanitize_for_log(sid)} joining room {sanitize_for_log(room)}")
    try:
        sio.enter_room(sid, room)
        await sio.emit("my_response", {"data": "Entered room: " + room}, room=sid)
    except Exception as e:
        logging.error(f"Error joining room: {e}")


@sio.event
async def leave_room(sid, room):
    """
    Handles a request to leave a room.

    Args:
        sid (str): Session ID of the client.
        room (str): The room to leave.
    """
    logging.info(f"Client {sanitize_for_log(sid)} leaving room {sanitize_for_log(room)}")
    try:
        sio.leave_room(sid, room)
        await sio.emit("my_response", {"data": "Left room: " + room}, room=sid)
    except Exception as e:
        logging.error(f"Error leaving room: {e}")


async def index(request):
    """
    Serves the index.html file.

    Args:
        request (aiohttp.web.Request): The request object.

    Returns:
        aiohttp.web.Response: The response object containing the HTML content.
    """
    try:
        with open("index.html") as f:
            return web.Response(content_type="text/html", text=f.read())
    except FileNotFoundError:
        return web.Response(status=404, text="index.html not found")
    except Exception:
        logging.exception("Error serving index.html")
        return web.Response(status=500, text="Internal Server Error")


if __name__ == "__main__":
    """
    Main entry point of the application.
    """
    try:
        # Serve static files (e.g., index.html)
        app.router.add_get("/", index)
        app.router.add_static("/static", "./static")  # Assuming a 'static' directory

        # Start the web server
        port = int(os.environ.get("PORT", 5000))  # Default port 5000 or from environment
        logging.info(f"Starting server on port {port}")
        web.run_app(app, port=port)

    except Exception as e:
        logging.error(f"Failed to start the server: {e}")
