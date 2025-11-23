import logging

def load_credentials(nr, vault_client):
    for host in nr.inventory.hosts.values():
        try:
            path = f"network/devices/{host.name}"
            response = vault_client.secrets.kv.read_secret_version(path = path)

            data = response["data"]["data"]
            host.username = data.get("username", host.username)
            host.password = data["login_password"]
            host.data["secret"] = data["enable_secret"]

            logging.info(f"Loaded vault credentials for {host.name} ({host.hostname}) from Vault")

        except Exception as e:
            logging.error(f"Error retrieving secrets for {host.name} ({host.hostname}) from Vault. Error: {e}")
            