import requests
import time
import os

from local_settings import API_KEY


BASE_URL = "https://api.litmos.com/v1.svc"
SUFFIX = "?source=MY-APP&format=json"

# category
SAIC = "SAIC_Motor"
MG = "MG"
RC = "Resources_Center"


def get_data():
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
        for user_data in users_response:
            courses_url = user_courses_url.format(user_id=user_data['Id'])
            info = {
                "email": user_data['Email']
            }
            SAIC_completed = 0
            SAIC_total = 0
            MG_completed = 0
            MG_total = 0
            RC_completed = 0
            RC_total = 0
            try:
                courses_request = requests.get(courses_url, headers=header)
                if courses_request.status_code != 200:
                    # log
                    continue
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
                if SAIC_total > 0:
                    info[SAIC+'_completed'] = SAIC_completed
                    info[SAIC+'_total'] = SAIC_total
                if MG_total > 0:
                    info[MG+'_completed'] = MG_completed
                    info[MG+'_total'] = MG_total
                if RC_total > 0:
                    info[RC+'_completed'] = RC_completed
                    info[RC+'_total'] = RC_total

                info_list.append(info)
            except Exception as e:
                # log
                continue

        result = {'info_list': info_list}
        finished = True

    return result


star_time = time.time()
get_data()
print(time.time() - star_time)
