import yaml
import subprocess
import os

with open('master_conf.yaml', 'r') as f:
    conf = yaml.load(f, Loader=yaml.Loader)

def try_dir(dir: str, match: str):
    confs = os.listdir(dir)
    for name in confs:
        split = name.split('.')
        basename = split[0]
        if basename == match.lower():
            return f'{dir}/{name}'

for item in conf['load']:
    item = try_dir('confs', item) or try_dir('example_confs', item)
    subprocess.run(['python', 'main.py', f'{item}'])