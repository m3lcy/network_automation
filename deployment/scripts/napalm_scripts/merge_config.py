import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
import argparse

from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from tasks.napalm_tasks.merge_config_tasks import merge_config 
from nornir_utils.plugins.functions import print_result

parser = argparse.ArgumentParser(
    description = "Merge a configauration snippet to devices using Napalm + Nornir."
)
parser.add_argument(
    "snippet_file",
    type = str,
    help = "Name of the config snippet inside deployment/config_snippets"
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--dry-run",
    action = "store_true",
    help = "Perform a dry-run merge (default if neither flag is specified)"
)
group.add_argument(
    "--commit",
    action = "store_true",
    help = "Commit the configuration merge to devices"
)

args = parser.parse_args()

# default 
dry_run_flag = not args.commit

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

snippet_path = Path("config_snippets") / args.snippet_file
if not snippet_path.exists():
    print(f"[ERROR] Snippet file not found: {snippet_path}")
    sys.exit(1)

result = nr.run(
    task = merge_config,
    snippet_file = args.snippet_file,
    timestamp = timestamp,
    dry_run = dry_run_flag
)
print_result(result)