from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
 def __init__(self): super().__init__(); self.links=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for k in ('href','src'):
   if k in d: self.links.append(d[k])
errors=[]; checked=0
for html in ROOT.rglob('*.html'):
 p=P();
 try:p.feed(html.read_text(encoding='utf-8',errors='ignore'))
 except Exception as e: errors.append(f'{html.relative_to(ROOT)} 無法讀取: {e}'); continue
 for raw in p.links:
  if not raw or raw.startswith(('#','mailto:','tel:','javascript:','data:','http://','https://')): continue
  path=unquote(urlparse(raw).path)
  if path.startswith('/math/'):
   target=ROOT/path[len('/math/'):]
  elif path.startswith('/'):
   continue
  else: target=(html.parent/path).resolve()
  if raw.endswith('/') or target.is_dir(): target=target/'index.html'
  checked+=1
  if not target.exists(): errors.append(f'{html.relative_to(ROOT)} -> {raw}')
print(f'已檢查 {checked} 個本機連結。')
if errors:
 print('\n發現可能失效的連結：')
 for x in errors: print(' -',x)
 raise SystemExit(1)
print('全部通過，沒有發現 404 路徑。')
