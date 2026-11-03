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
    // 复制上下文：把当前章节与步骤复制成一段可直接发给 agent 的文字
    const copyBtn = document.createElement('button');
    copyBtn.textContent = '复制上下文';
    copyBtn.title = '复制当前进度，粘贴给 agent';
    inner.appendChild(copyBtn);
    copyBtn.addEventListener('click', () => copyContext());

    document.body.appendChild(dock);
    const pad = () => { document.body.style.paddingBottom = (dock.offsetHeight + 18) + 'px'; };
    pad();
    window.addEventListener('resize', pad);
    window.addEventListener('load', pad);
  })();



  // ---- 复制上下文（不写文件、不起服务）----
  function currentChapterMeta() {
    const c = CHAPTERS.find(x => x.id === (document.body.dataset.chapter || 'index')) || {};
    const el = document.getElementById('step');
    const m = el && el.textContent.match(/\d+/);
    return { id: c.id, num: c.num, title: c.title, step: m ? Number(m[0]) : 0 };
  }

  function contextText() {
    const cur = currentChapterMeta();
    let visited = {};
    try { visited = JSON.parse(localStorage.getItem('netcloud-course-progress') || '{}'); } catch (e) {}
    const seen = CHAPTERS.filter(c => c.id !== 'index' && visited[c.id])
      .map(c => `${c.num} ${c.title}`).join('、') || '（还没有记录）';
    const total = document.getElementById('step');
    const totalText = total ? total.textContent.split('/').pop().trim() : '';
    const now = new Date();
    const stamp = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' +
      String(now.getDate()).padStart(2, '0') + ' ' + String(now.getHours()).padStart(2, '0') + ':' +
      String(now.getMinutes()).padStart(2, '0');
    return [
      '【课程进度】',
      `当前：第 ${cur.num} 章 ${cur.title}（${location.pathname.split('/').pop()}）`,
      `步骤：${totalText || '未知'}`,
      `已看过：${seen}`,
      `时间：${stamp}`,
    ].join('\n');
  }

  function toast(text) {
    const t = document.createElement('div');
    t.textContent = text;
    t.style.cssText = 'position:fixed;left:50%;bottom:70px;transform:translateX(-50%);background:#16181d;color:#fff;font-size:13px;padding:7px 14px;border-radius:8px;z-index:99;opacity:.95';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 1600);
  }

  function copyContext() {
    const text = contextText();
    const done = () => toast('已复制，粘贴给 agent 即可');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { toast('复制失败，请手动选中'); }
    ta.remove();
  }

  // 键盘导航：左右翻步骤，上下翻章节
  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    const idx = CHAPTERS.findIndex(c => c.id === currentId);
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const btn = document.getElementById(e.key === 'ArrowLeft' ? 'prev' : 'next');
      if (btn) { e.preventDefault(); btn.click(); }
    } else if (e.key === 'ArrowUp' && idx > 0) {
      e.preventDefault();
      location.href = CHAPTERS[idx - 1].file;
    } else if (e.key === 'ArrowDown' && idx >= 0 && idx < CHAPTERS.length - 1) {
      e.preventDefault();
      location.href = CHAPTERS[idx + 1].file;
    }
  });

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
