import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

import argparse
from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from tasks.napalm_tasks.replace_config_tasks import replace_config
from nornir_utils.plugins.functions import print_result

parser = argparse.ArgumentParser(
    description = "Perform full config replace using Napalm + Nornir + golden Jinja2 templates"
)

parser.add_argument(
    "template_file",
    type = str,
    help = "Jinja2 template name inside golden_configs/templates/"
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--dry-run",
    action = "store_true",
    help = "Shpw diff only (default if neither flag is specified)"
)
group.add_argument(
    "--commit",
    action = "store_true",
    help = "Commit the full config replace to devices"
)

args = parser.parse_args()
dry_run_flag = not args.commit          # default

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

tempalte_path = Path("golden_configs/templates") / args.template_file
if not tempalte_path.exists():
    print(f"[ERROR] Golden template not found: {tempalte_path}")
    sys.exit(1)

result = nr.run(
    task = replace_config,
    template_file = args.template_file,
    timestamp = timestamp,
    dry_run = dry_run_flag
)
print_result(result)