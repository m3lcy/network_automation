# Network Automation Platform 

This repository provides a modular network automation framework designed to safely manage
network device configurations. It supports both full golden configuration replacement and
incremental day-2 changes with built-in dry-run validation, side-by-side diffs, and automatic
rollback on config failure.

## Supported Features
• Full golden configuration replace with automatic rollback  
• Safe incremental configuration merges for day-2 operations  
• Dry-run mode with configuration diffs before deployment  
• Multi-vendor fact gathering and configuration backups using NAPALM  
• Secure credential retrieval via HashiCorp Vault

# Setup
Python>=3.12 required

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

# Core Scripts

```
scripts/nornir_scripts/gather_info.py     -(nornir_netmiko show commands)
scripts/nornir_scripts/config_tasks.py    -(nornir_netmiko quick command config)
scripts/nornir_napalm/gather_getters.py   -(napalm facts for multi-vendors)
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
python3 scripts/napalm_scripts/merge_config.py interfaces.j2 --dry-run --limit core-r1
```

## Run nornir_napalm full golden config replace + rollback on failure
```bash
python3 scripts/napalm_scripts/replace_config.py universal.j2 --commit --limit l3-sw-01
```

Can be modified at any time to fit workload needs.<br/>
All credential data is retrieved from HashiCorp Vault.

**TechStack**<br>
**Nornir**, **Netmiko**, **NAPALM**, **Jinja2**, **YAML**, **HashiCorp Vault**