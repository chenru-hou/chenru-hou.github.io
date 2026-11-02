"""Package the static site as a private, self-contained HTML preview."""
from pathlib import Path
import json, zipfile
r=Path(__file__).resolve().parents[1];out=r/'dist';css=(out/'assets/style.css').read_text()
pages={p.name:p.read_text().replace('<link rel="stylesheet" href="assets/style.css">','<style>'+css+'</style>') for p in out.glob('*.html')}
s=pages['index.html']
preview='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chenru Hou — Private preview</title><style>'+css+'</style></head><body>'+s.split('<body>',1)[1].split('</body>',1)[0]+'<script>const pages='+json.dumps(pages,ensure_ascii=False).replace('<','\\u003c')+';document.addEventListener("click",function(e){const a=e.target.closest("a");if(!a)return;const page=pages[a.getAttribute("href")];if(page){e.preventDefault();document.body.innerHTML=new DOMParser().parseFromString(page,"text/html").body.innerHTML;window.scrollTo(0,0);}});</script></body></html>'
(r/'private-preview.html').write_text(preview)
with zipfile.ZipFile(r/'website-preview.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out))
