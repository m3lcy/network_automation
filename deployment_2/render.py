from jinja2 import Environment, FileSystemLoader
import yaml

with open('vlans.yml') as f:
    vlans = yaml.safe_load(f)['vlan']

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.j2')

output = template.render(vlans=vlans)

print(output)
with open('generated_vlan_config.cfg', 'w') as f:
    f.write(output)