(() => {
  'use strict';
  const pages = JSON.parse(document.getElementById('preview-pages').textContent);
  let data = JSON.parse(document.getElementById('preview-data').textContent);
  const root = document.getElementById('preview-root');
  const status = document.getElementById('edit-status');
  const toggle = document.getElementById('edit-toggle');
  const undoButton = document.getElementById('edit-undo');
  let editing = false, currentPage = 'index.html', dirty = false;
  const undo = [];
  const copy = value => JSON.parse(JSON.stringify(value));
  function checkpoint() { undo.push(copy(data)); if (undo.length > 50) undo.shift(); undoButton.disabled = false; }
  function changed() { dirty = true; status.textContent = '有修改尚未导出。请点击“保存可编辑预览”保留，或“导出内容”用于同步 GitHub。'; }
  function valueAt(path) { return path.split('.').reduce((o, key) => o[key], data); }
  function setValue(path, value) {
    const parts = path.split('.'); const key = parts.pop();
    parts.reduce((o, part) => o[part], data)[key] = value;
  }
  function bind(node, path) {
    if (!node) return;
    node.dataset.editPath = path; node.dataset.placeholder = '点击补充';
    const value = valueAt(path);
    node.textContent = path.endsWith('.year') && !value ? '—' : String(value ?? '');
    node.contentEditable = editing ? 'true' : 'false';
  }
  function section(title) { return [...root.querySelectorAll('section')].find(s => s.querySelector('h2')?.textContent === title); }
  function bindEntries(title, key) {
    (section(title)?.querySelectorAll('.vita-row') || []).forEach((row, i) => {
      for (const [selector, field] of [['.date','date'], ['h3','title'], ['.institution','institution'], ['p:not(.institution)','detail']])
        bind(row.querySelector(selector), `profile.${key}.${i}.${field}`);
    });
  }
  function bindPapers() {
    // Match by original titles, independent of edited status/group order.
    const seed = JSON.parse(document.getElementById('preview-data').textContent);
    const original = seed.originalPublications || seed.publications;
    const selected = original.map((p, i) => ({p, i}));
    const ordered = currentPage === 'index.html' ? selected.filter(x => x.p.homepage) :
      [...selected.filter(x => x.p.type === 'Accepted'), ...selected.filter(x => x.p.type.toLowerCase().includes('revision')), ...selected.filter(x => x.p.type !== 'Accepted' && !x.p.type.toLowerCase().includes('revision'))];
    root.querySelectorAll('.pub').forEach((row, n) => {
      const index = ordered[n]?.i; if (index === undefined) return;
      const body = row.children[1];
      const paragraphs = [...body.children].filter(x => x.tagName === 'P');
      let note = paragraphs[2];
      if (!note) { note = document.createElement('p'); body.insertBefore(note, body.querySelector('.pub-links')); }
      note.dataset.note = '';
      [['.year','year'], ['.type','type'], ['h3','title'], ['p:not(.venue):not([data-note])','authors'], ['.venue','venue'], ['[data-note]','note']].forEach(([selector, field]) => bind(row.querySelector(selector), `publications.${index}.${field}`));
      note.hidden = !editing && !note.textContent;
    });
  }
  function render() {
    root.innerHTML = new DOMParser().parseFromString(pages[currentPage], 'text/html').body.innerHTML;
    if (currentPage === 'index.html') {
      bind(root.querySelector('.hero h1'), 'profile.name');
      const role = root.querySelector('.role');
      if (role) {
        role.replaceChildren(document.createElement('span'), document.createElement('br'), document.createElement('span'));
        bind(role.children[0], 'profile.role'); bind(role.children[2], 'profile.affiliation');
      }
      bind(root.querySelector('.intro'), 'profile.intro'); bind(root.querySelector('.about-grid > p'), 'profile.about');
      root.querySelectorAll('.tag').forEach((tag, i) => bind(tag, `profile.interests.${i}`));
      bindEntries('Education', 'education'); bindEntries('Research experience', 'experience');
      bindEntries('Conferences', 'conferences'); bindEntries('Teaching', 'teaching');
      bind(section('Methods')?.querySelector('p'), 'profile.methods');
      root.querySelectorAll('.news').forEach((row, i) => { bind(row.querySelector('.date'), `profile.news.${i}.date`); bind(row.querySelector('p'), `profile.news.${i}.text`); });
      const social = root.querySelector('.social');
      if (social) {
        social.replaceChildren();
        const links = data.profile.email ? [{label:'Email',url:'mailto:'+data.profile.email}, ...data.profile.links] : data.profile.links;
        links.forEach(item => { const a = document.createElement('a'); a.textContent = item.label+' ↗'; a.href = item.url; social.append(a); });
      }
    }
    if (['index.html','publications.html'].includes(currentPage)) bindPapers();
    const copyright = root.querySelector('footer > span');
    if (copyright) copyright.textContent = `© ${new Date().getFullYear()} ${data.profile.name}`;
  }
  root.addEventListener('focusin', e => { if (editing && e.target.dataset.editPath) checkpoint(); });
  root.addEventListener('input', e => {
    const path = e.target.dataset.editPath; if (!editing || !path) return;
    let value = e.target.innerText.replace(/\r/g, '');
    if (path.endsWith('.year')) {
      if (!/^(\d{0,4}|—)$/.test(value.trim())) { status.textContent = '年份请填写四位数字，或留空。'; return; }
      value = Number(value.trim().replace('—','')) || 0;
    }
    setValue(path, value); changed();
  });
  root.addEventListener('paste', e => {
    if (!editing || !e.target.dataset.editPath) return;
    e.preventDefault();
    const selection = window.getSelection(); if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0); range.deleteContents();
    const text = document.createTextNode(e.clipboardData.getData('text/plain'));
    range.insertNode(text); range.setStartAfter(text); range.collapse(true);
    selection.removeAllRanges(); selection.addRange(range);
    e.target.dispatchEvent(new Event('input', {bubbles:true}));
  });
  root.addEventListener('focusout', e => {
    const path = e.target.dataset.editPath;
    if (path?.endsWith('.year')) e.target.textContent = valueAt(path) || '—';
  });
  root.addEventListener('click', e => {
    const a = e.target.closest('a'); if (!a) return;
    const file = a.getAttribute('href');
    if (pages[file]) { e.preventDefault(); currentPage = file; render(); window.scrollTo(0,0); }
    else if (editing && !file.startsWith('#')) { e.preventDefault(); status.textContent = '编辑时外部链接暂不跳转；可通过“联系方式”修改联系链接。'; }
  });
  toggle.addEventListener('click', () => {
    editing = !editing; toggle.textContent = editing ? '完成编辑' : '开启编辑'; toggle.setAttribute('aria-pressed', editing);
    render(); if (!dirty) status.textContent = editing ? '点击虚线框内的文字即可修改；Home 和 Publications 中的同一论文会同步更新。' : '浏览模式。点击“开启编辑”继续修改。';
  });
  undoButton.addEventListener('click', () => { if (!undo.length) return; data = undo.pop(); undoButton.disabled = !undo.length; changed(); render(); });
  function download(name, content, type) {
    const url = URL.createObjectURL(new Blob([content], {type}));
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }
  document.getElementById('edit-save').addEventListener('click', () => {
    const doc = document.documentElement.cloneNode(true);
    // Preserve the original ordering metadata separately from editable values.
    doc.querySelector('#preview-data').textContent = JSON.stringify({...data, originalPublications: JSON.parse(document.getElementById('preview-data').textContent).originalPublications || JSON.parse(document.getElementById('preview-data').textContent).publications}).replace(/</g,'\\u003c');
    doc.querySelector('#preview-root').replaceChildren();
    doc.querySelector('#edit-toggle').textContent = '开启编辑'; doc.querySelector('#edit-toggle').setAttribute('aria-pressed','false');
    doc.querySelector('#edit-undo').disabled = true; doc.querySelector('#contact-dialog').removeAttribute('open');
    doc.querySelector('#edit-status').textContent = '已载入保存的内容。开启编辑后，点击文字即可修改。';
    download('chenru-editable-preview.html','<!doctype html>\n'+doc.outerHTML,'text/html;charset=utf-8');
    dirty = false; status.textContent = '已发起预览文件下载。请确认下载完成；以后打开该 HTML 文件可继续编辑。GitHub 尚未同步。';
  });
  document.getElementById('edit-export').addEventListener('click', () => {
    download('website-content.json', JSON.stringify({profile:data.profile,publications:data.publications},null,2)+'\n','application/json');
    status.textContent = '已发起内容下载。把 website-content.json 发回此聊天，即可协助同步到仓库。';
  });
  document.getElementById('edit-import').addEventListener('click', () => document.getElementById('edit-file').click());
  document.getElementById('edit-file').addEventListener('change', async e => {
    const file = e.target.files[0]; if (!file) return;
    try {
      const next = JSON.parse(await file.text()), p = next.profile;
      function compatible(sample, value) {
        if (Array.isArray(sample)) return Array.isArray(value) && sample.length === value.length && sample.every((x, i) => compatible(x, value[i]));
        if (sample && typeof sample === 'object') return value && typeof value === 'object' && Object.keys(sample).every(k => compatible(sample[k], value[k]));
        return typeof sample === typeof value;
      }
      if (!compatible(data.profile, p) || !compatible(data.publications, next.publications)) throw new Error('Invalid structure');
      if (!p || !['name','role','affiliation','intro','about','methods','email'].every(k => typeof p[k] === 'string') ||
          !['education','experience','conferences','teaching','news','links','interests'].every(k => Array.isArray(p[k])) ||
          !Array.isArray(next.publications) || next.publications.length !== data.publications.length ||
          !next.publications.every(x => x && typeof x.title === 'string') ||
          !p.links.every(x => x && typeof x.label === 'string' && /^https?:\/\//i.test(x.url))) throw new Error('Invalid content');
      checkpoint(); data.profile = copy(next.profile); data.publications = copy(next.publications); render(); changed();
    } catch { status.textContent = '导入失败：请选择从此预览“导出内容”生成的完整 JSON 文件。'; }
    e.target.value = '';
  });
  const dialog = document.getElementById('contact-dialog');
  document.getElementById('edit-contact').addEventListener('click', () => {
    const fields = document.getElementById('contact-fields'); fields.replaceChildren();
    function input(label, path, type='text') {
      const wrapper = document.createElement('label'); wrapper.textContent = label;
      const node = document.createElement('input'); node.type = type; node.dataset.path = path; node.value = valueAt(path);
      wrapper.append(node); fields.append(wrapper);
    }
    input('Email','profile.email','email');
    data.profile.links.forEach((_,i) => { input(`链接 ${i+1} 名称`,`profile.links.${i}.label`); input(`链接 ${i+1} 地址`,`profile.links.${i}.url`,'url'); });
    dialog.showModal();
  });
  dialog.querySelector('form').addEventListener('submit', e => {
    if (e.submitter?.value !== 'save') return;
    const inputs = [...dialog.querySelectorAll('input')];
    if (inputs.some(x => x.dataset.path.endsWith('.url') && !/^https?:\/\//i.test(x.value))) { e.preventDefault(); status.textContent = '链接地址必须以 https:// 或 http:// 开头。'; return; }
    checkpoint(); inputs.forEach(x => setValue(x.dataset.path,x.value)); changed(); render();
  });
  window.addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
  render();
})();
