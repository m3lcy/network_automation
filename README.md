# Network Automation Platform 

This repository provides a modular network automation framework designed to safely manage 
network device configurations, enabling consistent, scalable and error-resistant operations. Built on **Nornir** with official plugins from:

- [Nornir](https://nornir.readthedocs.io/)
- [NAPALM](https://napalm.readthedocs.io/en/latest/support/)
- [Netmiko](https://ktbyers.github.io/netmiko/)
- [nornir_napalm](https://github.com/nornir-automation/nornir_napalm)
- [nornir_netmiko](https://github.com/ktbyers/nornir_netmiko)


## Supported Features

This framework provides a safe, modular and auditable way to manage:<br>
- Cisco (IOS, IOS-XE, IOS-XR, NX-OS) 
- Juniper (Junos OS)
- Arista (EOS)
- Palo Alto Networks (PanOS)

### Configuration Management
- **Full golden configuration replacement**: Render and replace entire running-config from `templates/universal.j2` (or other full templates) with automatic rollback on failure
- **Safe incremental (day-2) merges**: Apply targeted snippets using Jinja2 templates + per-device data from `templates/`
- **Dry-run mode by default**: Preview rendered config, NAPALM-generated diff, or command list without making changes `--dry-run`
- **Commit control**: Explicit `--commit` required to push changes; rollback on error for replace operations
- **Timestamped golden configs**: Rendered templates saved in `golden_configs/rendered/` for audit/tracking

### Observability & Backup
- Running-config backups via NAPALM (saved to `outputs/backups/`)
- Structured fact gathering (NAPALM getters: interfaces, BGP, OSPF, etc.)
- Ad-hoc show command collection via Netmiko (e.g. `show ip interface brief`, `show ip route`, `show cdp neighbors`, etc.) with  output saved as YAML
- Post-change verification (e.g. `show run` capture after config push)

### Templating & Data Handling
- Jinja2 templating for both full configs (`universal.j2`) and snippets (e.g. `interfaces.j2`, `ospf.j2`, `vlans.j2`)
- Per-host/per-snippet variable data
- Strict Undefined handling to catch missing variables
- Global defaults + device-specific overrides via inventory YAML

### Execution & Safety
- Host/group limiting: `--limit core-r1`, `--limit group:l3_switches`, `--limit access-sw`
- Secure credential loading from HashiCorp Vault
- Consistent logging (`logs/device_access.log`) and output organization
- Modular design makes it easy to add new tasks, templates or snippets

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

| scripts/                                        | Description                                             | Backend   |
|:-----------------------------------------------:|:-------------------------------------------------------:|:----------:|
| `nornir_napalm_scripts/replace_config.py`       | Full golden configuration replace + rollback on failure | NAPALM    |
| `nornir_napalm_scripts/merge_config.py`         | Safe incremental changes using config snippets          | NAPALM    |
| `nornir_napalm_scripts/backup_config.py`        | Backup running-config                                   | NAPALM    |
| `nornir_napalm_scripts/gather_getters.py`       | Structured facts gathering (interfaces, BGP...)         | NAPALM    |
| `nornir_netmiko_scripts/gather_info.py`                 | Custom multi-command show collection                    | Netmiko   |
| `nornir_netmiko_scripts/send_config.py`                 | Send global + custom config commands                    | Netmiko   |

# Flags

`--dry-run` Default behavior (preview only) <br>
`--commit` Apply changes to devices <br>
`--limit` Target specific hosts/groups <br>
e.g. `--limit core-r1` `--limit group:l3_switches` `--limit access-sw`

# Usage Examples

```bash
# Dry-run a merge
python scripts/nornir_napalm_scripts/merge_config.py interfaces.j2 --limit l3-sw-01

# Full replace with commit
python scripts/nornir_napalm_scripts/replace_config.py universal.j2 --commit --limit core-r1

# Backup a group of devices
python scripts/nornir_napalm_scripts/backup_config.py --limit group: access_switches

# Gather detailed info
python scripts/nornir_netmiko_scripts/gather_info.py --limit "access-sw-01"
```

**TechStack**<br>
**Python**, **nornir_napalm**, **nornir_netmiko**, **Jinja2**, **YAML**, **HashiCorp Vault**