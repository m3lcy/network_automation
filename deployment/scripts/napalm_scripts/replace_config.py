import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

import argparse
from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from modules.runner import get_common_parser, run_task
from tasks.napalm_tasks.replace_config_tasks import replace_config
from nornir_utils.plugins.functions import print_result

parser = get_common_parser()
args = parser.parse_args()

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

BASE_DIR = Path(__file__).resolve().parents[2]  
template_path = BASE_DIR / "templates" / args.template
if not template_path.exists():
    print(f"[ERROR] Golden template not found: {template_path}")
    raise sys.exit(1)

run_task(
    nr = nr,
    task_func = replace_config,   
    template_file = args.template,
    commit = args.commit,
    limit = args.limit,
    pass_dry_run = True
)