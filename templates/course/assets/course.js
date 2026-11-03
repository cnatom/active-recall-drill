// Course chrome: chapter navigation, progress, language switch, term rendering.
// Data comes from assets/course-data.js (window.__COURSE_CHAPTERS, window.__COURSE_LANG).
(function () {
  const CHAPTERS = window.__COURSE_CHAPTERS || [];
  window.CHAPTERS = CHAPTERS;

  const STRINGS = window.I18N || { en: {} };
  const KEY_LANG = 'course-lang';
  const KEY_PROGRESS = 'netcloud-course-progress';

  function detectLang() {
    const saved = localStorage.getItem(KEY_LANG);
    if (saved && STRINGS[saved]) return saved;
    const scaffolded = window.__COURSE_LANG;
    if (scaffolded && STRINGS[scaffolded]) return scaffolded;
    const nav = (navigator.language || 'en').toLowerCase();
    return nav.startsWith('zh') && STRINGS.zh ? 'zh' : 'en';
  }

  const LANG = detectLang();
  window.COURSE_LANG = LANG;
  document.documentElement.lang = LANG === 'zh' ? 'zh-CN' : 'en';

  function t(key, vars) {
    const table = STRINGS[LANG] || STRINGS.en || {};
    let text = table[key] || (STRINGS.en && STRINGS.en[key]) || key;
    if (vars) {
      Object.keys(vars).forEach(k => { text = text.split('{' + k + '}').join(vars[k]); });
    }
    return text;
  }
  window.courseT = t;

  function readProgress() {
    try { return JSON.parse(localStorage.getItem(KEY_PROGRESS) || '{}'); } catch (e) { return {}; }
  }
  function markVisited(id) {
    if (!id) return;
    const p = readProgress();
    if (!p[id]) { p[id] = Date.now(); localStorage.setItem(KEY_PROGRESS, JSON.stringify(p)); }
  }

  const currentId = document.body.dataset.chapter || 'index';
  markVisited(currentId);
  const progress = readProgress();

  // static labels: <span data-i18n="next">…</span>, optionally with data-num="01"
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n, el.dataset.num ? { num: el.dataset.num } : null);
  });

  const navHost = document.getElementById('cnav');
  if (navHost) {
    const pills = CHAPTERS.map(c => {
      const cls = c.id === currentId ? 'pill cur' : (progress[c.id] ? 'pill done' : 'pill');
      return `<a class="${cls}" href="${c.file}">${c.num} ${c.title}</a>`;
    }).join('');
    navHost.innerHTML = `<div class="inner">
      <a class="brand" href="index.html">${t('courseMap')}</a>
      <nav class="pills">${pills}</nav>
      <button class="lang" id="langToggle">${t('switchTo')}</button>
    </div>`;
    const btn = document.getElementById('langToggle');
    if (btn) btn.onclick = () => {
      localStorage.setItem(KEY_LANG, LANG === 'zh' ? 'en' : 'zh');
      location.reload();
    };
  }

  const pagerHost = document.getElementById('pager');
  if (pagerHost) {
    const idx = CHAPTERS.findIndex(c => c.id === currentId);
    const prev = idx > 0 ? CHAPTERS[idx - 1] : null;
    const next = idx >= 0 && idx < CHAPTERS.length - 1 ? CHAPTERS[idx + 1] : null;
    pagerHost.innerHTML = `
      ${prev ? `<a href="${prev.file}">← ${prev.num} ${prev.title}</a>` : '<span></span>'}
      ${next ? `<a href="${next.file}">${next.num} ${next.title} →</a>` : `<a href="index.html">${t('backToMap')}</a>`}`;
  }

  // terms
  window.TERMS = window.TERMS || {};
  let waiting = [];
  let loaded = false;
  const useList = list => (list || []).forEach(x => {
    window.TERMS[x.abbr] = x;
    if (x.cn) window.TERMS[x.cn] = x;
  });
  Promise.resolve(window.__TERMS ? window.__TERMS
    : fetch('术语.json').then(r => r.json()).then(d => d.terms).catch(() => []))
    .then(list => { useList(list); })
    .then(() => { loaded = true; waiting.forEach(cb => cb()); waiting = []; });

  window.termsReady = function (cb) { if (loaded) cb(); else waiting.push(cb); };
  window.showTerms = function (hostId, keys) {
    const host = document.getElementById(hostId);
    if (!host) return;
    window.termsReady(() => {
      const def = document.getElementById('tdef');
      host.innerHTML = '';
      if (def) def.hidden = true;
      (keys || []).forEach(k => {
        const term = window.TERMS[k];
        if (!term) return;
        const b = document.createElement('button');
        b.className = 'tchip';
        b.textContent = k;
        const head = [term.abbr, term.full, term.cn].filter(Boolean).join('｜');
        b.onclick = () => { if (def) { def.hidden = false; def.textContent = head + '：' + term.note; } };
        host.appendChild(b);
      });
    });
  };

  window.termsReady(() => {
    document.querySelectorAll('[data-term]').forEach(el => {
      const term = window.TERMS[el.dataset.term];
      if (!term) return;
      el.setAttribute('title', [term.abbr, term.full, term.cn].filter(Boolean).join('｜') +
        (term.note ? '：' + term.note : ''));
    });
  });
})();
