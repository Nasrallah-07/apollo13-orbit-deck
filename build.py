#!/usr/bin/env python3
"""Copy the standalone ORBIT-DECK page into a local distributable folder."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'orbit-deck.html'
OUT = ROOT / 'dist' / 'orbit-deck.html'

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f'Cannot find standalone app: {SOURCE}')
    html = SOURCE.read_text(encoding='utf-8')
    if '<!doctype html>' not in html.lower() or '<script>' not in html:
        raise ValueError(f'{SOURCE.name} does not look like a complete HTML app')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding='utf-8')
    print(f'built {OUT} ({len(html):,} bytes)')

if __name__ == '__main__':
    main()
