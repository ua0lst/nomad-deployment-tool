import logging
from argparse import ArgumentParser, Namespace
from os.path import isfile
from typing import Optional


logging.basicConfig(format='%(asctime)s: %(levelname)s : %(message)s', level=logging.INFO)


def make_hcl_file_list(arguments) -> Optional[list]:
    """Make a JSON from the hcl job file"""
    args = arguments
    file_list: Optional[list] = _read_job_file(args.job_hcl)
    print('Make a hcl file list has been completed')

    return file_list


def _read_job_file(files) -> Optional[list]:
    """Make a file list"""

    file_list: Optional[list] = []

    for f in files:

        if isfile(f) is False:
            logging.error('File: ' + f + 'not found')
        else:
            file_obj = open(f)
            string_from_file = file_obj.read()
            file_obj.close()
            file_list.append(string_from_file)

    return file_list

