import requests
import re
from months import months
from datetime import datetime
import json


class CheckLatestCODUpdate:
    def __init__(self):
        self.url = None
        self.loc = None
        self.current_patch_date = None
        self.previous_date = None
        self.first_date = None
        self.second_date = None

    def query_google(self):
        print("Querying Google")
        self.output_message_to_logfile(f"{datetime.today()}: Querying Google")
        res = requests.get("https://www.google.com/search?&q=call+of+duty+patch+notes")
        self.output_message_to_logfile(f"{datetime.today()}: Google Response:\n{res.content.decode('ISO-8859-1')}")
        return res.content.decode("ISO-8859-1")

    def search_for_cod_patch_notes(self, res):
        print("Searching for COD Patch Notes")
        self.output_message_to_logfile(f"{datetime.today()}: Searching for COD Patch Notes")
        pattern = '(url\?q=https:\/\/www\.infinityward\.com\/news\/[0-9][0-9][0-9][0-9]-[0-9][0-9]\/MW_Patch_Notes_[A-Z][a-z]..........)'
        x = re.search(pattern, res)
        self.output_message_to_logfile(f"{datetime.today()}: Found: {x.group(0)}")
        return x.group(0)

    def get_first_part_of_date(self, response):
        print(f"Check date of patch notes in rgex line: {response}")
        self.output_message_to_logfile(f"{datetime.today()}: Check date of patch notes in rgex line: {response}")
        first_part_of_date = re.search("[0-9][0-9][0-9][0-9]-[0-9][0-9]", response).group(0)
        print(first_part_of_date)
        self.output_message_to_logfile(f"{datetime.today()}: Found: {first_part_of_date}")
        return first_part_of_date

    def get_second_part_of_date(self, response):
        print(f"Check date of patch notes in regex line: {response}")
        self.output_message_to_logfile(f"{datetime.today()}: Getting second part of date")
        for month in months:
            if month in response:
                print("Month found!")
                self.output_message_to_logfile(f"{datetime.today()}: Month found {month}")
                pattern = f'({month}_[0-9].)'
                second_part_of_date = re.search(pattern, response).group(0)
                if second_part_of_date[-1].isdigit():
                    second_part_of_date = second_part_of_date
                else:
                    second_part_of_date = second_part_of_date[:-1]
                print(second_part_of_date)
                self.output_message_to_logfile(f"{datetime.today()}: Second part of date: {second_part_of_date}")
                return second_part_of_date
        print("Month not found")
        self.output_message_to_logfile(f"{datetime.today()}: Month not found")
        return ""

    def format_date(self, first_date, second_date):
        print("Formatting Dates")
        self.output_message_to_logfile(f"{datetime.today()}: Formatting Dates")
        second_date = second_date.split("_")[1]
        formatted_date = f"{first_date}-{second_date}"
        return formatted_date

    def save_date_of_most_recent_patch_notes(self, date):
        print(f"Saving most recent patch date to file: {date}")
        self.output_message_to_logfile(f"{datetime.today()}: Saving most recent patch date to file: {date}")
        f = open(f"{self.loc}resources/patch-date.txt", "w")
        f.write(date)
        f.close()

    def read_date_of_last_patch(self):
        self.output_message_to_logfile(f"{datetime.today()}: Reading last date from file..")
        f = open(f"{self.loc}resources/patch-date.txt", "r")
        self.previous_patch_date = f.read()
        self.output_message_to_logfile(f"{datetime.today()}: Last date from file: {self.previous_patch_date}")
        return self.previous_patch_date

    def new_patch_is_released(self, current_date):
        print(f"Current Date: {current_date}\nPrevious Date: {self.previous_patch_date}")
        self.output_message_to_logfile(
            f"{datetime.today()}: Current Date: {current_date}\nPrevious Date: {self.previous_patch_date}"
        )
        current_date_converted = datetime.strptime(current_date, "%Y-%m-%d")
        previous_update_date_converted = datetime.strptime(self.previous_patch_date, "%Y-%m-%d")
        self.output_message_to_logfile(f"{datetime.today()}: Current Date Converted: {current_date_converted}\nPrevious Date Converted: {previous_update_date_converted}")
        print(f"Current Date Converted: {current_date_converted}\nPrevious Date Converted: {previous_update_date_converted}")
        if current_date_converted > previous_update_date_converted:
            print("Update now available!")
            self.output_message_to_logfile(f"{datetime.today()}: Update Available!")
            self.save_date_of_most_recent_patch_notes(current_date)
            return True
        else:
            print("No update available")
            self.output_message_to_logfile(f"{datetime.today()}: No update available")
            return False

    def generate_patch_notes_url(self, first_date, second_date):
        print("Generating URL...")
        self.output_message_to_logfile(f"{datetime.today()}: Generating URL")
        global url
        url = f"https://www.infinityward.com/news/{first_date}/MW_Patch_Notes_{second_date}"
        print(f"Generated: {url}")
        self.output_message_to_logfile(f"{datetime.today()}: Generated: {url}")
        return url

    def verify_if_correct_url_is_generated(self, url):
        res = requests.get(url)
        res = res.content.decode("utf8")
        if "Sorry, an unexpected error occurred" in res:
            print("Incorrect URL Generated")
            self.output_message_to_logfile(f"{datetime.today()}: Incorrect URL generated")
            return None
        else:
            print("URL is valid")
            self.output_message_to_logfile(f"{datetime.today()}: URL is valid")
            return True

    def check_if_new_patch_is_released(self, current_patch_date):
        if self.new_patch_is_released(current_patch_date):
            self.patch_url = self.generate_patch_notes_url(self.first_part_of_date, self.second_part_of_date)
            verify_url = self.verify_if_correct_url_is_generated(url)
            return verify_url

    def send_slack_message(self, message, hook):
        print("Sending Slack message...")
        self.output_message_to_logfile(f"{datetime.today()}: Sending Slack message...")
        slack_hook = f"https://hooks.slack.com/services/{hook}"
        payload = {"text": message}
        json_payload = json.dumps(payload)
        res = requests.post(slack_hook, data=json_payload)
        print(res.status_code)
        self.output_message_to_logfile(f"{datetime.today()}: {res.status_code}")

    def output_messages_to_logfile(self, messages):
        f = open(f"{self.loc}resources/log.txt", "a")
        for message in messages:
            f.write(f"{message}\n")
        f.close()

    def output_message_to_logfile(self, message):
        f = open(f"{self.loc}resources/log.txt", "a")
        f.write(f"{message}\n")
        f.close()

    @property
    def location(self):
        return self.loc

    @location.setter
    def location(self, loc):
        self.loc = loc

    @property
    def patch_url(self):
        return self.url

    @patch_url.setter
    def patch_url(self, url):
        self.url = url

    @property
    def previous_patch_date(self):
        return self.previous_date

    @previous_patch_date.setter
    def previous_patch_date(self, previous_date):
        self.previous_date = previous_date

    @property
    def first_part_of_date(self):
        return self.first_date

    @first_part_of_date.setter
    def first_part_of_date(self, first_date):
        self.first_date = first_date

    @property
    def second_part_of_date(self):
        return self.second_date

    @second_part_of_date.setter
    def second_part_of_date(self, second_date):
        self.second_date = second_date
