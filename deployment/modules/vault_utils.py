import hvac 
import os

def init_vault():
    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")

    if not vault_addr or not vault_token:
        raise EnvironmentError("Vault environment variables VAULT_ADDR or VAULT_TOKEN not set.")
    
    vault_client = hvac.Client(url = vault_addr, token = vault_token)

    if not vault_client.is_authenticated():
        raise ConnectionError("Unable to authenticate to Vault. Check vault token or address.")

    return vault_client