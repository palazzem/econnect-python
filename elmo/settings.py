from os import getenv


# Environment variables are required to configure the system
# TODO: implement a Config class that raise exceptions if
# not properly configured
BASE_URL = getenv("ALERTING_ENDPOINT")
VENDOR = getenv("ALERTING_VENDOR")

# Credentials
USERNAME = getenv("ALERTING_USERNAME")
PASSWORD = getenv("ALERTING_PASSWORD")
