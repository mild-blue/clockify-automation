import base64
import datetime
import json
import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests

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


def calculate_duration(start, end):
    """Calculate the duration in seconds between start and end times."""
    duration = end - start
    return int(duration.total_seconds())


# Created by chatGPT
def get_report_data_from_csv(csv_file_path):
    # Load the CSV file into a pandas DataFrame
    toggl_data = pd.read_csv(csv_file_path)

    # List to hold transformed data
    transformed_data = []

    # Iterate through each row and map it to the desired format
    for index, row in toggl_data.iterrows():
        # Combine Start date and Start time to create ISO format datetime
        start_time = datetime.datetime.strptime(f"{row['Start date']} {row['Start time']}", "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(f"{row['End date']} {row['End time']}", "%Y-%m-%d %H:%M:%S")

        # Create the transformed dictionary (mimicking the API JSON format)
        entry = {
            'id': index + 1,  # Since CSV lacks an ID, use the row index + 1
            'workspace_id': 4526181,  # Placeholder
            'project_id': 202830918,  # Placeholder
            'task_id': None,  # CSV lacks task information
            'billable': True if row['Billable'].strip().lower() == 'yes' else False,
            'start': start_time.isoformat() + "+00:00",
            'stop': end_time.isoformat() + "+00:00",
            'duration': calculate_duration(start_time, end_time),
            'description': row['Description'],
            'tags': [] if pd.isna(row['Tags']) else [row['Tags']],  # Empty list if no tags
            'tag_ids': [],  # Placeholder for tag IDs
            'duronly': True,  # Placeholder
            'at': end_time.isoformat() + "+00:00",  # Using the stop time as the 'at' time
            'server_deleted_at': None,
            'user_id': 3787173,  # Placeholder
            'uid': 3787173,  # Placeholder
            'wid': 4526181,  # Placeholder
            'pid': 202830918,  # Placeholder
            'client_name': row['Client'],
            'project_name': row['Project'],
            'project_color': '#566614',  # Placeholder
            'project_active': True,  # Placeholder
            'project_billable': False,  # Placeholder
            'user_name': row['User'],
            'user_avatar_url': '',  # Placeholder
            'permissions': None  # Placeholder
        }

        # Append the transformed entry to the list
        transformed_data.append(entry)

    # Now transformed_data contains the structured data similar to the API response
    return transformed_data


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

    toggle_base_url = 'https://api.track.toggl.com/api/v9'

    token = config['ToggleApiKey']
    auth_string = f"{token}:api_token"
    encoded_auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")

    headers = {
        'Authorization': f'Basic {encoded_auth_string}',
        'Content-Type': 'application/json'
    }
    # get time entries
    params = {
        'start_date': config['From'],
        'end_date': config['To']
    }
    try:
        if config.get('import_from_csv') is True:
            report_data = get_report_data_from_csv(config.get('csv_file_path'))
        else:
            report_response = requests.get(f'{toggle_base_url}/me/time_entries?meta=true', headers=headers,
                                           params=params)
            report_response.raise_for_status()
            report_data = report_response.json()

        # print(report_data)
    except requests.exceptions.RequestException as e:
        logger.error(f'Error while getting data from Toggl: {str(e)}')
        return

    if config.get('DeleteExistingFrom') is True and config.get('DryRun') is False:
        delete_entries(clockify, clockify_settings, f'{config["From"]} 00:00:00')

    target_workspace_id = int(get_target_workspace_id(toggle_settings.workspace, headers))
    for row in report_data:
        if row['stop'] == None:  # if task is still running
            continue
        if int(row['workspace_id']) != target_workspace_id:
            continue
        if row['project_id'] == None:
            raise Exception(
                f'task "{row["description"]}" from {row["start"]} has no assigned project (project_id is None)')
        if config['ToggleFilterClient'] != row['client_name'] and config['ToggleFilterClient'] != '':
            continue
        if config['ToggleFilterUser'] != row['user_name'] and config['ToggleFilterUser'] != '':
            continue

        start = datetime.datetime.strptime(row["start"], "%Y-%m-%dT%H:%M:%S%z").strftime(CSV_DATE_TIME_FORMAT)
        start = datetime.datetime.strptime(start, CSV_DATE_TIME_FORMAT)
        end = datetime.datetime.strptime(row["stop"], "%Y-%m-%dT%H:%M:%S%z").strftime(CSV_DATE_TIME_FORMAT)
        end = datetime.datetime.strptime(end, CSV_DATE_TIME_FORMAT)

        tags = [tag.strip() for tag in row['tags'] if tag.strip() != '']

        # tag billable if there's a tag billable
        billable = 'billable' in tags
        # remove billable and non-billable tags as we don't need them anymore
        tags = [tag for tag in tags if tag not in {'non-billable', 'billable'}]

        if config.get('DryRun') is False:
            clockify.addEntry(
                start=start,
                description=row['description'],
                projectName=row['project_name'],
                userMail=clockify_settings.email,
                workspace=clockify_settings.workspace,
                end=end,
                billable=billable
            )
        else:
            logger.info('Dry run - nothing is sent to Clockify.')


if __name__ == '__main__':
    main()
