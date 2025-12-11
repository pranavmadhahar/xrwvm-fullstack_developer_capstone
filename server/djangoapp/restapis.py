"""
REST API utilities for the dealership Django application.

Provides helper functions to create and manage API calls,
customizing connections between backend services and Django
endpoints. This module centralizes URL handling and request
logic to ensure consistent communication across the project.
"""

# Uncomment the imports below before you add the function code
import os
import traceback

import requests
from dotenv import load_dotenv

# load environ variables
load_dotenv()

backend_url = os.getenv("backend_url")
sentiment_analyzer_url = os.getenv("sentiment_analyzer_url")


# Add code for get requests to back end
def get_request(endpoint, **kwargs):
    """
    Send a GET request to the Node.js, mongodb backend service.

    This helper function receives a Django URL from views,
    merges it with the Node.js application endpoint, and
    performs a GET request using the `requests` library.

    Args:
        endpoint (str): The backend API endpoint to call.
        **kwargs: Optional query parameters to include in the request.

    Returns:
        requests.Response: The HTTP response object from the backend.
    """
    request_url = backend_url + endpoint
    print(f"GET from {request_url} with params {kwargs}")
    try:
        response = requests.get(
            request_url, params=kwargs if kwargs else None, timeout=20
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        return {"Status": 500, "message": "Backend error"}


# Add code for retrieving sentiments
def analyze_review_sentiments(text):
    """
    Send a GET request to the backend sentiment analysis microservice.

    This helper function receives reviews text from Django views,
    constructs the backend service URL, and performs an API call.
    Args:
        text(str): The review text to be analyzed.

    Returns:
        requests.Response: The HTTP response object containing
        the sentiment analysis results from the backend.
    """
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url, timeout=20)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        return {"Status": 500, "message": "Backend error"}


# Add code for posting review
def post_review(data_dict):
    """
    Send a POST request to the node.js and mongodb backend service

    This helper function receives reviews data as python dictionary
    from Django views, constructs the backend service URL,
    and performs an API call to insert the review in database.

    Args:
        data_dict(dict): The review data to be posted

    Returns:
        dict: The parsed JSON response from the backend service if successful,
        or an error dictionary with status and message,
        if a network exception occurs.
    """
    request_url = backend_url + "/insert_review"
    try:
        # requests lib has json=parameter that auto calls json.dumps(data_dict)
        response = requests.post(request_url, json=data_dict, timeout=20)
        print("Raw backend response :", response.status_code, response.text)
        backend_response = response.json()
        print(f"Backend response parsed : {backend_response}")
        return backend_response
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        traceback.print_exc()
        return {"Status": 500, "message": "Backend error"}
