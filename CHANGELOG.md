# Changelog

## 1.16.0 — 2026-11-04

- Collapse buttons move onto the rails themselves: `#mapToggle` in the course-map rail, `#tocToggle` in the 目录 rail.
- A collapsed rail keeps a 28 px strip so its button stays reachable; contents fade out.

## 1.15.0 — 2026-11-04

- 一级课程地图栏和二级目录栏可以各自独立收起、展开，状态分别持久化。
- 布局宽度改由 `--map-w` 与 `--toc-w` 相加，正文与底栏任意组合都不留空档。
- 两个浮动把手固定在左下角，窄屏自动隐藏。

## 1.14.0 — 2026-11-04

- New reference page `notes.html` (细碎知识): collapsible question cards with search and category chips, linked from the course rail.
- Entries live in `assets/notes-data.js`; `new_course.py` scaffolds the page and data file.
- Term list gains `5GC`.

## 1.13.0 — 2026-11-04

- 目录栏可收起：模块列表下方的 `收起目录 / 目录 ›` 按钮把二级目录收成 0 宽，状态记在 localStorage，内容区与底栏同步回移。
- 一级分组用原生 `<details>` 展开、收起，当前组默认打开。

## 1.12.1 — 2026-11-04

- Fix breakpoint order: the 目录 rail hides at 1200 px and below, the dock offset drops to 212 px on medium screens and 0 below 900 px.

## 1.12.0 — 2026-11-04

- Navigation split into two vertical rails: 课程地图 lists modules only, the new 目录 rail shows level-1 chapter groups with level-2 chapters, only the current group expanded.
- Chapter data gains a `group` field; the scaffold falls back to a single group when it is absent.
- 目录 rail hides below 1200 px; below 900 px the top bar shows module pills.
- Chapter page gains a spoken walkthrough section on the architecture chapter.

## 1.11.0 — 2026-11-04

- Packaged for the Agent Skills layout: repo root keeps README, LICENSE, CHANGELOG and `tests/`, the installable skill lives at `skills/active-recall-drill/`.
- `SKILL.md` frontmatter follows the agentskills.io spec (name, description, license, compatibility, string author/version); run section states that paths are relative to the skill directory.
- Readme split into Chinese primary `README.md` and `README.en.md`; install entry is `npx skills add cnatom/active-recall-drill`.
- Tests moved to the repo root and resolve the skill through `skills/*/scripts`.

## 1.10.0 — 2026-11-04

- Course shell is step-free: one complete figure per page, numbered points beside it in the right rail, no `?step` state or click-through fragments.
- Hover linking (`assets/hover-points.js`): a `data-p` figure part highlights its point and dims the rest; numbers are not printed on the figure.
- Term coverage is a hard gate: `scripts/check_terms.py` fails on any abbreviation missing from `术语.json`, and `showTerms` auto-collects ASCII terms found in the page.
- Layout rules: `.fig` and `.side` split with field tables in `.tables`; column heights must be balanced within ~150 px.
- Architecture pages reproduce reference diagrams in full and add an end-to-end business flow with failure/rollback notes.

## 1.9.3 — 2026-11-03

- Collision checker treats any box wider or taller than 250 units as a container band, so layered backgrounds no longer report false positives.
- All course chapters raised to the typography minimum and inactive-step opacity 0.45.

## 1.9.2 — 2026-11-03

- UI spec gains a typography section: `.stage.wide` for wide diagrams, minimum 11.5-unit SVG text, inactive opacity at least 0.45. A 1100-unit figure pushed into the 700 px column had been rendering labels at ~7 px.

## 1.9.1 — 2026-11-03

- Term search is a non-modal popover anchored bottom-right: no backdrop, the page stays readable and clickable; clicking outside closes it.

## 1.9.0 — 2026-11-03

- Global term search on every page: floating `术语 ⌘K` button, overlay with input and results, `/` or ⌘K to open, Enter for the first hit, Esc to close, link to the glossary page; step/chapter arrow shortcuts are suppressed while it is open.

## 1.8.1 — 2026-11-03

- Glossary masks are independent: `遮住英文` and `遮住中文` toggle separately; `只看缩写` hides both; clicking a card reveals what is masked.

## 1.8.0 — 2026-11-03

- Standalone glossary page allowed when the learner wants to memorise terms: abbreviation + full English visible, Chinese and explanation hidden until clicked, with `只看缩写`, `全部遮住/翻开`, `随机一张` and search. Linked from the nav, outside the chapter sequence.

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
