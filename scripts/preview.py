"""Package a private preview with inline editing; run build.py first."""
from pathlib import Path
import json, zipfile
root = Path(__file__).resolve().parents[1]
out = root / 'dist'
css = (out / 'assets/style.css').read_text()
pages = {p.name: p.read_text() for p in out.glob('*.html')}
data = {'profile': json.loads((root/'content/profile.json').read_text()), 'publications': json.loads((root/'content/publications.json').read_text())}
def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')
preview = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chenru Hou — Editable private preview</title><style>'''+css+'</style><style>'+(root/'preview/editor.css').read_text()+'''</style></head><body>
<div id="preview-editor" lang="zh-CN"><div class="editor-actions"><strong>私有预览</strong>
<button id="edit-toggle" aria-pressed="false">开启编辑</button><button id="edit-undo" disabled>撤销</button><button id="edit-contact">联系方式</button><button id="edit-save">保存可编辑预览</button><button id="edit-export">导出内容</button><button id="edit-import">导入内容</button><input id="edit-file" type="file" accept="application/json,.json" hidden></div>
<p id="edit-status" role="status" aria-live="polite">开启编辑后，点击文字即可修改。保存预览可保留修改；不会自动同步 GitHub。</p></div>
<div id="preview-root"></div>
<dialog id="contact-dialog" lang="zh-CN"><form method="dialog"><h2>联系方式</h2><div id="contact-fields"></div><div class="editor-actions"><button value="cancel" formnovalidate>取消</button><button value="save">保存修改</button></div></form></dialog>
<script id="preview-pages" type="application/json">'''+safe_json(pages)+'''</script><script id="preview-data" type="application/json">'''+safe_json(data)+'</script><script>'+(root/'preview/editor.js').read_text()+'</script></body></html>'
(root/'private-preview.html').write_text(preview)
with zipfile.ZipFile(root/'website-preview.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
        if p.is_file(): z.write(p, p.relative_to(out))
