---
name: active-recall-drill
description: Quiz learned material with spaced repetition and recall.
version: 1.3.5
author: cnatom, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [learning, spaced-repetition, recall, quiz]
    related_skills: [teach]
---

# Active Recall Drill

A local spaced-repetition store plus a drill loop: show the question, wait for an answer, reveal, grade, and let 1/3/7/15/30-day intervals decide the next review. Storage is a single JSON file, so it works offline and rides along with any file sync. It does not fetch study material, grade free-form answers with a model, or plan a curriculum.

## When to Use

- Learner says "quiz me", "review this", "test me", or "what's due today".
- A study session produced a few facts worth retaining instead of re-reading.
- Learner wants the weak items (lapses) or the mastered ones.

Don't use for: explaining a concept for the first time (teach it, then add items) or looking up a fact on demand.

## Prerequisites

- Python 3.9+, standard library only.
- Output language: system locale by default; override with `--lang zh|en` or `DRILL_LANG`. `--json` keys stay English.
- Writable data directory. Default `data/reviews.json` under the skill; override with `DRILL_STORE=/abs/path/reviews.json` to keep one store per subject or per device.

## How to Run

```bash
python3 scripts/drill.py due --limit 5
python3 scripts/drill.py card 3
python3 scripts/drill.py reveal 3          # only after the learner answered
python3 scripts/drill.py grade 3 --result right
```

## Quick Reference

| Command | Purpose |
|---|---|
| `due [--limit N] [--topic T] [--json]` | Items due today, earliest due date first |
| `card <id>` | Question only |
| `reveal <id>` | Answer plus source |
| `grade <id> --result right\|partial\|wrong [--note TEXT]` | Score and reschedule |
| `add --topic T --question Q --answer A [--source S] [--tags a,b]` | Add one item, due today |
| `import <file\|->` | Bulk add from a JSON array or `{"items": [...]}` |
| `stats [--json]` | Counts by status, due today, due within 3 days |
| `list [--topic T] [--status new\|learning\|mastered]` | Inspect items |
| `edit <id> [--topic/--question/--answer/--source]` | Fix wording or source |
| `rm <id>` | Delete an item |
| `note --topic T --text "..."` | Append one dated line to `data/notes/<topic>.md` |
| `selftest` | Assert scheduling rules without touching the store |

Never hand-edit the JSON during a session; re-run the command instead.

## Procedure

1. `due --limit 5`. If nothing is due, say so and ask whether to add items or learn something new. Done when either a list or an explicit "nothing due" is stated.
2. One item per turn: `card <id>`, wait for the learner's answer, then `reveal <id>`. Done when the answer was revealed only after the learner spoke.
3. Grade against the stored answer: `right` complete, `partial` right direction but a key detail missing, `wrong` contradicts it. A right mechanism with the wrong name is `partial`, not `right` — choosing the correct acronym while calling it by its neighbour's localized name shows the distinction was never learned. Name what was missing, then `grade`. Done when each asked item has exactly one grade.
4. If the learner asks for the answer outright, bargain once ("one more guess, no penalty"), then give it and immediately ask a reverse question on the same fact.
5. Close with `stats` and one takeaway via `note --topic <topic> --text "..."`. Done when stats print and one note line is written.

## Scheduling Rules

`INTERVALS = [1, 3, 7, 15, 30]` and `MASTERED_STREAK = len(INTERVALS) + 1` live at the top of `scripts/drill.py`.

| Result | Streak | Next due | Status |
|---|---|---|---|
| right | +1 | interval at the new index (1 → 3 → 7 → 15 → 30 d) | learning |
| right after the last interval | +1 | none | mastered |
| partial | reset to 0 | +1 day, index unchanged | learning |
| wrong | reset to 0, index 0, lapses +1 | +1 day | learning |

Mastered items are never scheduled again and are skipped by `due`. Grading a mastered item `right` does not recount it.

## Localization

- CLI and generated page chrome exist in English and Chinese (`scripts/i18n.py`, `assets/i18n.js`); add a language by adding one key to both tables.
- Course content is authored in one language. Only the shell (buttons, labels, step counter, map states) switches.
- `README.md` is Chinese and `README.en.md` mirrors it; references and SKILL.md stay English-only to keep instruction density high.
- Page language resolution order: saved choice in `localStorage` → `window.__COURSE_LANG` from the scaffold → `navigator.language`.

## Content Rules

- One fact per item; ask for a decision or a cause, not a recitation.
- Answers stay at one or two sentences. If it needs a paragraph, split the item.
- `topic` is a short `domain/subtopic` label (e.g. `networking/subnetting`), never a file name or date.
- `source` names where the fact comes from (book, page, doc path) so a wrong answer can be traced; never "the previous chat".
- At most five new items per session.
- After two consecutive `wrong` results, split the item into smaller ones and say why in its `note`.

## Teaching Discipline (optional)

`references/teaching-style.md` holds an opinionated classroom style: diagnose before teaching, one concept per step, progressive disclosure, predict-then-reveal only for partially known material, and a strict accuracy rule for numbers and device roles. Load it when actually teaching; the mechanics above work without it.

## New Subject → New Course (default for fresh material)

