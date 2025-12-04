# Network Automation Platform 
Nornir + Netmiko + NAPALM + Jinja2 + YAML + HashiCorp Vault

Python>=3.12 required

# Setup

## Clone and enter
```bash
git clone git@github.com:m3lcy/network_automation.git
cd network_automation/deployment
```

## (Optional) Create a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
```

## Install required Python packages
```bash
pip install -r requirements.txt
```

# Key Scripts

```
scripts/nornir_scripts/gather_info.py     -(nornir_netmiko show commands)
scripts/nornir_scripts/config_tasks.py    -(nornir_netmiko quick command config)
scripts/nornir_napalm/gather_getters.py      -(napalm facts for multi-vendors)
scripts/nornir_napalm/backup_config.py    -(backup running configs)
scripts/nornir_napalm/merge_config.py     -(safe incremental changes using config snippets)
scripts/nornir_napalm/replace_config.py   -(full config replace + rollback on failure) 
```

# Optional flags

## Dry-run - shows diff only (default flag if neither flags are specified)
```bash 
--dry-run
```

## Commit - push changes
```bash
--commit
```

## Limit - target specific hosts from inventory
```bash
--limit core-r1
```

# Usage

## Run nornir_netmiko show commands
```bash
python3 scripts/nornir_scripts/gather_info.py --limit access-sw-02
```

## Run nornir_napalm merge config
```bash
python3 scripts/napalm_scripts/merge_config.py interfaces_config.j2 --commit --limit core-r1
```

## Run nornir_napalm full golden config replace + rollback on failure
```bash
python3 scripts/napalm_scripts/replace_config.py universal.j2 --dry-run --limit l3-sw-01
```

Can be modified at any time to fit workload needs
All credential data is retrieved from HashiCorp Vault