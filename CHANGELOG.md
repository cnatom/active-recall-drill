# Changelog

## 1.7.1 — 2026-11-03

- Context copy now reports the real position (`第 N 步 / 共 M 步`) instead of only the total.
- The M-LAG figure redrawn as a clean square: two verticals plus two diagonals, peer-link/DAD between the boxes, escape port as a single L.

## 1.7.0 — 2026-11-03

- Progress sharing replaced by a `复制上下文` button: copies chapter, file, step, visited chapters and timestamp to the clipboard so the learner can paste it into the chat. No file picker, no daemon.

## 1.6.0 — 2026-11-03

- Progress recording replaced by an explicit `同步进度` button using the File System Access API: writes `progress.json` from the page, remembers the file handle, falls back to download. No background daemon.
- Removed `scripts/progress_server.py` and the POST reporting it required.

## 1.5.1 — 2026-11-03

- Keyboard navigation: left/right arrows step the figure, up/down arrows move between chapters. Ignored while typing in an input.

## 1.5.0 — 2026-11-03

- New `scripts/progress_server.py`: a 127.0.0.1 recorder that pages POST to, so the agent can read which chapter and step the learner is on (`progress.json`).
- Course pages report on load, click and tab hide; failures are silent and the course works without the server.
- Documented that a full-screen overlay must not be used for this: a capture-phase listener records clicks without swallowing them.

## 1.4.1 — 2026-11-03

- Chapter pills convert a vertical mouse wheel into horizontal scrolling while the pointer is over them, so a wheel-only mouse can reach later chapters.

## 1.4.0 — 2026-11-03

- New `references/ui-spec.md`: the approved shell (nav, step bubble, figure, cards, appendix, dock), exact numbers, and the table of rejected variants with their replacements.
- SKILL.md and `html-lessons.md` now point at the spec instead of restating styles that had drifted (tinted band → speech bubble).

## 1.3.10 — 2026-11-03

- Step caption turned into a plain speech bubble (white, hairline border, small tail pointing at the figure) instead of a tinted band.

## 1.3.9 — 2026-11-03

- Step caption restyled: 17.5 px semibold on a tinted band with an accent left border, so it no longer reads like body copy.

## 1.3.8 — 2026-11-03

- Step caption moved above the diagram (part of the figure); only buttons and terms remain in the bottom dock.
- Follow-up answers now live in a collapsed `.extra` section at the page bottom instead of extending the main step flow.

## 1.3.7 — 2026-11-03

- Top navigation collapsed to one row (chapter pills scroll horizontally); bottom dock collapsed to one row: buttons, step caption and terms side by side, with the term definition floating above the bar instead of growing it.
- Page header padding reduced so the diagram starts higher.

## 1.3.6 — 2026-11-03

- Course pages dock the controls, the step caption and the term row to the bottom of the viewport, so they stay visible while scrolling a tall diagram; `assets/course.js` moves the existing blocks into `.dock` and reserves body padding.

## 1.3.5 — 2026-11-03

- Visual review removed: screenshot-plus-vision is too slow for the learner. Pre-delivery checks are the SVG collision script plus DOM step assertions only.
- `check_svg_overlap.py` now scans every `<svg>` block, not just the first.

## 1.3.4 — 2026-11-03

- Delivery order fixed: edit → open immediately → then run the overlap check, one rendered look and step assertions; fix and reopen silently when a check fails.

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
