import signal
import yaml
import subprocess
import os
import sys

with open('master_conf.yaml', 'r') as f:
    conf = yaml.load(f, Loader=yaml.Loader)

def try_dir(dir: str, match: str):
    confs = os.listdir(dir)
    for name in confs:
        split = name.split('.')
        basename = split[0]
        if basename == match.lower():
            return f'{dir}/{name}'

procs: list[subprocess.Popen] = []
for item in conf['load']:
    item = try_dir('confs', item) or try_dir('example_confs', item)
    procs.append(subprocess.Popen(executable=sys.executable, args=['python', 'main.py', f'{item}']))

while True:
    died = 0
    for proc in procs:
        if died >= len(procs):
            break
        if proc.poll():
            died += 1