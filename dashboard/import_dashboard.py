import json
import logging
import os
from dashboard.dashboard import Dashboard as dash_c


all_dashboards_light = []  # stores all the dashboard metadata (without any panels/widgets or layout information). Useful to get dashboard id from dashboard name.
response_list = []  # stores all the responses - Useful to provide a summary report

logger = logging.getLogger(__name__)

class ImportDashboard:
    def __init__(self, endpoint_url, api_token, input_folder, plan, yes):
        self.api_token = api_token
        self.endpoint_url = endpoint_url
        self.input_folder = input_folder
        self.plan = plan
        self.yes = yes

    def import_dashboard(self):

        global dash
        dash = dash_c(self.endpoint_url, self.api_token)

        # prepare a list of dashboards from input folder
        dashboard_json_list = get_dashboards_json_list(self.input_folder)

        # prepare a plan for import
        import_plan(self.endpoint_url, self.api_token, dashboard_json_list)

        # print out the plan, if -plan option is provided.
        if self.plan:
            print_plan(dashboard_json_list)

            # skip confirmation if -yes is provided
            if not self.yes:
                capture_user_input()

        import_dashboards(self.endpoint_url, self.api_token, dashboard_json_list, self.input_folder)

        print_summary()
        log_summary()
        return


def get_files_list(path):
    import_dashboard_files = []

    walk_dir = path
    logger.debug('walk_dir = ' + walk_dir)
    logger.debug('walk_dir (absolute) = ' + os.path.abspath(walk_dir))



    for root, subdirs, files in os.walk(walk_dir):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(os.path.abspath(root), filename)
                logger.debug('\t- file %s (full path: %s)' % (filename, file_path))
                import_dashboard_files.append(file_path)
            else:
                logger.debug("Ignoring non-Json file - " + filename)

    return import_dashboard_files


def get_dashboards_json_list(path):
    dashboards_json_list = []

    files = get_files_list(path)

    curr_index = 0
    for f in files:
        with open(f, "r+") as f1:
            dashboards_json_list.append(json.loads(f1.read()))
            dashboards_json_list[curr_index]["file_name"] = f
            curr_index += 1

    return dashboards_json_list


def import_plan(endpoint_url, api_token, dashboards):


    for d in dashboards:
        #res = get_dashboard_by_id(endpoint_url, api_token, d["dashboard"]["id"])

        res = dash.get_dashboard_by_id(d["dashboard"]["id"])

        if res.ok and res.status_code == 200:  # dashboard found in Sysdig

            dashboard = json.loads(res.text)
            d["status"] = create_plan_dict(d["dashboard"]["id"], d["dashboard"]["name"], dashboard["dashboard"]["version"], "update",
                                                        len(dashboard["dashboard"]["panels"]), len(d["dashboard"]["panels"]), d["file_name"])

        elif res.ok == False and res.status_code == 404:  # dashboard not found in Sysdig
            d["status"] = create_plan_dict(d["dashboard"]["id"], d["dashboard"]["name"], 1, "create", 0, len(d["dashboard"]["panels"]), d["file_name"])


def create_plan_dict(id, name, version, operation, total_panels_in_sysdig, total_panels_in_file, file_name):
    dashboard_dict = {}

    dashboard_dict["id"] = id
    dashboard_dict["name"] = name
    dashboard_dict["version"] = version
    dashboard_dict["operation"] = operation
    dashboard_dict["total_panels_in_sysdig"] = total_panels_in_sysdig
    dashboard_dict["total_panels_in_file"] = total_panels_in_file
    dashboard_dict["file_name"] = file_name

    return dashboard_dict

def import_dashboards(endpoint_url, api_token, dashboards, input_folder):

    for d in dashboards:
        if d["status"]["operation"] == "create":
            res = dash.create_dashboard(d)
            if res.ok:
                dashboard_data = json.loads(res.text)

                # create new dashboard json file with new dashboard id and delete the old one.
                new_file_name = write_dashboard_to_file(dashboard_data, input_folder)
                os.remove(d["status"]["file_name"])

                #update response status
                add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "create", "success", "", d["file_name"], new_file_name)
            else:
                add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "create", "error", res.reason, d["file_name"], "")

        elif d["status"]["operation"] == "update":  # update dashboard

            d["dashboard"]["version"] = d["status"]["version"]
            res = dash.update_dashboard(d)
            if res.ok:
                dashboard_data = json.loads(res.text)
                add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "update", "success", "", d["file_name"], "")
            else:
                add_response_to_list(dashboard_data["dashboard"]["id"], dashboard_data["dashboard"]["name"], "update", "error", res.reason, d["file_name"], "")


