# Toggle to Clockify

It is based on https://github.com/pieye/toggl2clockify and significant part of the code is just copied from there.
Credits to Markus Proeller, markus.proeller@pieye.org.

## Setup

* Create virtual env: `python -m venv venv` and activate it: `. ./venv/bin/activate `.
* Install requirements: `pip install -r requirements.txt`.
* Set proper values in `config.json`, use `config_example.json` as a base.
* Run it: `python main.py`

## Configuration

- `ClockifyApiKey` - API key to your account in clockify
- `ClockifyAdminEmail` - email of the person you want to assign the time entries (usually your own email). Should be the
  same as in Toggle (otherwise the script has to be updated)
- `ClockifyWorkspace` - Clockify workspace
- `ToggleApiKey` - API key for Toggle
- `ToggleWorkspace` - Toggle workspace
- `ToggleFilterClient` - if you use a personal workspace and have just one client for all projects and want to filter by
  that one - fill the name, otherwise leave empty
- `ToggleFilterUser` - filter Toggle user - same as `ToggleFilterClient` but for the user, useful when there are more
  users in one workspace, and you want to export just one
- `From` - from when start exporting the data in format `YYYY-MM-DD`
- `To` - end date for data export in format `YYYY-MM-DD`
- `DeleteExistingFrom` - delete all entries from Clockify starting from the `From` date (*NOTE: that it even deletes
  entries with date `>= To`*)
- `DryRun` - if true, it does not export data to Clockify, just prints them to console

#### Example config

When your Clockify account is `mygmail+clockify@gmail.com`, target clockify workspace is `Mild Blue` and source Toggle
workspace is `Personal` with client `Mild Blue` and user `mygmail+toggl@gmail.com`.

```json
{
  "ClockifyApiKey": "xxxxxxxxxxxxxxxxxx",
  "ClockifyAdminEmail": "mygmail+clockify@gmail.com",
  "ClockifyWorkspace": "Mild Blue",
  "ToggleApiKey": "yyyyyyyyyyyyyyyyyyyyyyyyyy",
  "ToggleWorkspace": "Personal",
  "ToggleFilterClient": "Mild Blue",
  "ToggleFilterUser": "mygmail+toggl@gmail.com",
  "From": "2021-01-01",
  "To": "2021-01-31",
  "DeleteExistingFrom": false,
  "DryRun": false
}

```