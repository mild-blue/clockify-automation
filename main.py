import csv
import datetime
import json
import logging
import os
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from toggl.TogglPy import Toggl

from ClockifyAPI import ClockifyAPI

formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
fileHandler = logging.FileHandler('log.txt')
fileHandler.setFormatter(formatter)

logger = logging.getLogger('clockify-automation')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(fileHandler)

CSV_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

with open('config.json') as config_file:
    config = json.load(config_file)


@dataclass
class ServiceSettings:
    token: str
    workspace: str
    email: Optional[str] = None


def delete_entries(clockify: ClockifyAPI, clockify_settings: ServiceSettings, from_datetime: str):
    clockify.deleteEntriesOfUser(clockify_settings.email, clockify_settings.workspace,
                                 datetime.datetime.strptime(from_datetime, CSV_DATE_TIME_FORMAT).astimezone(
                                     datetime.timezone.utc))


def main():
    clockify_settings = ServiceSettings(config['ClockifyApiKey'],
                                        config['ClockifyWorkspace'],
                                        config['ClockifyAdminEmail'])
    toggle_settings = ServiceSettings(config['ToggleApiKey'], config['ToggleWorkspace'])

    clockify = ClockifyAPI(clockify_settings.token, clockify_settings.email, reqTimeout=1)
    clockify.getProjects(workspace=clockify_settings.workspace)

    toggl = Toggl()
    toggl.setAPIKey(config['ToggleApiKey'])

    wid = [w['id'] for w in toggl.getWorkspaces() if w['name'] == toggle_settings.workspace][0]
    start = config['From']
    end = config['To']
    csv_filter = {
        'workspace_id': wid,  # see the next example for getting a workspace id
        'since': start,
        'until': end,
    }
    file_name = f'{uuid4()}.csv'
    toggl.getDetailedReportCSV(csv_filter, file_name)

    if config.get('DeleteExistingFrom') is True and config.get('DryRun') is False:
        delete_entries(clockify, clockify_settings, f'{start} 00:00:00')

    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if config.get('ToggleFilterClient') and config['ToggleFilterClient'] != row['Client']:
                continue
            if config.get('ToggleFilterUser') and config['ToggleFilterUser'] != row['Email']:
                continue

            logger.info(row)

            start = datetime.datetime.strptime(f'{row["Start date"]} {row["Start time"]}', CSV_DATE_TIME_FORMAT) \
                .astimezone(datetime.timezone.utc)
            end = datetime.datetime.strptime(f'{row["End date"]} {row["End time"]}', CSV_DATE_TIME_FORMAT) \
                .astimezone(datetime.timezone.utc)

            tags = [tag.strip() for tag in row['Tags'].split(',') if tag.strip() != '']

            # tag billable if there's a tag billable
            billable = 'billable' in tags
            # remove billable and non-billable tags as we don't need them anymore
            tags = [tag for tag in tags if tag not in {'non-billable', 'billable'}]

            if config.get('DryRun') is False:
                clockify.addEntry(start=start, description=row['Description'], projectName=row['Project'],
                                  userMail=clockify_settings.email, workspace=clockify_settings.workspace, end=end,
                                  tagNames=tags, billable=billable)
            else:
                logger.info('Dry run - nothing is sent to Clockify.')

    if os.path.exists(file_name):
        os.remove(file_name)


if __name__ == '__main__':
    main()
