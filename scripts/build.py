"""Dependency-free static site generator. Run: python3 scripts/build.py."""
import html, json, re, shutil
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'assets', OUT / 'assets')
profile = json.loads((ROOT / 'content/profile.json').read_text())
pubs = json.loads((ROOT / 'content/publications.json').read_text())
def esc(value): return html.escape(str(value), quote=True)
def link(item):
    url = item['url']
    if not url.startswith(('https://', 'http://', 'mailto:')): raise ValueError('Unsupported link URL')
    return f'<a href="{esc(url)}">{esc(item["label"])} ↗</a>'
def layout(title, current, content, prefix=''):
    nav = ''.join(f'<a href="{prefix}{file}"'+(' aria-current="page"' if current == key else '')+f'>{label}</a>' for key,file,label in [('home','index.html','Home'),('publications','publications.html','Publications'),('blog','blog.html','Blog')])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{esc(profile['intro'])}"><title>{esc(title)} · {esc(profile['name'])}</title><link rel="stylesheet" href="{prefix}assets/style.css"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='%23416950'/%3E%3C/svg%3E"></head><body><a class="skip" href="#main">跳到正文</a><div class="shell"><header><a class="brand" href="{prefix}index.html"><i></i>{esc(profile['name'])}</a><nav aria-label="主导航">{nav}</nav></header><main id="main">{content}</main><footer><span>© {date.today().year} {esc(profile['name'])}</span><span class="footer-mark">RESEARCH · NOTES · IDEAS</span></footer></div></body></html>'''
def write(path, text):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
def pub_html(p):
    return f'''<article class="pub"><div class="year">{esc(p['year'])}</div><div><span class="type">{esc(p['type'])}</span><h3>{esc(p['title'])}</h3><p>{esc(p['authors'])}</p><p class="venue">{esc(p['venue'])}</p>{'<p>'+esc(p['note'])+'</p>' if p.get('note') else ''}<div class="pub-links">{''.join(link(i) for i in p.get('links', []))}</div></div></article>'''
def inline(text):
    text = esc(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', r'<a href="\2">\1</a>', text)
def markdown(text):
    parts, paragraph, listing = [], [], []
    def flush():
        if paragraph: parts.append('<p>'+inline(' '.join(paragraph))+'</p>'); paragraph.clear()
        if listing: parts.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in listing)+'</ul>'); listing.clear()
    for line in text.splitlines():
        if not line.strip(): flush()
        elif line.startswith('#'):
            flush(); match = re.match(r'^(#{1,6}) (.*)$', line)
            if match: parts.append(f'<h{len(match[1])}>{inline(match[2])}</h{len(match[1])}>')
            else: paragraph.append(line)
        elif line.startswith('- '):
            if paragraph: flush()
            listing.append(line[2:])
        else:
            if listing: flush()
            paragraph.append(line)
    flush()
    return ''.join(parts)
posts=[]
for path in (ROOT/'content/posts').glob('*.md'):
    if not re.fullmatch(r'[a-z0-9-]+', path.stem): raise ValueError('Use lowercase ASCII filenames')
    _, front, body = path.read_text().split('---', 2)
    data = dict(line.split(': ', 1) for line in front.strip().splitlines())
    date.fromisoformat(data['date'])
    data.update(body=body, slug=path.stem)
    posts.append(data)
posts.sort(key=lambda p:p['date'], reverse=True)
def post_row(p):
    return f'''<a class="blog-row" href="posts/{esc(p['slug'])}.html"><time class="date" datetime="{esc(p['date'])}">{esc(p['date'])}</time><div><span class="eyebrow">{esc(p['tag'])}</span><h2>{esc(p['title'])}</h2><p>{esc(p['summary'])}</p></div><span class="arrow" aria-hidden="true">↗</span></a>'''
social=''.join(link(i) for i in profile['links'])
if profile.get('email'): social=link({'label':'Email','url':'mailto:'+profile['email']})+social
portrait='''<div class="portrait" role="img" aria-label="个人照片占位图"><svg viewBox="0 0 160 180" fill="none" aria-hidden="true"><circle cx="80" cy="57" r="32" stroke="currentColor" stroke-width="1.2"/><path d="M18 166c0-45 24-65 62-65s62 20 62 65" stroke="currentColor" stroke-width="1.2"/><circle cx="80" cy="84" r="69" stroke="currentColor" stroke-opacity=".2"/><path d="M0 166h160" stroke="currentColor" stroke-opacity=".4"/></svg><span>YOUR PORTRAIT</span></div>'''
home=f'''<section class="hero"><div><div class="eyebrow">A PERSONAL ACADEMIC SPACE</div><h1>{esc(profile['name'])}<span class="cn">{esc(profile['name_zh'])}</span></h1><div class="role">{esc(profile['role'])}<br>{esc(profile['affiliation'])}</div><p class="intro">{esc(profile['intro'])}</p><div class="social">{social}</div></div>{portrait}</section><section class="section"><div class="section-title"><h2>About / 关于我</h2><span class="eyebrow">CURIOSITY DRIVES RESEARCH</span></div><div class="about-grid"><p>{esc(profile['about'])}</p><div class="tags">{''.join('<span class="tag">'+esc(i)+'</span>' for i in profile['interests'])}</div></div></section><section class="section"><div class="section-title"><h2>News / 近况</h2></div>{''.join('<div class="news"><span class="date">'+esc(n['date'])+'</span><p>'+esc(n['text'])+'</p></div>' for n in profile['news'])}</section><section class="section"><div class="section-title"><h2>Research / 研究成果</h2><a href="publications.html">所有发表 →</a></div><p class="draft-note">草稿中的论文为占位示例，待补充真实研究成果。</p>{''.join(pub_html(p) for p in sorted(pubs,key=lambda p:p['year'],reverse=True)[:1])}</section><section class="section"><div class="section-title"><h2>Writing / 最近写作</h2><a href="blog.html">所有文章 →</a></div>{''.join(post_row(p) for p in posts[:1]) or '<p class="empty">新的文章即将发布。</p>'}</section>'''
write('index.html', layout('Home', 'home', home))
write('publications.html', layout('Publications','publications','<div class="page-head"><div class="eyebrow">RESEARCH OUTPUT</div><h1>Publications<span class="cn">学术发表</span></h1><p>在这里汇集研究工作、论文与开放资源。</p></div><p class="draft-note">以下为展示排版的示例条目，尚非真实发表记录。</p>'+(''.join(pub_html(p) for p in sorted(pubs,key=lambda p:p['year'],reverse=True)) or '<p class="empty">论文信息即将更新。</p>')))
write('blog.html',layout('Blog','blog','<div class="page-head"><div class="eyebrow">NOTES ALONG THE WAY</div><h1>Blog<span class="cn">思考与笔记</span></h1><p>论文之外，留下研究过程中的问题、灵感与发现。</p></div>'+(''.join(post_row(p) for p in posts) or '<p class="empty">新的文章即将发布。</p>')))
for p in posts:
    write(f'posts/{p["slug"]}.html', layout(p['title'],'blog',f'<article class="article"><a class="back" href="../blog.html">← 返回 Blog</a><h1>{esc(p["title"])}</h1><div class="date">{esc(p["date"])} · {esc(p["tag"])}</div>{markdown(p["body"])}</article>','../'))
write('404.html',layout('Page not found','', '<div class="page-head"><h1>404</h1><p>这个页面暂时不存在。</p><a class="back" href="index.html">返回首页 →</a></div>'))
write('.nojekyll','')
print(f'Built {len(list(OUT.rglob("*.html")))} pages in {OUT}')
