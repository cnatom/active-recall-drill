#!/usr/bin/env python3
"""Check that every abbreviation used in a course page exists in 术语.json.

Usage: check_terms.py <course dir>            (术语.json + chapters/)
       check_terms.py <术语.json> <chapters dir>
Exit 1 and list the missing tokens when a page uses an abbreviation that has no
glossary entry. Node instance names (TOR-1, EOR-A, CE-2) and roman numerals are
ignored.
"""
import glob
import html
import json
import os
import re
import sys

NODE = re.compile(r'^(TOR|EOR|DCGW|CE|POD)-[A-Z0-9]+$|^I{1,3}$|^IV$')
TOKEN = re.compile(r'\b[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)*\b')


def visible_text(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return html.unescape(s)


def main():
    if len(sys.argv) == 2:
        root = sys.argv[1]
        terms_path = os.path.join(root, '术语.json')
        chapters = os.path.join(root, 'chapters')
        if not os.path.isdir(chapters):
            chapters = root
    elif len(sys.argv) == 3:
        terms_path, chapters = sys.argv[1], sys.argv[2]
    else:
        print(__doc__)
        return 2
    terms = {t['abbr'] for t in json.load(open(terms_path, encoding='utf-8'))['terms']}
    missing = {}
    for path in sorted(glob.glob(os.path.join(chapters, '**', '*.html'), recursive=True)):
        for tok in sorted(set(TOKEN.findall(visible_text(path)))):
            if tok in terms or NODE.match(tok):
                continue
            missing.setdefault(tok, []).append(os.path.basename(path))
    if not missing:
        print('all terms covered')
        return 0
    for tok, files in sorted(missing.items()):
        print(f'{tok}: {", ".join(files)}')
    print(f'\n{len(missing)} term(s) missing from 术语.json')
    return 1


if __name__ == '__main__':
    sys.exit(main())
