import csv
import datetime
import json
import logging
from dataclasses import dataclass
from toggl.TogglPy import Toggl
from typing import Optional
from uuid import uuid4

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

CSV_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

config = {}
with open('config.json') as config_file:
    config = json.load(config_file)


@dataclass
class ServiceSettings:
    token: str
    workspace: str
    email: Optional[str] = None


def main():
    clockify_settings = ServiceSettings(config["ClockifyApiKey"],
                                        config["ClockifyWorkspace"],
                                        config["ClockifyAdminEmail"])
    toggle_settings = ServiceSettings(config["ToggleApiKey"], config["ToggleWorkspace"])

    clockify = ClockifyAPI(clockify_settings.token, clockify_settings.email, reqTimeout=1)
    clockify.getProjects(workspace=clockify_settings.workspace)

    toggl = Toggl()
    toggl.setAPIKey(config["ToggleApiKey"])

    wid = [w['id'] for w in toggl.getWorkspaces() if w['name'] == toggle_settings.workspace][0]
    start = config["From"]
    end = config["To"]
    csv_filter = {
        'workspace_id': wid,  # see the next example for getting a workspace id
        'since': start,
        'until': end,
    }
    file_name = f'{uuid4()}.csv'
    toggl.getDetailedReportCSV(csv_filter, file_name)

    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start = datetime.datetime.strptime(f'{row["Start date"]} {row["Start time"]}', CSV_DATE_TIME_FORMAT) \
                .astimezone(datetime.timezone.utc)
            end = datetime.datetime.strptime(f'{row["End date"]} {row["End time"]}', CSV_DATE_TIME_FORMAT) \
                .astimezone(datetime.timezone.utc)

            tags = list(filter(lambda x: x.strip() != '', row['Tags'].split(',')))

            billable = 'billable' in row['Tags'] and 'non-billable' not in row['Tags']

            logger.info(row)

            if not config["DryRun"]:
                clockify.addEntry(start=start, description=row['Description'], projectName=row['Project'],
                                  userMail=clockify_settings.email, workspace=clockify_settings.workspace, end=end,
                                  tagNames=tags, billable=billable)
            else:
                logger.info("Dry run - nothing is sent to Clockify.")


if __name__ == '__main__':
    main()
