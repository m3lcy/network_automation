import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

import argparse
from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from modules.runner import get_common_parser, run_task
from tasks.napalm_tasks.gather_getters_tasks import gather_getters
from nornir_utils.plugins.functions import print_result

parser = get_common_parser()
args = parser.parse_args()

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

run_task(
    nr = nr,
    task_func = gather_getters,
    timestamp = timestamp,
    commit = args.commit,
    limit = args.limit,
    pass_dry_run = False
)