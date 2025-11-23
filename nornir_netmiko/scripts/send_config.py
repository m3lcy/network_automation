import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from nornir.tasks.config_tasks import send_config
from nornir_utils.plugins.functions import print_result

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

result = nr.run(
    task = send_config,
    timestamp = timestamp
)
print_result(result)