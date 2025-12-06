# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

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
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Check user credentials
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""} # return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    try:
        # get data from the request
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email']
    # if there is problem in the json
    except(json.JSONDecodeError, KeyError):
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
            email=email
        )
        login(request, user)
        # log this is as new user
        logger.debug(f"{username} is new user")
        data = {"username": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        if username_exist:
            data = {"username": username, "error": "Username Already Registered"}
            return JsonResponse(data)
        elif email_exist:
            data = {"email": email, "error": "Email Already Registered"}
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "Invalid Details"}, status=400)

        
def get_cars(request):

    count=CarMake.objects.filter().count()
    print(count)
    if count == 0:
        # run fn to bulk upload data from populate.py
        initiate()
    
    # using select_related to reference both CarModel and CarMake class
    car_models = CarModel.objects.select_related('car_make')

    cars = []

    for car_model in car_models:

        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    
    return JsonResponse({"CarModels": cars})

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create view to render the dealer details
def get_dealer_details(request, dealer_id):

    if dealer_id:
        endpoint = f"/fetchDealers/{str(dealer_id)}"
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Get dealership reviews 
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            # call sentiment analyzer microservice
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            # add new key:value pair in reviews dict 
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})


# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
