import pandas as pd
import subprocess

from pathlib import Path


def get_checksum(f):
    cmd = f'sha256sum {f}'
    res = subprocess.check_output(cmd, shell=True).decode().strip()
    return [x.strip() for x in res.split(' ', 1)]

checksumsfile = Path('data/checksums.txt')
checksums = {}
pwd = Path('./')
with open(checksumsfile) as fh:
    for line in fh.readlines():
        sha256, p = [x.strip() for x in line.split(' ', 1)]
        p = Path(p).relative_to(pwd)
        checksums[p] = sha256

for f in Path('rapporten').rglob('*'):
    if not f.is_file():
        continue

    if f not in checksums:
        print(f'Adding checksum for {f}')

    sha256, p = get_checksum(f)
    p = Path(p).relative_to(pwd)
    checksums[p] = sha256

with open(checksumsfile, 'w') as fh:
    for k in sorted(checksums.keys()):
        fh.write(f'{checksums[k]} {k}')
    

df = pd.read_csv('data/meta.csv')
df = df.sort_values(['woonplaats', 'straat', 'huisnummer'])

df['rapport_sha256'] = df['rapport'].apply(lambda x: checksums[Path(x)])
df['rapport'] = df['rapport'].apply(lambda x: f'[{Path(x).name}]({x})')
df['funda'] = df['funda'].apply(lambda x: f'[Funda]({x})')
df['adres'] = df[['straat', 'huisnummer', 'woonplaats']].apply(lambda x: f'{x.iloc[0]} {x.iloc[1]}, {x.iloc[2]}', axis=1)
df = df[[df.columns[-1], *df.columns[:-1]]]

dropcols = ['woonplaats', 'straat', 'huisnummer']
df = df.drop(columns=dropcols)

table = df.to_markdown(index=False)

with open('_templates/page.tpl') as fh:
    page = fh.read()

page = page.replace('{{TABLE}}', table)

with open('REGISTER.md', 'w') as fh:
    fh.write(page)
