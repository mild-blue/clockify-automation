import csv
import datetime
import json
import logging
import os
import urllib
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4
import requests
from ClockifyAPI import ClockifyAPI
import base64

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
    clockify.deleteEntriesOfUser(
        clockify_settings.email,
        clockify_settings.workspace,
        datetime.datetime.strptime(from_datetime, CSV_DATE_TIME_FORMAT).astimezone(datetime.timezone.utc)
    )

def get_target_workspace_id(workspace_name: str, headers: dict):
    response = requests.get('https://api.track.toggl.com/api/v9/workspaces', headers=headers)
    response.raise_for_status()
    workspaces = response.json()
    for workspace in workspaces:
        if workspace['name'] == workspace_name:
            return str(workspace['id'])
    return None

def main():
    clockify_settings = ServiceSettings(
        config['ClockifyApiKey'],
        config['ClockifyWorkspace'],
        config['ClockifyAdminEmail']
    )

    toggle_settings = ServiceSettings(
        config['ToggleApiKey'],
        config['ToggleWorkspace']
    )

    clockify = ClockifyAPI(clockify_settings.token, clockify_settings.email, reqTimeout=1)
    clockify.getProjects(workspace=clockify_settings.workspace)

    toggle_api_key = config['ToggleApiKey']
    toggle_workspace = config['ToggleWorkspace']

    toggle_base_url = 'https://api.track.toggl.com/api/v9'
    toggle_reports_url = f'{toggle_base_url}/reports/api/v2'

    email = config['ToggleUser']
    token = config['ToggleApiKey']
    auth_string = f"{token}:api_token"
    encoded_auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")

    headers = {
        'Authorization': f'Basic {encoded_auth_string}',
        'Content-Type': 'application/json'
    }
    # get time entries
    file_name = f'{uuid4()}.csv'
    try:
        report_response = requests.get(f'{toggle_base_url}/me/time_entries?meta=true', headers=headers)
        report_response.raise_for_status()
        report_data = report_response.json()
        for report in report_data:
            if report['start'] < config['From']:
                report_data.remove(report)
                continue
            if  report['stop'] >= config['To']: 
                report_data.remove(report)
                continue
            description = report['description']
            start = report['start']
            if report['project_id'] == None:
                raise Exception(f'task "{description}" from {start} has no assigned project (project_id is None)')

        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
    except requests.exceptions.RequestException as e:
        logger.error(f'Error while getting data from Toggl: {str(e)}')
        return

    if config.get('DeleteExistingFrom') is True and config.get('DryRun') is False:
        delete_entries(clockify, clockify_settings, f'{config["From"]} 00:00:00')

    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if config['ToggleFilterClient'] != row['client_name'] and config['ToggleFilterClient'] != '':
                continue
            if row['workspace_id'] != get_target_workspace_id(toggle_settings.workspace, headers):
                continue
            
            if row['stop'] == '':
                continue
            
            logger.info(row)

            start = datetime.datetime.strptime(row["start"], "%Y-%m-%dT%H:%M:%S%z").strftime(CSV_DATE_TIME_FORMAT)
            start = datetime.datetime.strptime(start, CSV_DATE_TIME_FORMAT)
            end = datetime.datetime.strptime(row["stop"], "%Y-%m-%dT%H:%M:%S%z").strftime(CSV_DATE_TIME_FORMAT)
            end = datetime.datetime.strptime(end, CSV_DATE_TIME_FORMAT)

            tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip() != '']

            # tag billable if there's a tag billable
            billable = 'billable' in tags
            # remove billable and non-billable tags as we don't need them anymore
            tags = [tag for tag in tags if tag not in {'non-billable', 'billable'}]

            if config.get('DryRun') is False:
                clockify.addEntry(
                    start=start,
                    description=row['description'],
                    projectName= row['project_name'],
                    userMail=clockify_settings.email,
                    workspace=clockify_settings.workspace,
                    end=end,
                    billable=billable
                )
            else:
                logger.info('Dry run - nothing is sent to Clockify.')

    if os.path.exists(file_name):
        os.remove(file_name)

if __name__ == '__main__':
    main()
