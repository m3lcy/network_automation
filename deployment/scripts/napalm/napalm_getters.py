from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.task import Result
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.logging_utils import setup_logging
from modules.vault_utils import init_vault
from modules.nornir_init import init_nornir
from modules.credentials import load_credentials
from tasks.napalm.napalm_getters_tasks import napalm_getters
from nornir_utils.plugins.functions import print_result

timestamp = setup_logging()
vault_client = init_vault()
nr = init_nornir()
load_credentials(nr, vault_client)

result = nr.run(
    task = napalm_getters,
    timestamp = timestamp
)
print_result(result)