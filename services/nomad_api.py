import nomad
import logging, os
from dotenv import load_dotenv
from typing import Optional
from time import sleep
from sys import exit

logging.basicConfig(format='%(asctime)s: %(levelname)s : %(message)s', level=logging.INFO)


class TextColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_up():

    settings: Optional[dict] = {}
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    nomad_server = os.environ.get('NOMAD_SERVER')
    nomad_token = os.environ.get('NOMAD_TOKEN')
    nomad_namespace = os.environ.get('NOMAD_NAMESPACE')
    nomad_region = os.environ.get('NOMAD_REGION')

    nomad_connector = nomad.Nomad(host=nomad_server, token=nomad_token, secure=False, timeout=5,
                                  verify=False, namespace=nomad_namespace, region=nomad_region)
    settings['nomad_connector'] = nomad_connector
    settings['sleep_time'] = int(os.environ.get('SLEEP_TIME'))
    settings['nomad_deployment_timeout'] = int(os.environ.get('NOMAD_DEPLOYMENT_TIMEOUT'))

    return settings


def make_json_file_list(hcl_file_list, nomad_connector) -> Optional[list]:
    """Make a file json list"""

    file_json_list: Optional[list] = []

    print(f'{TextColor.ENDC}\nPrepare to make a JSON list\n')

    for file in hcl_file_list:
        try:
            json = nomad_connector.jobs.parse(file)
            file_json_list.append({'Job': json})
            print(f'{TextColor.OKGREEN}Job ' + json['ID'] + ' has been added to a queue')

        except nomad.api.exceptions.BadRequestNomadException as err:
            logging.error(err.nomad_resp.reason)
            logging.error(err.nomad_resp.text)

    return file_json_list


def plan_nomad_job(json_list, nomad_connector) -> None:
    """Plan the Nomad jobs"""

    print(f'{TextColor.ENDC}\nPlan Nomad jobs')

    for j in json_list:
        try:
            plan_result = nomad_connector.job.plan_job(j['Job']['ID'], j)
            print(f'{TextColor.ENDC}\nPlan the ' + j['Job']['ID'] + ' job')

            groups_update_data = dict(plan_result['Annotations']['DesiredTGUpdates']).keys()

            for annotation in groups_update_data:
                print('Group:' + annotation + ' - Destructive update: ' + str(
                    plan_result['Annotations']['DesiredTGUpdates'][annotation]['DestructiveUpdate']))

            if plan_result['Warnings']:
                print(f'{TextColor.WARNING}')
                print(plan_result['Warnings'])

        except nomad.api.exceptions.BaseNomadException as err:
            logging.error(err.nomad_resp.reason)
            logging.error(err.nomad_resp.text)


def nomad_deployment_status(nomad_connector, job_id):
    try:
        return nomad_connector.job.get_deployment(job_id)
    except nomad.api.exceptions.BaseNomadException as err:
        print(err.nomad_resp.reason)
        print(err.nomad_resp.text)


def get_deployment_status(nomad_connector, json_list, sleep_time, nomad_deployment_timeout):
    """Making of a deployment status dict"""

    ticker = 0
    deployment_status_dict: Optional[dict] = {}

    # Making of an initial deployment dict
    for json in json_list:
        deployment_status_dict[json["Job"]["ID"]] = {}
        deployment_status_dict[json["Job"]["ID"]]["Summary"] = "null"
        deployment_status_dict[json["Job"]["ID"]]["DesiredCanaries"] = {}

    while ticker <= nomad_deployment_timeout:
        sleep(sleep_time)
        for json in json_list:
            deployment_status_dict[json["Job"]["ID"]]["Summary"] = \
                nomad_deployment_status(nomad_connector, json["Job"]["ID"])
            deployment_status = deployment_status_dict[json["Job"]["ID"]]["Summary"]["Status"]
            if deployment_status == 'successful':
                print(f'{TextColor.OKGREEN}' + json['Job']['ID'] + ' deployment status: ' + deployment_status)
            else:
                print(f'{TextColor.WARNING}' + json['Job']['ID'] + ' deployment status: ' + deployment_status)

        if all(deployment_status_dict[deployment]["Summary"]["Status"] == "successful" for deployment in
               deployment_status_dict):
            print("Deployments are successful")
            break

        ticker = ticker + sleep_time

    if ticker >= nomad_deployment_timeout:
        print(f'{TextColor.FAIL}Deployments are failed')
        exit(os.EX_SOFTWARE)


def run_nomad_job(nomad_connector, json_list):
    """Run a nomad job"""

    print(f'{TextColor.ENDC}\nRun Nomad jobs')

    for j in json_list:
        try:
            run_result = nomad_connector.job.register_job(j['Job']['ID'], j)
            if run_result['Warnings']:
                print(f'{TextColor.ENDC}' + j["Job"]["ID"])
                print(f'{TextColor.WARNING}' + run_result["Warnings"])

        except nomad.api.exceptions.BaseNomadException as err:
            logging.error(err.nomad_resp.reason)
            logging.error(err.nomad_resp.text)


