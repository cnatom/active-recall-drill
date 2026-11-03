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
    // 同步进度：写入用户选的 progress.json（无服务进程）
    const syncBtn = document.createElement('button');
    syncBtn.textContent = '同步进度';
    syncBtn.title = '把当前章节与步骤写入 progress.json';
    inner.appendChild(syncBtn);
    syncBtn.addEventListener('click', () => syncProgress());
    document.body.appendChild(dock);
    const pad = () => { document.body.style.paddingBottom = (dock.offsetHeight + 18) + 'px'; };
    pad();
    window.addEventListener('resize', pad);
    window.addEventListener('load', pad);
  })();


  // ---- 进度同步（File System Access API，无后台进程）----
  function currentChapterMeta() {
    const c = CHAPTERS.find(x => x.id === (document.body.dataset.chapter || 'index')) || {};
    const el = document.getElementById('step');
    const m = el && el.textContent.match(/\d+/);
    return { id: c.id, num: c.num, title: c.title, step: m ? Number(m[0]) : 0 };
  }

  function progressPayload() {
    return {
      updated: new Date().toISOString(),
      current: currentChapterMeta(),
      visited: (() => { try { return JSON.parse(localStorage.getItem('netcloud-course-progress') || '{}'); } catch (e) { return {}; } })(),
    };
  }

  function toast(text) {
    const t = document.createElement('div');
    t.textContent = text;
    t.style.cssText = 'position:fixed;left:50%;bottom:70px;transform:translateX(-50%);background:#16181d;color:#fff;font-size:13px;padding:7px 14px;border-radius:8px;z-index:99;opacity:.95';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 1800);
  }

  function idb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open('course-progress', 1);
      req.onupgradeneeded = () => req.result.createObjectStore('handles');
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  function idbGet(key) {
    return idb().then(db => new Promise((res, rej) => {
      const tx = db.transaction('handles', 'readonly').objectStore('handles').get(key);
      tx.onsuccess = () => res(tx.result);
      tx.onerror = () => rej(tx.error);
    }));
  }
  function idbSet(key, val) {
    return idb().then(db => new Promise((res, rej) => {
      const tx = db.transaction('handles', 'readwrite').objectStore('handles').put(val, key);
      tx.onsuccess = () => res();
      tx.onerror = () => rej(tx.error);
    }));
  }

  async function syncProgress() {
    const json = JSON.stringify(progressPayload(), null, 2);
    if (window.showSaveFilePicker) {
      try {
        let handle = await idbGet('progress-file').catch(() => null);
        if (!handle) {
          handle = await window.showSaveFilePicker({
            suggestedName: 'progress.json',
            types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
          });
          await idbSet('progress-file', handle).catch(() => {});
        }
        let perm = await handle.queryPermission({ mode: 'readwrite' });
        if (perm !== 'granted') perm = await handle.requestPermission({ mode: 'readwrite' });
        if (perm !== 'granted') throw new Error('permission denied');
        const w = await handle.createWritable();
        await w.write(json);
        await w.close();
        toast('已写入 progress.json');
        return;
      } catch (e) {
        if (e && e.name === 'AbortError') return;
        // 权限被拒或浏览器不支持时退回下载
      }
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([json], { type: 'application/json' }));
    a.download = 'progress.json';
    a.click();
    URL.revokeObjectURL(a.href);
    toast('已下载 progress.json');
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
