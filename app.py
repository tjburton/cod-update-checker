import sys
from codupdate import CheckLatestCODUpdate


def get_latest_cod_update():
    cod_update = CheckLatestCODUpdate()
    cod_update.location = location
    response = cod_update.query_google()
    call_of_duty_part_url = cod_update.search_for_cod_patch_notes(response)
    first_part = cod_update.get_first_part_of_date(call_of_duty_part_url)
    second_part = cod_update.get_second_part_of_date(call_of_duty_part_url)
    cod_update.first_part_of_date = first_part
    cod_update.second_part_of_date = second_part
    current_patch_date = cod_update.format_date(first_part, second_part)
    cod_update.read_date_of_last_patch()
    url_is_successful = cod_update.check_if_new_patch_is_released(current_patch_date)
    if url_is_successful:
        message = f"A new Call of Duty Warzone Update is available:\n{cod_update.url}"
        cod_update.send_slack_message(message, hook)


if __name__ == '__main__':
    hook = sys.argv[1]
    location = sys.argv[2]
    get_latest_cod_update()



