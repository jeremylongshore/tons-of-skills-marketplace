#!/usr/bin/env python3
"""
Template for generating FastAPI API endpoints.

This module provides a basic structure for creating FastAPI applications,
including error handling, dependency injection, and endpoint definitions.
"""

import logging
import re
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_CONTROL_CHARS = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def sanitize_for_log(value) -> str:
    """
    Strips CR/LF/control characters from a request-controlled value before it
    is written to the log, preventing log-injection / forged log entries.

    Args:
        value: Any value destined for a log message.

    Returns:
        str: A single-line, control-character-free representation of value.
    """
    # Remove CR/LF with str.replace first (the pattern CodeQL recognizes as
    # a log-injection sanitizer), then strip the remaining control chars.
    text = str(value).replace("\r", "").replace("\n", "")
    return _CONTROL_CHARS.sub("", text)


app = FastAPI(
    title="FastAPI API Template",
    description="A template for building FastAPI applications.",
    version="0.1.0",
)


class RequestModel(BaseModel):
    """
    Example request model using Pydantic for data validation.
    """

    item_id: int
    item_name: str
    item_description: str = None
    item_price: float


class ResponseModel(BaseModel):
    """
    Example response model for API endpoints.
    """

    message: str
    data: Dict[str, Any] = {}


async def get_db():
    """
    Simulates a database dependency.  In a real application,
    this would connect to a database and yield a database session.
    """
    try:
        # Simulate database connection
        logging.info("Connecting to database...")
        db = {"items": []}  # Placeholder for database
        yield db
    finally:
        # Simulate database disconnection
        logging.info("Disconnecting from database...")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler for HTTPExceptions.
    """
    logging.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """
    Custom exception handler for Pydantic ValidationErrors.
    """
    logging.error(f"ValidationError: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Validation Error", "errors": exc.errors()},
    )


@app.get("/", response_model=ResponseModel)
async def read_root():
    """
    Root endpoint.
    """
    logging.info("Root endpoint accessed.")
    return ResponseModel(message="Welcome to the FastAPI API Template!")


@app.post("/items/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_item(item: RequestModel, db: dict = Depends(get_db)):
    """
    Endpoint to create a new item.
    """
    try:
        logging.info(f"Creating item: {sanitize_for_log(item)}")
        db["items"].append(item.dict())
        return ResponseModel(message="Item created successfully", data=item.dict())
    except Exception as e:
        logging.error(f"Error creating item: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/items/{item_id}", response_model=ResponseModel)
async def read_item(item_id: int, db: dict = Depends(get_db)):
    """
    Endpoint to read an item by its ID.
    """
    try:
        logging.info(f"Reading item with ID: {sanitize_for_log(item_id)}")
        item = next((item for item in db["items"] if item["item_id"] == item_id), None)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return ResponseModel(message="Item retrieved successfully", data=item)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error reading item: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    """
    Example usage of the FastAPI application.

    To run this example:
    1. Save this file as `main.py`.
    2. Install FastAPI and Uvicorn: `pip install fastapi uvicorn`
    3. Run the application: `uvicorn main:app --reload`

    Then, you can access the API endpoints in your browser or using a tool like curl or Postman.
    """
    import uvicorn

    logging.info("Running FastAPI application in example mode...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
