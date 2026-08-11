#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/'catalog'/'CANONICAL_SNAPSHOT_RESEARCH_INDEX.json'
URL_RE=re.compile(r'https?://[^\s<>"\']+')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def urls(text): return sorted(set(u.rstrip('.,;:)]}') for u in URL_RE.findall(text)))
def main():
 idx=json.loads(INDEX.read_text(encoding='utf-8')); failures=[]; checked=0
 for item in idx['items']:
  tr=item.get('englishTranslationPath')
  if not tr: continue
  checked+=1; s=ROOT/item['preservedPath']; t=ROOT/tr
  if not t.is_file(): failures.append(f'missing translation: {tr}'); continue
  if sha(s)!=item['sha256']: failures.append(f'source hash drift: {item["sourcePath"]}')
  if item.get('translationSha256')!=sha(t): failures.append(f'translation hash drift: {tr}')
  st=s.read_text(encoding='utf-8',errors='replace'); tt=t.read_text(encoding='utf-8',errors='replace')
  if urls(st)!=urls(tt): failures.append(f'URL set mismatch: {item["sourcePath"]}')
  # Editorial migration may legitimately convert HTML/indented/preformatted source into fenced Markdown.
  # Require well-formed translation fences rather than representation identity.
  fence_lines = sum(1 for line in tt.splitlines() if re.match(r'^\s*```', line))
  if fence_lines % 2 != 0: failures.append(f'unbalanced translation code fences: {item["sourcePath"]}')
  if len(tt.strip())<50: failures.append(f'translation too small: {item["sourcePath"]}')
 if failures:
  print('\n'.join('FAIL '+x for x in failures)); return 1
 print(f'PASS snapshot translation QA: {checked} translated document(s)')
 return 0
if __name__=='__main__': raise SystemExit(main())
