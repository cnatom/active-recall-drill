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
    // 鼠标停在章节列表上时，垂直滚轮改为横向滚动
    const pillsEl = navHost.querySelector('.pills');
    if (pillsEl) {
      pillsEl.addEventListener('wheel', e => {
        if (Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
        if (pillsEl.scrollWidth <= pillsEl.clientWidth) return;
        e.preventDefault();
        pillsEl.scrollLeft += e.deltaY;
      }, { passive: false });
    }

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


  // 步骤描述移到主图上方；控制条与术语固定到底部
  (function () {
    const stage = document.querySelector('.wrap > .stage');
    const msgEl = document.getElementById('msg');
    if (stage && msgEl && !document.querySelector('.stepcap')) {
      const cap = document.createElement('div');
      cap.className = 'stepcap';
      stage.parentNode.insertBefore(cap, stage);
      cap.appendChild(msgEl);
    }
  })();

  (function () {
    const bar = document.querySelector('.wrap > .bar');
    const terms = document.querySelector('.wrap > .terms');
    if (!bar && !terms) return;
    const dock = document.createElement('div');
    dock.className = 'dock';
    const inner = document.createElement('div');
    inner.className = 'inner';
    dock.appendChild(inner);
    if (bar) inner.appendChild(bar);
    if (terms) inner.appendChild(terms);
    document.body.appendChild(dock);
    const pad = () => { document.body.style.paddingBottom = (dock.offsetHeight + 18) + 'px'; };
    pad();
    window.addEventListener('resize', pad);
    window.addEventListener('load', pad);
  })();

  // report chapter + step to the local recorder (silently ignored if it is not running)
  (function () {
    const meta = CHAPTERS.find(c => c.id === currentId) || {};
    function currentStep() {
      const el = document.getElementById('step');
      const m = el && el.textContent.match(/\d+/);
      return m ? Number(m[0]) : 0;
    }
    function report() {
      const payload = { file: location.pathname.split('/').pop(), id: currentId,
                        num: meta.num, title: meta.title, step: currentStep() };
      try {
        fetch('http://127.0.0.1:8766/hit', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload), keepalive: true,
        }).catch(() => {});
      } catch (e) {}
    }
    report();
    document.addEventListener('click', report, { capture: true });
    document.addEventListener('visibilitychange', () => { if (document.hidden) report(); });
  })();

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
