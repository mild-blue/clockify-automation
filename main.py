import datetime
import json
import logging
import os
from typing import Tuple, Optional, List

import pandas as pd

from ClockifyAPI import ClockifyAPI

formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
fileHandler = logging.FileHandler("log.txt")
fileHandler.setFormatter(formatter)

logger = logging.getLogger("clockify-automation")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(fileHandler)

clockifyReqTimeout = 1
fallbackUserMail = None
workspace = "cl_test"


def load_clockify_api_data() -> Optional[Tuple[List[str], str]]:
    f_name = os.path.abspath("config.json")
    try:
        f = open(f_name, "r")
    except FileNotFoundError:
        logger.error("file %s not found" % f_name)
        return None

    try:
        data = json.load(f)
    except Exception as e:
        logger.error("reading content of json file %s failed with msg: %s" % (f_name, str(e)))
        return None

    if "ClockifyKeys" not in data:
        logger.error("json entry 'ClockifyKeys' missing in file %s" % f_name)
        return None

    clockify_tokens = data["ClockifyKeys"]
    if not isinstance(clockify_tokens, list):
        logger.error("json entry 'ClockifyKeys' must be a list of strings")
        return None

    if "Workspaces" in data:
        workspaces = data["Workspaces"]
        if not isinstance(workspaces, list):
            logger.error("json entry 'Workspaces' must be a list")
            return None
    else:
        workspaces = None

    if "ClockifyAdmin" not in data:
        logger.error("json entry 'ClockifyAdmin' missing in file %s" % f_name)
        return None
    else:
        clockify_admin = data["ClockifyAdmin"]
        if not isinstance(clockify_admin, str):
            logger.error("json entry 'ClockifyAdmin' must be a string")
            return None

    if "FallbackUserMail" in data:
        fallback_user_email = data["FallbackUserMail"]
    else:
        fallback_user_email = None

    return clockify_tokens, clockify_admin


def main():
    clockify_tokens, clockify_admin = load_clockify_api_data()
    clockify = ClockifyAPI(clockify_tokens, clockify_admin, reqTimeout=clockifyReqTimeout,
                           fallbackUserMail=fallbackUserMail)
    clockify.getProjects(workspace=workspace)
    clockify.deleteEntriesOfUser("ireallyhateyourservices@gmail.com", workspace)

    time_entries = pd.read_csv("Clockify_Detailed_Report_01_01_2020-12_31_2020_noTK.csv")
    for i, entry in time_entries.iterrows():
        start = datetime.datetime.strptime(f'{entry["Start Date"]} {entry["Start Time"]}', '%m/%d/%Y %I:%M:%S %p') \
            .astimezone(datetime.timezone.utc)
        end = datetime.datetime.strptime(f'{entry["End Date"]} {entry["End Time"]}', '%m/%d/%Y %I:%M:%S %p') \
            .astimezone(datetime.timezone.utc)
        tags = entry.Tags.split(', ') if isinstance(entry.Tags, str) else None
        billable = entry.Billable == 'Yes' or (tags is not None and 'billable' in tags)
        clockify.addEntry(start=start, description=entry.Description, projectName=entry.Project,
                          userMail="ireallyhateyourservices@gmail.com", workspace=workspace, end=end,
                          tagNames=tags, billable=billable)
        logger.info(i)


if __name__ == '__main__':
    main()
