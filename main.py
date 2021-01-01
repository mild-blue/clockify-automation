import json
import logging
import os
from typing import Tuple, Optional

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


def load_data() -> Optional[Tuple[str, str]]:
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

    if "ClockifyKey" not in data:
        logger.error("json entry 'ClockifyKeys' missing in file %s" % f_name)
        return None

    clockify_token = data["ClockifyKey"]
    if not isinstance(clockify_token, str):
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

    return clockify_token, clockify_admin


def main():
    clockify_token, clockify_admin = load_data()
    clockify = ClockifyAPI(clockify_token, clockify_admin, reqTimeout=clockifyReqTimeout,
                           fallbackUserMail=fallbackUserMail)


if __name__ == '__main__':
    main()
