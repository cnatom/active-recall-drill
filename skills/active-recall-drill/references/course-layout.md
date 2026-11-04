# Course layout (multi-chapter)

One subject is one course, not a list of pages. Test: after studying, the learner can retell the whole chain in order, not just recall isolated explanations.

## Tree

```
<subject>/
├── index.html            course map: chapter cards + progress
├── ch01.html … chNN.html one page per chapter
├── 术语.json             term source (abbr/full/cn/note/cat/src)
└── assets/
    ├── course.css        the only stylesheet
    ├── course.js         chapter nav, progress, language switch, terms
    ├── i18n.js           UI strings for the shell
    ├── course-data.js    chapter list (window.__COURSE_CHAPTERS, __COURSE_LANG)
    └── terms-data.js     generated from 术语.json for file://
```

Scaffold with:

```bash
python3 scripts/new_course.py <dir> --title "Networking basics" \
  --chapters "Devices|what each box does,Layer 2: VLAN|one switch, several groups"
```

Add `--lang zh|en` to pin the page language; otherwise it follows the system locale.

A course that outgrows one directory moves its pages to `chapters/<module>/`; the recipe is under "Splitting a flat course into modules" below.

## Chapter count and order

- Five to seven chapters. `00` is always the course map and carries no teaching content.
- Order is dependency order: do not teach chapter N+1 before the learner accepts chapter N. Even parallel textbook topics get an order.
- One concept per chapter. A follow-up question patches that chapter with one more picture; only a genuinely new concept becomes a new chapter.
- Hardware subjects get exactly one physical chapter: racks, device positions, cables per server, uplink speeds, A/B zones. It follows the role chapter and precedes any quiz that asks why a device is duplicated; without it the learner reads every logical page and still cannot answer physical questions.

## Coverage chain (what a complete course contains)

A course that stops at the logical layers leaves holes the learner discovers mid-quiz. Cover the chain below; each item is one chapter, in this order, and skip only what the subject genuinely lacks:

1. roles and where each sits;
2. physical form: racks, cables per server, uplink counts and speeds, A/B zones;
3. redundancy: what is paired, how the pair presents as one, what fails over and how fast;
4. how a service attaches (the two or three supported modes and when each is used);
5. isolation and multi-tenancy (VRFs, instances, per-tenant routing);
6. addressing and numbering rules (prefix plan, VLAN classes, unit of allocation);
7. the real topology with its traffic classes;
8. the management plane (who installs, who operates, who orchestrates);
9. operations: failure handling and change handling;
10. automation and the maturity ladder for both.

Design starts at 5-7 chapters, but a production system ends at 10-15. When a quiz answer is blank, find which link of this chain was never taught and add it in place; do not compress two links into one chapter.

## Reordering or renumbering chapters

Chapter numbers are display values; ids stay stable, so a reorder never renames files.

1. Rewrite the order and `num` values in `assets/course-data.js` (array order drives nav pills, the map and the pager).
2. In each moved page update `data-num` on the kicker, the `第 N 章` text and the `<title>` prefix — grep the old number to catch all three.
3. Check for duplicate titles and numbers across chapters; a copy-paste chapter keeps its source's `<h1>` and the map then shows two chapters with the same name.
4. Open the map and one moved chapter; nav highlight comes from `data-chapter`/`id`, so it must still point at the unchanged id.

## Relocating a course directory

Moving the folder is not a reorder. A course the learner is part-way through has progress in `localStorage` keyed by chapter id, and every page hardcodes relative `assets/…` includes, so a move must keep filenames, ids and the internal layout unchanged.

1. `mv` the whole directory. Nothing inside points at an absolute path, so `assets/…` keeps resolving and no page needs editing.
2. Update the one place that names the old path (the library index / README line), and search the library for the old folder name before declaring done.
3. Verify from the new location with a headless last-step dump of two chapters plus the map, not by reading the HTML.
4. Renaming chapters, renumbering, or splitting into module folders is a separate change with its own review. Do not bundle it into a relocation the learner asked for as "just move it" — they are often still working through the pages they already have.

## Splitting a flat course into modules

Do this only when the learner asks to grow the course, and keep every existing id. Progress lives in `localStorage` keyed by `data-chapter`, so a split that renames ids silently wipes what they have read.

