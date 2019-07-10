import asyncio
import requests
import time

from aiohttp import ClientSession
from local_settings import *

BASE_URL = "https://api.litmos.com/v1.svc"
SUFFIX = "?source=MY-APP&format=json"

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
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    # log
                    pass
                else:
                    courses_list = await response.json()
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
    time.sleep(0.6)


async def get_data():
    user_url = BASE_URL + "/users" + SUFFIX + "&start={}&limit=100"
    user_courses_url = BASE_URL + "/users/{user_id}/courses" + SUFFIX
    header = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    finished = False
    result = {}
    users_retry = 0
    info_list = []
    offset = 0
    while not finished:
        try:
            users_request = requests.get(user_url.format(offset), headers=header)
            if users_request.status_code != 200:
                if users_retry > 4:
                    # log
                    break
                else:
                    users_retry += 1
                    print("retry to fetch user list ..")
                    continue
            users_response = users_request.json()
        except Exception as e:
            print(e)
            break

        tasks = [asyncio.create_task(get_course_data(
            user_courses_url.format(user_id=user_data['Id']),
            user_data['UserName'],
            headers=header,
            info_list=info_list
        )) for user_data in users_response if user_data['Brand'] == "CRM"]
        for task in tasks:
            await task

        if len(users_response) == 100:
            offset += 100
            finished = False
        else:
            finished = True
    result = {'infoList': info_list}
    return result


def send_data(data):
    params = {
        "grant_type": "password",
        "client_id": client_id,  # Consumer Key
        "client_secret": client_secret,  # Consumer Secret
        "username": username,  # The email you use to login
        "password": password  # Concat your password and your security token
    }
    token_request = requests.post(token_endpoint, params=params)
    token_response = token_request.json()
    access_token = token_response['access_token']

    post_header = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }

    post_request = requests.post(post_endpoint, json=data, headers=post_header)
    print(post_request.status_code)


if __name__ == '__main__':
    print("start to fetch data from LMS ...")
    start = time.time()
    data = asyncio.run(get_data())
    print("cost: {}".format(time.time() - start))
    print("start to send data to CRM ...")
    send_data(data)
    print("Done")
