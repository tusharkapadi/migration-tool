import requests
import json
import logging

logger = logging.getLogger(__name__)


class Dashboard:
    def __init__(self, endpoint_url, api_token):
        self.api_token = api_token
        self.endpoint_url = endpoint_url

    def get_dashboard_by_id(self, dashboard_id):

        url = self.endpoint_url + "/api/v3/dashboards/" + str(dashboard_id)

        response = requests.request("GET", url, headers=prepare_http_header(self.api_token), data={})

        if response.ok is False:
            logger.error("Received an error getting a dashboard (" + url + ") - " + json.dumps(response.reason))
            logger.debug("------- error generating payload -------")
            logger.debug(response.text)

        return response

    def get_all_dashboards(self, isLight):

        if isLight:
            url = self.endpoint_url + "/api/v3/dashboards/?light=true"
        else:
            url = self.endpoint_url + "/api/v3/dashboards"

        response = requests.request("GET", url, headers=prepare_http_header(self.api_token), data={})

        if not response.ok:
            logger.error("Received an error getting all dashboards (" + url + ") - " + json.dumps(response.reason))
            logger.debug("------- error generating payload -------")
            logger.debug(response.text)

        return response

    def update_dashboard(self, dashboard_data):

        dashboard_id = dashboard_data["dashboard"]["id"]
        url = self.endpoint_url + "/api/v3/dashboards/" + str(dashboard_id)

        response = requests.request("PUT", url, headers=prepare_http_header(self.api_token), data=json.dumps(dashboard_data))

        if not response.ok:
            logger.error("Received an error updating a dashboard (" + url + ") - " + json.dumps(response.reason))
            logger.debug("------- error generating payload -------")
            logger.debug(response.text)

        return response

    def create_dashboard(self, dashboard_data):

        # remove dashboard id and version from the json
        dashboard_data["dashboard"]["id"] = ""
        if "version" in dashboard_data["dashboard"]: dashboard_data["dashboard"]["version"] = ""

        url = self.endpoint_url + "/api/v3/dashboards/"

        response = requests.request("POST", url, headers=prepare_http_header(self.api_token), data=json.dumps(dashboard_data))

        if not response.ok:
            logger.error("Received an error creating a dashboard (" + url + ") - " + json.dumps(response.reason))
            logger.debug("------- error generating payload -------")
            logger.debug(response.text)

        return response


def prepare_http_header(api_token):
    auth = "Bearer " + api_token
    headers = {'Content-Type': 'application/json', 'Authorization': auth}

    return headers