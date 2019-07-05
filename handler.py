import asyncio
import requests
import time
import os

from local_settings import *

BASE_URL = "https://api.litmos.com/v1.svc"
SUFFIX = "?source=MY-APP&format=json"

saleforce_oauth2 = "https://test.salesforce.com/services/oauth2/token"
saleforce_post_api = "https://saicservice--smiluat.cs74.my.salesforce.com/services/apexrest/SyncCourse"

# category
SAIC = "SAIC_Motor"
MG = "MG"
RC = "Resources_Center"


async def get_course_data(url, email, headers, info_list):
    info = {
        "email": email
    }
    SAIC_completed = 0
    SAIC_total = 0
    MG_completed = 0
    MG_total = 0
    RC_completed = 0
    RC_total = 0
    try:
        courses_request = requests.get(url, headers=headers)
        if courses_request.status_code != 200:
            # log
            pass
        else:
            courses_list = courses_request.json()
            for course in courses_list:
                if course['Name'].startswith(SAIC):
                    SAIC_total += 1
                    if course['Complete']:
                        SAIC_completed += 1
                elif course['Name'].startswith(MG):
                    MG_total += 1
                    if course['Complete']:
                        MG_completed += 1
                elif course['Name'].startswith(RC):
                    RC_total += 1
                    if course['Complete']:
                        RC_completed += 1
                else:
                    pass
        info[SAIC + '_completed'] = SAIC_completed
        info[SAIC + '_total'] = SAIC_total

        info[MG + '_completed'] = MG_completed
        info[MG + '_total'] = MG_total

        info[RC + '_completed'] = RC_completed
        info[RC + '_total'] = RC_total

        info_list.append(info)
    except Exception as e:
        # log
        pass


async def get_data():
    user_url = BASE_URL + "/users" + SUFFIX
    user_courses_url = BASE_URL + "/users/{user_id}/courses" + SUFFIX
    header = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    finished = False
    result = {}
    users_retry = 0
    while not finished:
        info_list = []
        try:
            users_request = requests.get(user_url, headers=header)
            if users_request.status_code != 200:
                if users_retry > 4:
                    # log
                    break
                else:
                    users_retry += 1
                    # log
                    continue
            users_response = users_request.json()
        except Exception as e:
            # log
            break

        tasks = [asyncio.create_task(get_course_data(
            user_courses_url.format(user_id=user_data['Id']),
            user_data['Email'],
            headers=header,
            info_list=info_list
        )) for user_data in users_response]
        for task in tasks:
            await task
        result = {'info_list': info_list}
        finished = True

    return result


def send_data(data):
    token_query = "{token_url}?grant_type={grant_type}&client_id={client_id}&" \
                  "client_secret={client_secret}&username={username}&password={password}".format(
        token_url=saleforce_oauth2,
        grant_type=grant_type,
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password
    )

    token_request = requests.post(token_query)
    token_response = token_request.json()
    access_token = token_response['access_token']

    post_header = {
        "access_token": access_token,
        "Content-Type": "application/json"
    }

    post_request = requests.post(saleforce_post_api, data=data, headers=post_header)
    print(post_request.status_code)


data = asyncio.run(get_data())
send_data(data)
