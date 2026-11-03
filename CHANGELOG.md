# Changelog

## 1.3.3 — 2026-11-03

- New: `scripts/check_svg_overlap.py` — samples every connector against node rects and fails on collisions; run before opening a page.
- Lessons now require one rendered look (headless screenshot) before delivery, plus DOM step checks; the earlier "skip vision" rule was wrong.
- Documented drawing order (connectors before node groups) and elbow routing around containers.

## 1.3.2 — 2026-11-03

- README restructured after comparable skill repos: badge, one-line scope, install, usage, file tree, requirements, notes, license.
- Install simplified to `npx skills add cnatom/active-recall-drill`; the CLI detects the single skill in the repo.

## 1.3.1 — 2026-11-03

- README: added the one-line prompt for installing through an agent; trimmed filler sentences in both languages.

## 1.3.0 — 2026-11-03

- Repository layout moved to `skills/active-recall-drill/` so skills.sh can discover and install it: `npx skills add cnatom/active-recall-drill --skill active-recall-drill`.
- README reduced to the standard shape (features, install, usage, docs, notes, license) in Chinese with an English mirror.
- SKILL.md states that all paths are relative to the skill directory.

## 1.2.0 — 2026-11-03

- New: `scripts/i18n.py` message catalog; every CLI message and builder page is available in English and Chinese.
- New: `--lang zh|en` and `DRILL_LANG`; default language follows `LANG` / `LC_ALL`.
- New: course pages ship `assets/i18n.js` plus a nav language switch; the scaffolded language comes from `new_course.py --lang` and falls back to `navigator.language`.
- New: `README.zh-CN.md`; other docs stay English-only by design.
- Builders (`build_index.py`, `build_glossary.py`) gained `--lang` and localised page chrome.

## 1.1.0 — 2026-11-03

- New: `scripts/new_course.py` scaffolds a multi-chapter course (index map, chapter pages, shared `assets/`, empty terms file) in one command.
- New: `templates/course/` (`index.html`, `chapter.html`, `assets/course.css`, `assets/course.js`) with `window.__COURSE_CHAPTERS` indirection so the chapter list stays generated.
- New: `references/course-layout.md` — chapter count, ordering, page shape, progress, `file://` rules.
- SKILL.md: "New Subject → New Course" is now the default path for fresh material.

## 1.0.0 — 2026-11-03

First public-ready version.

- Store schema v1: `data/reviews.json`, atomic writes, refuses to overwrite a corrupt store.
- Scheduling: 1/3/7/15/30-day intervals, mastery after a sixth correct answer, lapse tracking.
- Commands: `due`, `card`, `reveal`, `grade`, `add`, `import`, `stats`, `list`, `edit`, `rm`, `note`, `selftest`.
- Extras: entry-page generator (`build_index.py`), glossary generator (`build_glossary.py`), terms-to-JS converter (`build_terms.py`), lesson template.
- Docs: `references/data-model.md`, `references/html-lessons.md`, `references/teaching-style.md`.
- Tests: `tests/test_drill.py` (stdlib `unittest`, no network).

### Breaking changes

None — first release.
