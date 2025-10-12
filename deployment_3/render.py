from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import logging
import os
import yaml

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

os.makedirs('logs', exist_ok = True)
os.makedirs('outputs', exist_ok = True)

logging.basicConfig(
    filename = 'logs/device_access.log',
    level = logging.INFO,
    format = '%(asctime)s = %(levelname)s - %(message)s'
)

try:
    with open('data/vlans.yml') as f:
        vlans = yaml.safe_load(f)['vlans']
        logging.info(f"Loaded {len(vlans)} VLANS successfully.")
except Exception as e:
    logging.error(f"Failed to load VLANS: {e}")
    raise

try:
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templates/template.j2')
    output = template.render(vlans=vlans)
    logging.info("Template rendered successfully.")
except Exception as e:
    logging.error(f"Template rendering failed: {e}")

print(output)

filename = f"outputs/generated_vlan_config.cfg"

try:
    with open('outputs/generated_vlan_config.cfg', 'w') as f:
        f.write(output)
    os.chmod(filename, 0o444)
    logging.info(f"Configuration saved to {filename}")

except Exception as e:
    logging.error(f"Failed to write output: {e}")
    raise