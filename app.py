import requests
import re
from months import months
from datetime import datetime
import json
import sys

url = None
logs = []

def query_google():
    print("Querying Google")
    logs.append(f"{datetime.today()}: Querying Google")
    res = requests.get("https://www.google.com/search?&q=call+of+duty+patch+notes")
    logs.append(f"{datetime.today()}: Google Response:\nres.content.decode('ISO-8859-1')")
    return res.content.decode("ISO-8859-1")


def search_for_cod_patch_notes(res):
    print("Searching for COD Patch Notes")
    logs.append(f"{datetime.today()}: Searching for COD Patch Notes")
    pattern = '(url\?q=https:\/\/www\.infinityward\.com\/news\/[0-9][0-9][0-9][0-9]-[0-9][0-9]\/MW_Patch_Notes_[A-Z][a-z]..........)'
    x = re.search(pattern, res)
    logs.append(f"{datetime.today()}: Found: {x.group(0)}")
    return x.group(0)


def get_first_part_of_date(response):
    print(f"Check date of patch notes in rgex line: {response}")
    logs.append(f"{datetime.today()}: Check date of patch notes in rgex line: {response}")
    first_part_of_date = re.search("[0-9][0-9][0-9][0-9]-[0-9][0-9]", response).group(0)
    print(first_part_of_date)
    logs.append(f"{datetime.today()}: Found: {first_part_of_date}")
    return first_part_of_date


def get_second_part_of_date(response):
    print(f"Check date of patch notes in regex line: {response}")
    logs.append(f"{datetime.today()}: Getting second part of date")
    second_part_of_date = None
    for month in months:
        if month in response:
            print("Month found!")
            logs.append(f"{datetime.today()}: Month found {month}")
            pattern = f'({month}_[0-9].)'
            second_part_of_date = re.search(pattern, response).group(0)
            if second_part_of_date[-1].isdigit():
                second_part_of_date = second_part_of_date
            else:
                second_part_of_date = second_part_of_date[:-1]
            print(second_part_of_date)
            logs.append(f"{datetime.today()}: Second part of date: {second_part_of_date}")
            return second_part_of_date
    print("Month not found")
    logs.append(f"{datetime.today()}: Month not found")
    return ""


def format_date(first_date, second_date):
    print("Formatting Dates")
    logs.append(f"{datetime.today()}: Formatting Dates")
    second_date = second_date.split("_")[1]
    formatted_date = f"{first_date}-{second_date}"
    return formatted_date


def save_date_of_most_recent_patch_notes(date, loc):
    print(f"Saving most recent patch date to file: {current_patch_date}")
    logs.append(f"{datetime.today()}: Saving most recent patch date to file: {current_patch_date}")
    f = open(f"{loc}patch-date.txt", "w")
    f.write(date)
    f.close()


def read_date_of_last_patch(loc):
    logs.append(f"{datetime.today()}: Reading last date from file..")
    f = open(f"{loc}patch-date.txt", "r")
    logs.append(f"{datetime.today()}: Last date from file {f.read()}")
    return f.read()


def new_patch_is_released(current_date, previous_update_date, loc):
    print(f"Current Date: {current_date}\nPrevious Date: {previous_update_date}")
    logs.append(f"{datetime.today()}: Current Date: {current_date}\nPrevious Date: {previous_update_date}")
    current_date_converted = datetime.strptime(current_date, "%Y-%m-%d")
    previous_update_date_converted = datetime.strptime(previous_update_date, "%Y-%m-%d")
    logs.append(f"{datetime.today()}: Current Date Converted: {current_date_converted}\nPrevious Date Converted: {previous_update_date_converted}")
    print(f"Current Date Converted: {current_date_converted}\nPrevious Date Converted: {previous_update_date_converted}")
    if current_date_converted > previous_update_date_converted:
        print("Update now available!")
        logs.append(f"{datetime.today()}: Update Available!")
        save_date_of_most_recent_patch_notes(current_date, loc)
        return True
    else:
        print("No update available")
        return False


def generate_patch_notes_url(first_date, second_date):
    print("Generating URL...")
    logs.append(f"{datetime.today()}: Generating URL")
    global url
    url = f"https://www.infinityward.com/news/{first_date}/MW_Patch_Notes_{second_date}"
    print(f"Generated: {url}")
    logs.append(f"{datetime.today()}: Generated: {url}")
    return url


def verify_if_correct_url_is_generated(url):
    res = requests.get(url)
    res = res.content.decode("utf8")
    if "Sorry, an unexpected error occurred" in res:
        print("Incorrect URL Generated")
        logs.append(f"{datetime.today()}: Incorrect URL generated")
        return None
    else:
        print("URL is valid")
        logs.append(f"{datetime.today()}: URL is valid")
        return True


def check_if_new_patch_is_released(loc):
    global logs
    output_to_logfile(loc, logs)
    logs = []
    if new_patch_is_released(current_patch_date, last_patch_date, loc):
        url = generate_patch_notes_url(first_part, second_part)
        verify_url = verify_if_correct_url_is_generated(url)
        return verify_url


def send_slack_message(message, hook):
    print("Sending Slack message...")
    logs.append(f"{datetime.today()}: Sending Slack message...")
    slack_hook = f"https://hooks.slack.com/services/{hook}"
    payload = {"text": message}
    json_payload = json.dumps(payload)
    res = requests.post(slack_hook, data=json_payload)
    print(res.status_code)
    logs.append(f"{datetime.today()}: {res.status_code}")


def output_to_logfile(loc, messages):
    f = open(f"{loc}log.txt", "a")
    for message in messages:
        f.write(f"{message}")
    f.close()


if __name__ == '__main__':
    hook = sys.argv[1]
    location = sys.argv[2]
    response = query_google()
    call_of_duty_part_url = search_for_cod_patch_notes(response)
    first_part = get_first_part_of_date(call_of_duty_part_url)
    second_part = get_second_part_of_date(call_of_duty_part_url)
    current_patch_date = format_date(first_part, second_part)
    last_patch_date = read_date_of_last_patch(location)
    url_is_successful = check_if_new_patch_is_released(location)
    message = f"A new Call of Duty Warzone update is now available:\n{url}"
    if url_is_successful:
        send_slack_message(message, hook)
    output_to_logfile(location, logs)


