import json
import logging
from dashboard.dashboard import Dashboard as dash_c

all_dashboards_light = [] # stores all the dashboard metadata (without any panels/widgets or layout information). Useful to get dashboard id from dashboard name.
response_list = [] # stores all the responses - Useful to provide a summary report



class ExportDashboard:
    def __init__(self, endpoint_url, api_token, fetch_all, ids, names, output_folder):
        self.api_token = api_token
        self.endpoint_url = endpoint_url
        self.fetch_all = fetch_all
        self.ids = ids
        self.names = names
        self.output_folder = output_folder

    def export_dashboard(self):

        global logger
        logger = logging.getLogger(__name__)

        global dash
        dash = dash_c(self.endpoint_url, self.api_token)

        if self.fetch_all:
            response = dash.get_all_dashboards(False)
            if response.ok:
                dashboards = json.loads(response.text)
                for dashboard_data_tmp in dashboards["dashboards"]:
                    try:
                        dashboard_data = {"dashboard": dashboard_data_tmp}
                        file_name = write_dashboard_to_file(dashboard_data, self.output_folder)
                        logger.debug(file_name + " created successfully.")
                    except FileNotFoundError as e:
                        add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "error", e.strerror + e.filename, e.filename)

                    add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "success", "", file_name)
        else:
            if len(self.ids) > 0:
                data = self.ids.split(",")
                for d in data:
                    response = dash.get_dashboard_by_id(d)

                    if response.ok:
                        dashboard_data = json.loads(response.text)
                        file_name = write_dashboard_to_file(dashboard_data, self.output_folder)
                        add_response_to_list(d, "", "success", "", file_name)
                    else:
                        add_response_to_list(d, "", "error", response.reason, "")

            if len(self.names) > 0:
                data = self.names.split(",")
                for d in data:
                    dashboard = get_dashboard_id_from_name(self.endpoint_url, self.api_token, d)
                    if len(dashboard) > 0:
                        response = dash.get_dashboard_by_id(dashboard["id"])
                        if response.ok:
                            dashboard_data = json.loads(response.text)
                            file_name = write_dashboard_to_file(dashboard_data, self.output_folder)
                            add_response_to_list(dashboard["id"], d, "success", "", file_name)
                        else:
                            add_response_to_list(dashboard["id"], d, "error", response.reason, "")
                    else:
                        add_response_to_list("", d, "error", "dashboard not found", "")
        print_summary()
        log_summary()
        return

def add_response_to_list(id, name, status, error, file_name):

    response_dict = {}
    global response_list

    response_dict["id"] = id
    response_dict["name"] = name
    response_dict["status"] = status
    response_dict["error"] = error
    response_dict["file_name"] = file_name

    response_list.append(response_dict)

def write_dashboard_to_file(dashboard_data, output_folder):

    file_name = str(dashboard_data["dashboard"]["id"]) + "-" + dashboard_data["dashboard"]["name"] + ".json"
    with open(output_folder + file_name, 'w') as outfile:
        json.dump(dashboard_data, outfile)

    logger.debug("Successfully exported the dashboard - " + file_name)

    return file_name

def get_dashboard_id_from_name(endpoint_url, api_token, dashboard_name):
    global all_dashboards_light
    if len(all_dashboards_light) == 0:
        all_dashboards_light = json.loads(dash.get_all_dashboards(True).text)

    dashboard = [dash for dash in all_dashboards_light["dashboards"] if dash["name"] == dashboard_name]
    if len(dashboard) > 0:
        return dashboard[0]
    else:
        return []


def print_summary():

    success_count = len([r for r in response_list if r["status"] == "success"])
    error_count = len([r for r in response_list if r["status"] == "error"])

    print("="*70)
    print(str(success_count) + " dashboards exported successfully and " + str(error_count) + " dashboards failed.")
    print("=" * 70)

    for r in response_list:
        print("\tDashboard Id: " + str(r["id"]))
        print("\tDashboard Name: " + r["name"])
        print("\tStatus: " + r["status"])
        print("\tFile Name: " + r["file_name"])
        if r["status"] == "error":
            print("\tError: " + r["error"])
        print("\t", end="")
        print("-" * 60)


def log_summary():
    success_count = len([r for r in response_list if r["status"] == "success"])
    error_count = len([r for r in response_list if r["status"] == "error"])

    logger.debug("=" * 70)
    logger.debug('%s dashboards exported successfully %s dashboards failed.',str(success_count), str(error_count))

    logger.debug("=" * 70)

    for r in response_list:
        logger.debug("\tDashboard Id: " + str(r["id"]))
        logger.debug("\tDashboard Name: " + r["name"])
        logger.debug("\tStatus: " + r["status"])
        logger.debug("\tFile Name: " + r["file_name"])
        if r["status"] == "error":
            logger.debug("\tError: " + r["error"])
        logger.debug("-" * 60)
