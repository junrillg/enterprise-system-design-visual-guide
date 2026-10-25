"""Validate reference links, diagram sources, and concept coverage."""
from pathlib import Path
from urllib.parse import urlparse
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
errors = []
markdown = list(ROOT.glob('*.md'))
for file in markdown:
    text = file.read_text()
    if text.count('<details>') != text.count('</details>'):
        errors.append(f'{file.name}: unbalanced details')
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
        target = target.split('#', 1)[0]
        if target and not urlparse(target).scheme and not (ROOT / target).exists():
            errors.append(f'{file.name}: missing {target}')
for file in ROOT.glob('*.svg'):
    tree = ET.parse(file)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    if tree.find('s:title', ns) is None or tree.find('s:desc', ns) is None:
        errors.append(f'{file.name}: missing accessible description')
    if not file.with_suffix('.mmd').exists():
        errors.append(f'{file.name}: missing Mermaid source')
for number in range(1, 8):
    matches = list(ROOT.glob(f'{number:02d}-*.md'))
    if len(matches) != 1:
        errors.append(f'concept {number}: expected one reference file')
        continue
    for required in ['<details>', 'Design position', '**Boundary:**', 'https://']:
        if required not in matches[0].read_text():
            errors.append(f'{matches[0].name}: missing {required}')
questions = (ROOT / '10-design-questions.md').read_text().count('<details>')
if questions != 40:
    errors.append(f'Expected 40 design questions, found {questions}')
refs = (ROOT / '11-research-register.md').read_text()
if len(re.findall(r'^\*\*S\d{2}', refs, flags=re.M)) != 33:
    errors.append('Expected 33 reference entries')
if len(list(ROOT.glob('*.svg'))) != 11:
    errors.append('Expected 11 diagrams')
if not (ROOT / 'START_HERE.html').exists():
    errors.append('Missing offline reference')
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: local links, 7 concepts, 11 diagrams, 40 design questions, 33 sources')
