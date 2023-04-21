#!/bin/bash
# -*- coding: utf-8 -*-
"""Script for automatically updating the `CHANGELOG.md` based on the commits since the latest release tag."""
from pathlib import Path
import re
import subprocess

with Path('src/aiida_quantumespresso/__init__.py').open('r', encoding='utf8') as handle:
    version = re.search(r"__version__ = '(?P<version_number>\d+.+)'", handle.read()).groupdict()['version_number']

tags = subprocess.run(['git', 'tag'], capture_output=True, check=False).stdout

tag_pattern = re.compile(r'(v\d\.\d\.\d)\n')
tags = tags.decode()

latest_tag = tag_pattern.findall(tags)[-1]

comm = f'git log --pretty=format:%s {latest_tag}..origin/main'

commits = subprocess.run(
    f'git log --pretty=format:%s {latest_tag}..origin/main'.split(), capture_output=True, check=False
).stdout
commits = commits.decode()

pr_pattern = re.compile(r'\(\S(?P<pr_number>\d+)\)')

for pr_match in pr_pattern.finditer(commits):
    pr_number = pr_match.groupdict()['pr_number']
    commits = commits.replace(
        fr'(#{pr_number})', f'[[#{pr_number}](https://github.com/aiidateam/aiida-quantumespresso/pull/{pr_number})]'
    )

changelog_message = f'## v{version}\n'

for commit_title in commits.split('\n'):
    changelog_message += f'\n* {commit_title}'

with Path('CHANGELOG.md').open('r', encoding='utf8') as handle:
    current_changelog = handle.read()

if str(version) not in current_changelog:
    with Path('CHANGELOG.md').open('w', encoding='utf8') as handle:
        handle.write(changelog_message + '\n\n' + current_changelog)
else:
    raise ValueError('Current version already in `CHANGELOG.md`.')
