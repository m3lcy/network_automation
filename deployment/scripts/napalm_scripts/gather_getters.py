import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from tasks.napalm_tasks.gather_getters_tasks import gather_getters
from nornir_utils.plugins.functions import print_result

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

result = nr.run(
    task = gather_getters,
    timestamp = timestamp
)
print_result(result)