1. `mkdir -p chapters/<module>` and move each page to `chapters/<module>/NN-<slug>.html`, numbering by **display order** in `course-data.js`, not by the old file sort (the old files are usually scrambled: chapter 05 may live in `ch08.html`).
2. On every moved page add `data-root="../../"` to `<body>` and rewrite the includes to `../../assets/…`; ids (`data-chapter`), `data-num` and titles stay untouched.
3. Rewrite `assets/course-data.js` as `window.__COURSE_MODULES = [{id, num, title, desc, chapters:[…]}]` plus a flattened `window.__COURSE_CHAPTERS`; page `file` values become root-relative (`chapters/<module>/NN-slug.html`).
4. In `course.js` read `const ROOT = document.body.dataset.root || ''` and prefix every link with it: nav brand, chapter pills, glossary, pager, term-overlay footer. Without this, nav and pager resolve inside the chapter directory and 404.
5. In `index.html` render one card list per module with a module heading, and skip the `index` entry so the map does not link to itself.
6. Add the new chapters as `chapters/<module>/NN-slug.html`, register them in the module array, and add their terms before running `build_terms.py`.
7. Verify: headless-dump every page for a non-empty `.points` list and at least two chips, no `.bar`; check the first page's pager points at the map and the last page's pager closes the sequence; count chapter cards against the data array; run `check_svg_overlap.py` on each new page.

## Converting to step-free

Do this when the learner says steps are too fragmented ("完全取消分步骤") or asks for one complete figure. Chapter ids stay untouched; only the interaction layer changes.

1. Reveal everything: replace both `opacity="0"` attributes and `style="opacity:0"` (hidden table rows and cells) with opacity 1. The old render loop was the only thing showing them.
2. Remove the `#dot` marker, every `<div class="bar">…</div>`, and the inline step script (`<script>` starting with `const S` through its `</script>`). A page with two demos has a second, deeper-indented bar and a second array inside the same script; fold its messages into the same points list and delete both bars.
3. Build `<ol class="points">` from the messages in order (one `<li><span class="n">N</span><div>…</div></li>` each) and insert it before the first `.note` (before `.terms` when the page has no note). Wording written for a step ("再往上") reads fine as a numbered sequence; rewrite only what is unreadable alone.
4. Rebuild the term row: chips used to come from `showTerms` per step. Take the union of every `terms:` array, dedupe, and call `showTerms('tchips', [...])` once after `course.js`; change the label to 本页术语.
5. Check that deleting bars did not eat the terms block: after the rewrite `grep -c 'id="tchips"'` must be 1 on every page. A non-greedy bar match on a page with a second nested bar can swallow the section between them; re-insert the `.terms` block before the pager if it vanished.
6. Pages whose script rewrote table cells (source MAC, route origin) freeze at the first step's values. Either rewrite those cells to state the rule, or caption the table "以第一跳为例" so the shown values are honest.
7. Previously hidden connectors now paint. Run `check_svg_overlap.py` on every page and route or shorten any line that crosses a box; a line hidden behind `opacity="0"` was never checked before.
8. Verify per page with a headless dump: `class="points"` count ≥3, `class="tchip"` ≥2, `class="bar"` = 0; then open two pages.
9. Cross-link figure and points: add `data-p="N"` to each group or box (`data-p="2,5"` when one shape serves several points), include `assets/hover-points.js`, and verify with a synthetic `mouseover` on one `[data-p]` shape: exactly one `.hot`, the rest `.dim`, then `mouseleave` clears them.

## Fixed page shape

1. Small chapter number, title, one-line lead (what this chapter solves).
2. One complete figure inside `.fig`: every box, label and connector visible at full opacity, no `?step` state. Field values live in full-width `.tables` cards below the stage (or at the foot of `.fig` when the points rail is taller), never in the points rail.
3. `<ol class="points">` in `.side`, beside the figure: every point visible at once, numbered, ordered 由浅入深 (what it is → how it works → what it means), one sentence each. No numbers printed on the figure itself; `data-p` links drive hover highlighting.
4. Note, then the `生活中的样子` analogy scene, then the term row. No caption bubble, no bar, no moving dot.
5. Chapter pager: previous / next.
6. Follow-up Q&A that is not part of the chapter goes into `<section class="extra"><details>…</details></section>` at the bottom, collapsed by default; it never enters the points list or the chapter list.

Page content is static HTML. The term row is filled once with the union of the page's terms:

```html
<script>showTerms('tchips', ['SDN','NFV','VXLAN']);</script>
```

There is no `S` array; a page that still has one is a legacy step page (see Converting to step-free).

## Progress, navigation, language

