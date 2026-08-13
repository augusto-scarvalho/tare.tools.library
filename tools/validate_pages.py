#!/usr/bin/env python3
"""Fail closed when a generated SIGNAL projection is incomplete or leaks input."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from bs4 import BeautifulSoup

def validate(output: Path) -> list[str]:
 errors=[]
 if not (output/'index.html').is_file(): return ['missing site index']
 if not (output/'assets'/'signal.css').is_file(): errors.append('missing Signal stylesheet')
 for page in output.glob('p/*/index.html'):
  text=page.read_text(encoding='utf-8'); soup=BeautifulSoup(text,'html.parser')
  if soup.find('article',attrs={'data-tare-document':True}) is None: errors.append(f'{page}: missing canonical article')
  record=page.parent/'PROJECTION_RECORD.json'
  if not record.is_file(): errors.append(f'{page}: missing projection record'); continue
  data=json.loads(record.read_text(encoding='utf-8'))
  if not data.get('source_sha256') or not data.get('semantic_fingerprint'): errors.append(f'{record}: incomplete provenance')
  for tag in soup.find_all(['script','iframe','form']):
   if tag.name=='script' and tag.get('src')=='/assets/site.js': continue
   errors.append(f'{page}: active output element {tag.name}')
  for tag in soup.find_all(src=True):
   if tag['src'].startswith(('http://','https://','//')): errors.append(f'{page}: remote asset {tag["src"]}')
 return errors

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('output',type=Path); args=ap.parse_args(); errors=validate(args.output)
 print('PASS Pages validation' if not errors else '\n'.join('ERROR '+x for x in errors)); raise SystemExit(bool(errors))
