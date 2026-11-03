# Changelog

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
