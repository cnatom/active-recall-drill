// 网络云组网课：章节导航、学习进度、术语加载
(function () {
  const CHAPTERS = window.__COURSE_CHAPTERS || [];
  window.CHAPTERS = CHAPTERS;

  const KEY = 'netcloud-course-progress';
  function readProgress() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; }
  }
  function markVisited(id) {
    if (!id) return;
    const p = readProgress();
    if (!p[id]) { p[id] = Date.now(); localStorage.setItem(KEY, JSON.stringify(p)); }
  }

  const currentId = document.body.dataset.chapter || 'index';
  markVisited(currentId);
  const progress = readProgress();

  const navHost = document.getElementById('cnav');
  if (navHost) {
    const pills = CHAPTERS.map(c => {
      const cls = c.id === currentId ? 'pill cur' : (progress[c.id] ? 'pill done' : 'pill');
      return `<a class="${cls}" href="${c.file}">${c.num} ${c.title}</a>`;
    }).join('');
    navHost.innerHTML = `<div class="inner">
      <a class="brand" href="index.html">网络云组网 <span>· 学习课</span></a>
      <nav class="pills">${pills}</nav>
    </div>`;
  }

  const pagerHost = document.getElementById('pager');
  if (pagerHost) {
    const idx = CHAPTERS.findIndex(c => c.id === currentId);
    const prev = idx > 0 ? CHAPTERS[idx - 1] : null;
    const next = idx >= 0 && idx < CHAPTERS.length - 1 ? CHAPTERS[idx + 1] : null;
    pagerHost.innerHTML = `
      ${prev ? `<a href="${prev.file}">← ${prev.num} ${prev.title}</a>` : '<span></span>'}
      ${next ? `<a href="${next.file}">${next.num} ${next.title} →</a>` : '<a href="index.html">回到课程地图</a>'}`;
  }

  // 术语
  window.TERMS = window.TERMS || {};
  let waiting = [];
  let loaded = false;
  const useList = list => (list || []).forEach(t => { window.TERMS[t.abbr] = t; if (t.cn) window.TERMS[t.cn] = t; });
  Promise.resolve(window.__TERMS ? window.__TERMS : fetch('术语.json').then(r => r.json()).then(d => d.terms).catch(() => [])).then(list => {
    useList(list);
  }).then(() => {
    loaded = true;
    waiting.forEach(cb => cb());
    waiting = [];
  });
  window.termsReady = function (cb) {
    if (loaded) cb(); else waiting.push(cb);
  };
  window.showTerms = function (hostId, keys) {
    const host = document.getElementById(hostId);
    if (!host) return;
    window.termsReady(() => {
      const def = document.getElementById('tdef');
      host.innerHTML = '';
      if (def) def.hidden = true;
      (keys || []).forEach(k => {
        const t = window.TERMS[k];
        if (!t) return;
        const b = document.createElement('button');
        b.className = 'tchip';
        b.textContent = k;
        const head = [t.abbr, t.full, t.cn].filter(Boolean).join('｜');
        b.onclick = () => { if (def) { def.hidden = false; def.textContent = head + '：' + t.note; } };
        host.appendChild(b);
      });
    });
  };

  // 给带 data-term 的元素挂悬停说明
  window.termsReady(() => {
    document.querySelectorAll('[data-term]').forEach(el => {
      const t = window.TERMS[el.dataset.term];
      if (!t) return;
      el.setAttribute('title', [t.abbr, t.full, t.cn].filter(Boolean).join('｜') + (t.note ? '：' + t.note : ''));
    });
  });
})();