- `#cnav` is injected by `assets/course.js` as a fixed 212 px left rail (course-map link, module label, stacked chapter labels); the current chapter is highlighted and visited chapters are marked. Below 900 px the rail becomes the one-row top bar again.
- Progress lives under one `localStorage` key (`netcloud-course-progress` by default; change it at the top of `course.js`).
- The chapter list lives in `assets/course-data.js`; generated. Add a chapter there and create the matching html.
- UI strings live in `assets/i18n.js`. Language resolution: saved choice → `__COURSE_LANG` → `navigator.language`. The nav has a one-click switch. Content stays in one language; only the shell is translated.

## Delivery and checks

- After every edit, `open <absolute path>` and work over `file://`; no reload polling, no local server.
- Data files (terms) must be converted to `.js` before a `file://` page can read them.
- Assert with a headless DOM read: every page must have a `.points` list, at least two `.tchip`s and no `.bar`:

```bash
out=$( "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --virtual-time-budget=2000 --dump-dom "file:///abs/page.html" )
printf '%s' "$out" | grep -c 'class="points"'; printf '%s' "$out" | grep -o 'class="tchip"' | wc -l
```

- A DOM dump cannot see geometry. After changing the shell (rail width, dock offset, column split, `body` padding) render at `--window-size=1440,900` with `--screenshot` and sample pixels with PIL: rail background left of 212 px, content background right of it, dock background only below its own top edge. Recipe: `references/ui-spec.md` → Layout verification.
- After any scripted restructuring of page markup, assert structure before measuring: `<div>`/`</div>` counts equal per page, `.stage`/`.fig`/`.side` present the expected number of times, and `.note`/`.terms`/`.pager` still resolve with `.wrap` as parent. A batch that drops `<div class="stage">` still renders, and only a height measurement or the learner notices the note vanished.
- Column balance: compare `.fig` and `.side` heights in the headless dump; rebalance tables (below the stage vs at the foot of `.fig`) until the shorter column is within ~150 px of the taller one.

## Maintenance

- Edit terms only in `术语.json`, then run `scripts/build_terms.py 术语.json`; never hand-edit `terms-data.js`.
- Visual and pacing rules: `html-lessons.md`. Teaching rhythm: `teaching-style.md`.

### Adding a chapter to a running course

Do this when review exposes a missing concept, and keep the new page indistinguishable from the rest. If the course is already modular, place the page in `chapters/<module>/`, add `data-root="../../"`, and register the root-relative `file` path; otherwise keep it beside `index.html`.

1. Copy the nearest chapter file to `NN-<slug>.html` (or `chNN.html` in a flat course) and replace title, kicker (`data-num`), lead, the figure, the points list and the terms call.
2. Keep the include order `course-data.js` → `i18n.js` → `terms-data.js` → `course.js`, then the inline terms call.
3. Register the chapter in `assets/course-data.js` with `num`, `id`, `title`, `file`, `desc`; the map, nav rail and pager read only that array, so no other page needs editing.
4. Add every new term used by the page to `术语.json`, then `python3 scripts/build_terms.py 术语.json`; a missing key renders a blank chip.
5. Verify with a headless dump: points present, chips ≥2, no `.bar`; then run `check_svg_overlap.py` and open the page.

## Retrofitting an existing course to a newer shell

When `templates/course/assets/` gains a feature (nav, language switch), existing course directories keep working on the old copy — every page hardcodes its script includes and chrome labels, so nothing updates by itself.

1. Copy `course.css`, `course.js`, `i18n.js` from `templates/course/assets/` over the course's `assets/`.
2. Move the chapter array out of `course.js` into a generated `assets/course-data.js` (`window.__COURSE_LANG`, `window.__COURSE_CHAPTERS`); the current `course.js` reads data only and no longer holds the list.
3. In every page keep this script order: `course-data.js` → `i18n.js` → `terms-data.js` → `course.js`; the inline page script runs last.
4. Replace hardcoded chrome with `data-i18n="prev|next|restart|terms"` and the chapter kicker with `data-i18n="chapterOf" data-num="01"`; map states use `courseT('visited'|'notStarted')`. Step-free pages have no step counter or buttons, so skip `courseT('stepOf', …)` on them.
5. Verify without clicking: copy the course to a temp dir, set `__COURSE_LANG = "en"` in `course-data.js`, then headless-dump one chapter and grep for `Chapter` and `Next` (step-free pages have no `Step` string).

Content language is untouched: the switch translates the shell only.
