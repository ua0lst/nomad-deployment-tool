from services.nomad_api import set_up, make_json_file_list, plan_nomad_job, get_deployment_status, run_nomad_job
from services.make_hcl_file_list import make_hcl_file_list
from services.parser import set_up_parser
from time import sleep


n_conn = set_up()['nomad_connector']
sleep_time = set_up()['sleep_time']
nomad_deployment_timeout = set_up()['nomad_deployment_timeout']


def deploy():
    print(f'Test vars')

    jobs = n_conn.jobs.get_jobs()

    for job in jobs:
        print(job['ID'])


if __name__ == '__main__':

    arguments = set_up_parser()

    if arguments.upgrade_type == 'rolling':
        hcl_file_list = make_hcl_file_list(arguments)
        json_list = make_json_file_list(hcl_file_list, n_conn)
        plan_nomad_job(json_list, n_conn)
        run_nomad_job(n_conn, json_list)
        sleep(5)
        get_deployment_status(n_conn, json_list, sleep_time, nomad_deployment_timeout)
    else:
        print('Canary deployments will be here')

    # deploy()
