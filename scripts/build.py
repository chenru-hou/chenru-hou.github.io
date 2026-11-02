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
site = json.loads((ROOT / 'content/site.json').read_text()) if (ROOT / 'content/site.json').exists() else {}
def esc(value): return html.escape(str(value), quote=True)
def link(item):
    url = item['url']
    if not url.startswith(('https://', 'http://', 'mailto:')): raise ValueError('Unsupported link URL')
    return f'<a href="{esc(url)}">{esc(item["label"])} ↗</a>'
def layout(title, current, content, prefix=''):
    description = site.get('description') or profile['intro'].strip() or 'Academic website of '+profile['name']
    page = {'home':'', 'publications':'publications.html', 'blog':'blog.html'}.get(current, '')
    canonical = site.get('url', '').rstrip('/')+'/'+page
    metadata = ''
    if site.get('url') and not prefix and current:
        metadata = f'<link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} · {esc(profile["name"])}"><meta property="og:description" content="{esc(description)}">'
    if current == 'home':
        person = {'@context':'https://schema.org','@type':'Person','name':profile['name'],'url':site.get('url',''),'jobTitle':profile['role'],'sameAs':[i['url'] for i in profile['links']]}
        metadata += '<script type="application/ld+json">'+json.dumps(person).replace('<', '\\u003c')+'</script>'
    nav = ''.join(f'<a href="{prefix}{file}"'+(' aria-current="page"' if current == key else '')+f'>{label}</a>' for key,file,label in [('home','index.html','Home'),('publications','publications.html','Publications'),('blog','blog.html','Blog')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{esc(description)}">{metadata}<title>{esc(title)} · {esc(profile['name'])}</title><link rel="stylesheet" href="{prefix}assets/style.css"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='%23416950'/%3E%3C/svg%3E"></head><body><a class="skip" href="#main">Skip to content</a><div class="shell"><header><nav aria-label="Main navigation">{nav}</nav></header><main id="main">{content}</main><footer><span>© {date.today().year} {esc(profile['name'])}</span><span class="footer-mark">RESEARCH · NOTES · IDEAS</span></footer></div></body></html>'''
def write(path, text):
    # Keep empty fields available to the editor without reserving visual space.
    text = re.sub(r'<p(\s[^>]*)?>(\s*)</p>', lambda m: '<p'+(m[1] or '')+' hidden></p>', text)
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
def pub_html(p):
    doi = p.get('doi', '')
    if doi and not doi.startswith('https://doi.org/'): raise ValueError('Unsupported DOI URL')
    doi_link = ' · <a class="doi" href="'+esc(doi)+'">DOI ↗</a>' if doi else ''
    return f'''<article class="pub"><div class="year">{esc(p['year'] or '—')}</div><div><span class="type">{esc(p['type'])}</span><h3>{esc(p['title'])}</h3><p>{esc(p['authors'])}</p><p class="venue"{' hidden' if not p['venue'].strip() and not doi else ''}><span class="venue-text">{esc(p['venue'])}</span>{doi_link}</p>{'<p>'+esc(p['note'])+'</p>' if p.get('note', '').strip() else ''}<div class="pub-links">{''.join(link(i) for i in p.get('links', []))}</div></div></article>'''
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
portrait='''<div class="portrait" role="img" aria-label="Portrait placeholder"><svg viewBox="0 0 160 180" fill="none" aria-hidden="true"><circle cx="80" cy="57" r="32" stroke="currentColor" stroke-width="1.2"/><path d="M18 166c0-45 24-65 62-65s62 20 62 65" stroke="currentColor" stroke-width="1.2"/><circle cx="80" cy="84" r="69" stroke="currentColor" stroke-opacity=".2"/><path d="M0 166h160" stroke="currentColor" stroke-opacity=".4"/></svg><span>YOUR PORTRAIT</span></div>'''
def entries(title, items):
    if not items: return ''
    rows = ''.join(f'<article class="vita-row"><div class="date">{esc(x["date"])}</div><div><h3>{esc(x["title"])}</h3><p class="institution">{esc(x["institution"])}</p><p>{esc(x["detail"])}</p></div></article>' for x in items)
    return f'<section class="section"><div class="section-title"><h2>{title}</h2></div>{rows}</section>'
affiliation_link = ' · '+link({'label':'Website','url':profile['affiliation_url']}) if profile.get('affiliation_url') else ''
home=f'''<section class="hero"><div><h1>{esc(profile['name'])}</h1><div class="role">{esc(profile['role'])}<br>{esc(profile['affiliation'])}{affiliation_link}</div><p class="intro">{esc(profile['intro'])}</p><div class="social">{social}</div></div></section><section class="section"><div class="section-title"><h2>About</h2></div><div class="about-grid"><p>{esc(profile['about'])}</p><div class="research-interests"><div class="eyebrow">CURIOSITY DRIVES RESEARCH</div><div class="tags">{''.join('<span class="tag">'+esc(i)+'</span>' for i in profile['interests'])}</div></div></div></section><section class="section"><div class="section-title"><h2>News</h2></div>{''.join('<div class="news"><span class="date">'+esc(n['date'])+'</span><p>'+esc(n['text'])+'</p></div>' for n in profile['news'])}</section><section class="section"><div class="section-title"><h2>Journal papers</h2><a href="publications.html">All publications →</a></div>{''.join(pub_html(p) for p in [p for p in pubs if p.get('homepage')])}</section>'''
# Hide an empty news section until a factual update is supplied.
if not profile['news']:
    home = home.replace('<section class="section"><div class="section-title"><h2>News</h2></div></section>', '')
home += entries('Education', profile.get('education', []))
home += entries('Research experience', profile.get('experience', []))
home += entries('Conferences', profile.get('conferences', []))
home += entries('Teaching', profile.get('teaching', []))
if profile.get('methods'):
    home += '<section class="section"><div class="section-title"><h2>Methods</h2></div><p>'+esc(profile['methods'])+'</p></section>'
write('index.html', layout('Home', 'home', home))
write('publications.html', layout('Publications','publications','<div class="page-head"><div class="eyebrow">RESEARCH OUTPUT</div><h1>Publications</h1><p>Research on classroom diversity, peer networks, and educational inequality.</p></div>'+('<h2 class="pub-group">Accepted publications</h2>'+''.join(pub_html(p) for p in pubs if p['type'] == 'Accepted')+'<h2 class="pub-group">Manuscripts in revision</h2>'+''.join(pub_html(p) for p in pubs if 'revision' in p['type'].lower())+'<h2 class="pub-group">Working papers & manuscripts under review</h2>'+''.join(pub_html(p) for p in pubs if p['type'] != 'Accepted' and 'revision' not in p['type'].lower()) or '<p class="empty">Publication details coming soon.</p>')))
write('blog.html',layout('Blog','blog','<div class="page-head"><div class="eyebrow">NOTES ALONG THE WAY</div><h1>Blog</h1><p>Questions, ideas, and discoveries from the research process.</p></div>'+(''.join(post_row(p) for p in posts) or '<p class="empty">New posts coming soon.</p>')))
for p in posts:
    write(f'posts/{p["slug"]}.html', layout(p['title'],'blog',f'<article class="article"><a class="back" href="../blog.html">← Back to Blog</a><h1>{esc(p["title"])}</h1><div class="date">{esc(p["date"])} · {esc(p["tag"])}</div>{markdown(p["body"])}</article>','../'))
write('404.html',layout('Page not found','', '<div class="page-head"><h1>404</h1><p>The page you are looking for could not be found.</p><a class="back" href="index.html">Back to home →</a></div>'))
write('.nojekyll','')
if site.get('url'):
    origin = site['url'].rstrip('/')
    urls = [origin+'/' if p.name == 'index.html' else origin+'/'+p.relative_to(OUT).as_posix() for p in sorted(OUT.rglob('*.html')) if p.name != '404.html']
    write('robots.txt', 'User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(url)+'</loc></url>' for url in urls)+'</urlset>')
print(f'Built {len(list(OUT.rglob("*.html")))} pages in {OUT}')