When the learner starts a subject rather than reviewing one, do not emit loose pages: scaffold a course, then fill it chapter by chapter.

```bash
python3 scripts/new_course.py <dir> --title "Networking basics" \
  --chapters "Devices|what each box does,Layer 2: VLAN|one switch, several groups,Layer 3: IP and gateway|crossing groups"
```

The script creates `index.html` (course map with progress), `ch01.html`…`chNN.html`, `assets/{course.css,course.js,i18n.js,course-data.js,terms-data.js}`, and an empty `术语.json`. Chapter titles may carry a `|description`. Upgrading an older course to a newer shell is a separate recipe in `references/course-layout.md`.

Conventions (details in `references/course-layout.md`):

- Start with 5 to 7 chapters; `00` is always the map. The count is a ceiling on what is taught at once, not a cap on the course: when review shows a whole role chain was never introduced (who installs a virtual network function vs who manages it afterwards), add a chapter in role order instead of a paragraph in chat.
- For any subject with hardware — networks, servers, data centres — one chapter is physical: racks, which box sits where, how many cables per server, uplink speeds, A/B zones. Logical chapters alone leave "why two NICs, why two switches" unanswerable, and a quiz on device roles then fails even though every logical page was read. Place the physical chapter right after the role chapter and before any device-role quiz.
- One concept per page. A follow-up question patches the chapter it belongs to; a genuinely new concept becomes a new chapter, not a new page beside the course.
- Every page: title + one-line lead, diagram with a fixed side table, previous/next/restart, one-line caption per step (≤ 25 words), terms for the current step, chapter pager.
- All pages share `assets/`; never fork the stylesheet per chapter.
- Open with `file://` after each edit. No reload polling, no local server. Open first, verify second with `check_svg_overlap.py` plus DOM step checks; never a screenshot-plus-vision pass.

## After the learner finishes a course

A blank answer after "I read every page" is a content gap, not a memory gap. Handle it as such.

1. Grade the item `wrong` with a note naming the gap; do not re-ask the same item in the same turn.
2. Find the concept the item depends on. If the course never introduced it, the fix is a page change: patch the chapter it belongs to, or add one chapter that walks the chain in role order. A definition in chat is not a fix — the learner reads pages, not the transcript.
3. Re-test that item on the next scheduled day, not immediately after teaching; the scheduler already carries it.
4. If the learner names several related terms as unknown (`EMS MANO NFVO VNFM VIM`), treat them as one chain and teach the chain once, top-down, instead of five separate definitions.

## Lesson Pages (optional, single page)

`references/html-lessons.md` covers the one-page form: skeleton, progressive steps, field tables beside the diagram, fast animation, `?step=N` assertions, the `file://` JSON pitfall, and the pre-delivery self-check (`scripts/check_svg_overlap.py` plus one rendered look). Start from `templates/lesson-page.html`; `scripts/build_index.py` builds an entry page and `scripts/build_terms.py` turns a terms JSON into a `<script>`-loadable data file.

## Pitfalls

- **`fetch()` is blocked on `file://`.** Convert JSON data to a `.js` file that assigns a global and load it with `<script src>` when pages are opened from disk.
- **A corrupted store exits instead of writing.** By design. Back up, fix, rerun; never let the script silently recreate an empty store.
- **Due dates are local calendar days.** A learner crossing timezones may see items a day early or late; migrate data deliberately rather than switching to UTC ad hoc.
- **Double grading.** One grade per review; re-running `grade ... right` on a mastered item is ignored.
- **Import needs all three fields.** Every row requires `topic`, `question`, `answer`.
- **A step's picture is a factual claim.** Verify each step's fields against the real mechanism in both directions; a wrong state (e.g. a transit tag left on the payload at delivery) teaches the inverse model and the learner spots it before you do.
- **A term chip renders empty when the key is missing from `术语.json`.** Adding a chapter that uses new terms requires adding those entries and rerunning `build_terms.py`; otherwise the row is blank and looks broken.
- **Two abbreviations with near-identical localized names teach each other's meaning.** `EMS` (Element Management System) and `VNFM` (VNF Manager) both read as "网元管理…"; a learner who says "the element manager" may mean either. When such a pair appears, one term card must contrast them in a line (EMS governs a running element's config and alarms; VNFM creates and scales the element), and an answer that swaps the names is `partial`.
- **A logical-roles course introduces no physical referents.** After chapters on VLANs, gateways and routing, the learner can still be unable to answer "why two NICs per server, why two switches". That is a coverage gap, not a memory gap: add the physical chapter described under course conventions, then quiz.
- **SVG paints in document order.** A connector written after the node groups covers the boxes it crosses, and a straight line between two distant nodes cuts through whatever sits between them. Put connectors first, route elbows around containers, and run the overlap check before opening the page.

## Verification

- `python3 scripts/drill.py selftest` prints `selftest ok` and asserts interval math, mastery, wrong reset and partial handling.
- `python3 -m unittest discover -s tests -v` passes against a temporary `DRILL_STORE`.
- Smoke test: `DRILL_STORE=$(mktemp)/d.json` then `add`, `due`, `card`, `reveal`, `grade right`, `stats`; the item moves to a future date and status `learning`.
