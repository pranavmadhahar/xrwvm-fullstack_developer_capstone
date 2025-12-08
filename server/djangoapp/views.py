"""
Views functions for manging the Django application.

This module defines the functions that are mapped to URL patterns,
and execute the logic when those routes are accessed.
"""

# Uncomment the required imports before adding the code
from django.contrib.auth.models import User
from django.contrib.auth import logout

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_request`
@csrf_exempt
def login_user(request):
    """
    Handles user login request.

    This function receives user's login credentials from the request.body,
    authenticate the user and process the request.

    Args:
        request(HTTPRequest): The HTTP request object containing
        user's username and password in request.body

    Returns:
        JsonResponse:  A JSON response as a dictionary indicating
        login result(success or failure)
    """
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    # Check user credentials
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"Message": "Invalid crenditials"}
        return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    """
    Handles user logout request.

    This function processes user's logout request.
    Clear's the user's session, and returns a JSON response indicating
    that the user has been logged out.

    Args:
        request(HTTPRequest):
        The HTTP request object containing the logout request.

    Returns:
        JsonResponse:
        A JSON response with a dictionary containing an empty user object
        to confirm logout.
    """
    logout(request)
    data = {"userName": ""}  # return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    """
    Handles new user registeration request.

    This function receives user's credentials from the request.body,
    checks whether the username already exists in the database,
    and if not, creates a new user by saving details in the database.

    Args:
        request(HTTPRequest):
        The HTTP request object containing
        user's username, password, first name, last name and email
        in request.body

    Returns:
        JsonResponse:
        A JSON response as a dictionary indicating
        registration result.
    """
    try:
        # get data from the request
        data = json.loads(request.body)
        username = data["userName"]
        password = data["password"]
        first_name = data["firstName"]
        last_name = data["lastName"]
        email = data["email"]
    # if there is problem in the json
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid Request"}, status=400)

    # Check if user already exists
    username_exist = User.objects.filter(username=username).exists()
    email_exist = User.objects.filter(email=email).exists()

    # if it is a new user
    if not username_exist and not email_exist:
        # create user in auth_user table
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        # log this is as new user
        logger.debug(f"{username} is new user")
        data = {"username": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        if username_exist:
            data = {
                "username": username,
                "error": "Username Already Registered"
            }
            return JsonResponse(data)
        elif email_exist:
            data = {"email": email, "error": "Email Already Registered"}
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "Invalid Details"}, status=400)


def get_cars(request):
    """
    Handle request to retrieve car data

    This view function checks the database for available cars,
    if no records exists, it uploads car make and car model data
    using a helper function.
    Finally it returns total cars with car make and car model details.

    Args:
        request(HTTPRequest):
        The HTTP request object for retrieving car data.

    Returns:
        JsonResponse:
        A JSON response as a dictionary containing,
        car make and car model details.
    """
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        # run fn to bulk upload data from populate.py
        initiate()
    # using select_related to reference both CarModel and CarMake class
    car_models = CarModel.objects.select_related("car_make")

    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
            })
    return JsonResponse({"CarModels": cars})


# Update the `get_dealerships` render list of dealerships all by default,
def get_dealerships(request, state="All"):
    """
    Handle request to retrieve dealerships data with optional state filter.

    This view function receives a user request for dealership information,
    sends an API request to the node.js mongodb backened service,
    using a helper function, and returns a list of dealerships.
    If state is provided, the results are filtered accordingly.

    Args:
        request(HTTPRequest):
        The HTTP request object for retrieving dealership data.
        state(str, optional):
        The state name to filter dealerships. Defaults to all.

    Returns:
        JsonResponse:  A JSON response containing dealership details.
    """
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Create view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{str(dealer_id)}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Get dealership reviews
def get_dealer_reviews(request, dealer_id):
    """
    Handle requests to retrieve dealerships reviews.

    This view function receives a user request for dealership reviews,
    sends an API request to the node.js mongodb backend service,
    using a helper function, and returns a list of reviews.
    It also calls the sentiment analysis microservice,
    to enrich each review with its corresponding sentiment.

    Args:
        request(HTTPRequest):
        The HTTP request object for retrieving dealership reviews data.
        dealer_id:
        The unique identifier of the dealership to filter reviews.

    Returns:
        JsonResponse:
        A JSON response containing dealership reviews with sentiments.
    """
    # if dealer id has been provided
    if dealer_id:
        endpoint_reviews = f"/fetchReviews/dealer/{str(dealer_id)}"
        endpoint_dealer = f"/fetchDealer/{str(dealer_id)}"

        reviews = get_request(endpoint_reviews)
        dealer_response = get_request(endpoint_dealer)
        # dealer_response will return a list which contain dict
        dealer_details = dealer_response[0]

        for review_detail in reviews:
            # call sentiment analyzer microservice
            response = analyze_review_sentiments(review_detail["review"])
            print(f"Reviews:  {reviews}")
            # add new key:value pair in reviews dict
            review_detail["sentiment"] = response["sentiment"]
            review_detail["city"] = dealer_details["city"]
            review_detail["address"] = dealer_details["address"]
            review_detail["zip"] = dealer_details["zip"]
            review_detail["state"] = dealer_details["state"]
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
def add_review(request):
    """
    Handle requests to add dealerships reviews.

    This view function receives a user request(request.body),
    containing dealership review data. It checks for user authentication,
    then sends an API call to the node.js mongodb backend service
    using a helper function.
    Finally it returns a JSON response with the backend result.

    Args:
        request(HTTPRequest):
        The HTTP request object containing user review data.
    Returns:
        JsonResponse:
        A JSON response indicating success or failure of review submission.
    """
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            print(f"Backend response: {response}")
            return JsonResponse(response)
        except Exception as e:
            print("Error posting review ", e)
            return JsonResponse({"status": 500, "message": "Backend error"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
