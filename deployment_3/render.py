from jinja2 import Environment, FileSystemLoader
import yaml

with open('vlans.yml') as f:
    vlans = yaml.safe_load(f)['vlans']

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('format.j2')

output = template.render(vlans=vlans)

print(output)
with open('generated_vlan_config.cfg', 'r') as f:
    f.write(output)