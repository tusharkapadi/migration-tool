import sys
import os
import logging

from dashboard.export_dashboard import ExportDashboard as exp_dash
from dashboard.import_dashboard import ImportDashboard as imp_dash

logger = logging.getLogger(__name__)

#TODO: remove trailing spaces from values for inputs

def migration_tool():

    #parse input
    operation, resource, endpoint_url, api_token, fetch_all, ids, names, output_folder, input_folder, plan, yes, log_level, log_folder = parseInput()

    #set logging
    log_level_dict = {"NOTSET": 0, "DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40, "CRITICAL": 50}

    logging.basicConfig(level=log_level_dict.setdefault(log_level.upper(), 20),
                        filename=log_folder + 'sysdig_migration_tool.log',
                        filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("Initializing Sysdig Migration Script.")
    try:
        if operation.lower() == "export":
            dash = exp_dash(endpoint_url, api_token, fetch_all, ids, names, output_folder)
            dash.export_dashboard()
        elif operation.lower() == "import":
            dash = imp_dash(endpoint_url, api_token, input_folder, plan, yes)
            dash.import_dashboard()
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)



def parseInput():

    logger.info(sys.argv)

    help_msg = 'usage: %s dashboard export endpoint_url=<Sysdig Monitor End Point URL> api_token=<Sysdig Monitor API Token> ids=dashboard_ids names=dashboard_names'
    if len(sys.argv) < 4:
        print("")
        print((
                'usage: %s dashboard export endpoint_url=<Sysdig Monitor End Point URL> api_token=<Sysdig Monitor API Token> ids=dashboard_ids names=dashboard_names' %
                sys.argv[0]))
        sys.exit(1)

    operation = sys.argv[1]
    resource = sys.argv[2]
    fetch_all = False
    ids = ""
    names = ""
    output_folder = "./json/"
    input_folder = ""
    plan = False
    yes = False
    log_level = "info"
    log_folder = "logs/"

    endpoint_url = os.getenv('SYSDIG_ENDPOINT_URL')
    api_token = os.getenv('SYSDIG_API_TOKEN')

    for arg in sys.argv:
        k = arg.split("=")
        if k[0] == "--all":
            fetch_all = True
        elif k[0] == "--ids":
            ids = k[1]
        elif k[0] == "--names":
            names = k[1]
        elif k[0] == "--output_folder":
            output_folder = k[1]
        elif k[0] == "--input_folder":
            input_folder = k[1]
        elif k[0] == "--plan":
            plan = True
        elif k[0] == "--yes":
            yes = True
        elif k[0] == "--log_level":
            log_level = k[1]
        elif k[0] == "--log_folder":
            log_folder = k[1]

    # TODO: add contion to check for log level value
    # TODO: make sure to add / in the end for all folders - check if folders ends with "/"

    return operation, resource, endpoint_url, api_token, fetch_all, ids, names, output_folder, input_folder, plan, yes, log_level, log_folder


if __name__ == '__main__':
    migration_tool()
