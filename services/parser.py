from argparse import ArgumentParser, Namespace
from typing import Optional


def set_up_parser() -> Optional[Namespace]:
    """Set up a parser"""

    parser = ArgumentParser(description='CI arguments')
    parser.add_argument('-job_hcl', dest='job_hcl', action="append", help='HCL job file')
    parser.add_argument('-upgrade_type', dest='upgrade_type', action="store", help='Upgrade type to deploy')
    args = parser.parse_args()

    return args
