import json
import requests
import os

from local_settings import API_KEY


BASE_URL = "https://api.litmos.com/v1.svc"
SUFFIX = "?source=MY-APP&format=json"


def get_data():
    user_url = BASE_URL + "/users" + SUFFIX
    user_courses_url = BASE_URL + "/users/courses" + SUFFIX
    header = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    user_request = requests.get(user_url, headers=header)
    user_response = user_request.json()
    print(user_response)

get_data()