def add_response_to_list(id, name, operation, status, error, file_name, new_file_name):
    response_dict = {}
    global response_list

    response_dict["id"] = id
    response_dict["name"] = name
    response_dict["operation"] = operation
    response_dict["status"] = status
    response_dict["error"] = error
    response_dict["file_name"] = file_name
    response_dict["new_file_name"] = new_file_name


    response_list.append(response_dict)


def write_dashboard_to_file(dashboard_data, output_folder):
    file_name = str(dashboard_data["dashboard"]["id"]) + "-" + dashboard_data["dashboard"]["name"] + ".json"
    with open(output_folder + file_name, 'w') as outfile:
        json.dump(dashboard_data, outfile)

    return file_name

def print_plan(dashboard_plan_list):
    print("")
    print("Script will perform following actions on dashboards:")
    for d in dashboard_plan_list:
        print("\t",end="")
        print("-" * 60)
        print("\tDashboard Id: " + str(d["status"]["id"]))
        print("\tDashboard Name: " + d["status"]["name"])
        print("\tOperation: " + d["status"]["operation"])
        print("\tTotal Panels found in Dashboard in Sysdig: " + str(d["status"]["total_panels_in_sysdig"]))
        print("\tTotal Panels found in Dashboard in File: " + str(d["status"]["total_panels_in_file"]))

    create_count = len([d["status"]["operation"] for d in dashboard_plan_list if d["status"]["operation"] == "create"])
    update_count = len([d["status"]["operation"] for d in dashboard_plan_list if d["status"]["operation"] == "update"])
    print("")
    print("Plan: " + str(create_count) + " to create, " + str(update_count) + " to update")

def capture_user_input():
    yes = False
    user_input = ""

    while True:
        if user_input.lower() == "yes":
            yes = True
            break
        else:
            print("Please review plan and confirm with 'yes' to continue...\n")
            user_input = input("Enter a value: ")

    return yes

def print_summary():

    create_success_count = len([r for r in response_list if r["operation"] == "create" and r["status"] == "success"])
    create_error_count = len([r for r in response_list if r["operation"] == "create" and r["status"] == "error"])

    update_success_count = len([r for r in response_list if r["operation"] == "update" and r["status"] == "success"])
    update_error_count = len([r for r in response_list if r["operation"] == "update" and r["status"] == "error"])

    print("="*70)
    print(str(create_success_count) + " out of " + str(create_success_count + create_error_count) + " dashboards created successfully")
    print(str(update_success_count) + " out of " + str(update_success_count + update_error_count) + " dashboards updated successfully")
    print("=" * 70)

    for r in response_list:
        print("\tFile Name: " + r["file_name"])
        print("\tDashboard Id: " + str(r["id"]))
        print("\tDashboard Name: " + r["name"])
        print("\tOperation: " + r["operation"])
        print("\tStatus: " + r["status"])
        if r["status"] == "error":
            print("\tError: " + r["error"])
        if r["operation"] == "create":
            print("\tNew File Name: " + r["new_file_name"])
        print("\t", end="")
        print("-" * 60)

def log_summary():
    create_success_count = len([r for r in response_list if r["operation"] == "create" and r["status"] == "success"])
    create_error_count = len([r for r in response_list if r["operation"] == "create" and r["status"] == "error"])

    update_success_count = len([r for r in response_list if r["operation"] == "update" and r["status"] == "success"])
    update_error_count = len([r for r in response_list if r["operation"] == "update" and r["status"] == "error"])

    logger.debug("=" * 70)
    logger.debug(str(create_success_count) + " out of " + str(
        create_success_count + create_error_count) + " dashboards created successfully")
    logger.debug(str(update_success_count) + " out of " + str(
        update_success_count + update_error_count) + " dashboards updated successfully")
    logger.debug("=" * 70)

    for r in response_list:
        logger.debug("\tFile Name: " + r["file_name"])
        logger.debug("\tDashboard Id: " + str(r["id"]))
        logger.debug("\tDashboard Name: " + r["name"])
        logger.debug("\tOperation: " + r["operation"])
        logger.debug("\tStatus: " + r["status"])
        if r["status"] == "error":
            logger.debug("\tError: " + r["error"])
        if r["operation"] == "create":
            logger.debug("\tNew File Name: " + r["new_file_name"])
        logger.debug("-" * 60)
