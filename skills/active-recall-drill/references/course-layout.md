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

## Fixed page shape

1. Small chapter number, title, one-line lead (what this chapter solves).
2. Body: diagram left, table right. The diagram holds nodes and one moving dot; field values live in the fixed table, never in a floating card.
3. Step caption directly above the diagram (it is part of the figure). Controls dock to the viewport bottom with the term row (`assets/course.js` moves `.bar` and `.terms` into `.dock`).
4. Terms for this step: two or three, expanding to `ABR｜full name｜local name: one line`.
5. Chapter pager: previous / next.
6. Follow-up Q&A that is not part of the chapter goes into `<section class="extra"><details>…</details></section>` at the bottom, collapsed by default; it never enters the step array or the chapter list.

The `S` array is the only content source, one entry per step:

```js
const S = [
  { msg: 'one line', pos: [x, y], a: 'field one', b: 'field two', terms: ['VLAN', 'L2'] },
];
```

## Progress, navigation, language

- `#cnav` is injected by `assets/course.js`; the current chapter is highlighted and visited chapters are marked.
- Progress lives under one `localStorage` key (`netcloud-course-progress` by default; change it at the top of `course.js`).
- The chapter list lives in `assets/course-data.js`; generated. Add a chapter there and create the matching html.
- UI strings live in `assets/i18n.js`. Language resolution: saved choice → `__COURSE_LANG` → `navigator.language`. The nav has a one-click switch. Content stays in one language; only the shell is translated.

## Delivery and checks

- After every edit, `open <absolute path>` and work over `file://`; no reload polling, no local server.
- Data files (terms) must be converted to `.js` before a `file://` page can read them.
- Assert with `?step=N` and a headless DOM read instead of screenshots:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --virtual-time-budget=3000 --dump-dom "file:///abs/path/ch03.html?step=4" \
  | grep -o 'id="msg">[^<]*'
```

## Maintenance

- Edit terms only in `术语.json`, then run `scripts/build_terms.py 术语.json`; never hand-edit `terms-data.js`.
- Visual and pacing rules: `html-lessons.md`. Teaching rhythm: `teaching-style.md`.

### Adding a chapter to a running course

Do this when review exposes a missing concept, and keep the new page indistinguishable from the rest.

1. Copy the nearest chapter file to `chNN.html` and replace title, kicker (`data-num`), lead, the `S` array and the step count in the initial label.
2. Keep the include order `course-data.js` → `i18n.js` → `terms-data.js` → `course.js`, then the inline script.
3. Register the chapter in `assets/course-data.js` with `num`, `id` (`chNN`), `title`, `file`, `desc`; the map, nav pills and pager read only that array, so no other page needs editing.
4. Add every new term used by the page to `术语.json`, then `python3 scripts/build_terms.py 术语.json`; a missing key renders a blank chip.
5. Verify with a headless dump of the last step (`?step=<last>`): the final caption, the highlighted element and the term chips must all be present; then `open` the page.

## Retrofitting an existing course to a newer shell

When `templates/course/assets/` gains a feature (nav, language switch), existing course directories keep working on the old copy — every page hardcodes its script includes and chrome labels, so nothing updates by itself.

1. Copy `course.css`, `course.js`, `i18n.js` from `templates/course/assets/` over the course's `assets/`.
2. Move the chapter array out of `course.js` into a generated `assets/course-data.js` (`window.__COURSE_LANG`, `window.__COURSE_CHAPTERS`); the current `course.js` reads data only and no longer holds the list.
3. In every page keep this script order: `course-data.js` → `i18n.js` → `terms-data.js` → `course.js`; the inline page script runs last.
4. Replace hardcoded chrome with `data-i18n="prev|next|restart|terms"`, the chapter kicker with `data-i18n="chapterOf" data-num="01"`, step counters with `courseT('stepOf', { i, n })`, and map states with `courseT('visited'|'notStarted')`.
5. Verify without clicking: copy the course to a temp dir, set `__COURSE_LANG = "en"` in `course-data.js`, then headless-dump one chapter and grep for `Chapter`, `Next`, `Step`.

Content language is untouched: the switch translates the shell only.
