# Uncomment the imports below before you add the function code
import requests
import os
import traceback

from dotenv import load_dotenv

# load environ variables
load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# Add code for get requests to back end
# def get_request(endpoint, **kwargs):
#     params = ""
#     if(kwargs):
#         for key,value in kwargs.items():
#             params=params+key+"="+value+"&"

#     request_url = backend_url+endpoint+"?"+params

#     print("GET from {} ".format(request_url))
#     try:
#         # Call get method of requests library with URL and parameters
#         response = requests.get(request_url)
#         return response.json()
#     except:
#         # If any error occurs
#         print("Network exception occurred")

def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint
    print(f"GET from {request_url} with params {kwargs}")
    try:
        response = requests.get(request_url, params=kwargs if kwargs else None)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        return None



# Add code for retrieving sentiments

def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")

# Add code for posting review
def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        # requests lib has json=parameter that auto calls json.dumps(data_dict)
        response = requests.post(request_url,json=data_dict)
        print("Raw backend response :", response.status_code, response.text)
        backend_response = response.json()
        print(f"Backend response parsed : {backend_response}")
        return backend_response
    except Exception as e:
        print("Network exception occurred: ", e)
        traceback.print_exc()
        return {"status": 500, "message": "Backend error"}
