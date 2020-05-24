import requests
import re
from months import months
from datetime import datetime
import json
import sys

url = None
location = sys.argv[2]

def query_google():
    print("Querying Google")
    res = requests.get("https://www.google.com/search?&q=call+of+duty+patch+notes")
    return res.content.decode("ISO-8859-1")


def search_for_cod_patch_notes(res):
    print("Searching for COD Patch Notes")
    pattern = '(url\?q=https:\/\/www\.infinityward\.com\/news\/)(.................................................................)'
    x = re.search(pattern, res)
    return x.group(2)


def get_first_part_of_date(response):
    print(f"Check date of patch notes in rgex line: {response}")
    first_part_of_date = re.search("[0-9][0-9][0-9][0-9]-[0-9][0-9]", response).group(0)
    print(first_part_of_date)
    return first_part_of_date


def get_second_part_of_date(response):
    print(f"Check date of patch notes in regex line: {response}")
    second_part_of_date = None
    for month in months:
        if month in response:
            pattern = f'({month}_[0-9][0-9])'
            second_part_of_date = re.search(pattern, response).group(0)
            print(second_part_of_date)
    return second_part_of_date


def format_date(first_date, second_date):
    print("Formatting Dates")
    second_date = second_date.split("_")[1]
    formatted_date = f"{first_date}-{second_date}"
    return formatted_date


def save_date_of_most_recent_patch_notes(date):
    print(f"Saving most recent patch date to file: {current_patch_date}")
    f = open(f"{location}patch-date.txt", "w")
    f.write(date)
    f.close()


def read_date_of_last_patch():
    f = open(f"{location}patch-date.txt", "r")
    return f.read()


def new_patch_is_released(current_date, previous_update_date):
    if datetime.strptime(current_date, "%Y-%m-%d") > datetime.strptime(previous_update_date, "%Y-%m-%d"):
        print("Update now available!")
        save_date_of_most_recent_patch_notes(current_date)
        return True
    else:
        print("No update available")
        return False


def generate_patch_notes_url(first_date, second_date):
    print("Generating URL...")
    global url
    url = f"https://www.infinityward.com/news/{first_date}/MW_Patch_Notes_{second_date}"
    print(f"Generated: {url}")
    return url


def verify_if_correct_url_is_generated(url):
    res = requests.get(url)
    res = res.content.decode("utf8")
    if "Sorry, an unexpected error occurred" in res:
        print("Incorrect URL Generated")
        return None
    else:
        print("URL is valid")
        return True


def check_if_new_patch_is_released():
    if new_patch_is_released(current_patch_date, last_patch_date):
        url = generate_patch_notes_url(first_part, second_part)
        verify_url = verify_if_correct_url_is_generated(url)
        return verify_url


def send_slack_message(hook):
    print("Sending Slack message...")
    slack_hook = f"https://hooks.slack.com/services/{hook}"
    message = f"A new Call of Duty Warzone update is now available:\n{url}"
    payload = {"text": message}
    json_payload = json.dumps(payload)
    res = requests.post(slack_hook, data=json_payload)
    print(res.status_code)


if __name__ == '__main__':
    hook = sys.argv[1]
    response = query_google()
    call_of_duty_part_url = search_for_cod_patch_notes(response)
    first_part = get_first_part_of_date(call_of_duty_part_url)
    second_part = get_second_part_of_date(call_of_duty_part_url)
    current_patch_date = format_date(first_part, second_part)
    last_patch_date = read_date_of_last_patch()
    url_is_successful = check_if_new_patch_is_released()
    if url_is_successful:
        send_slack_message(hook)


