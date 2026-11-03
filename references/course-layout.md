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

## Fixed page shape

1. Small chapter number, title, one-line lead (what this chapter solves).
2. Body: diagram left, table right. The diagram holds nodes and one moving dot; field values live in the fixed table, never in a floating card.
3. Controls: previous / next / restart plus a one-line caption (≤ 25 words).
4. Terms for this step: two or three, expanding to `ABR｜full name｜local name: one line`.
5. Chapter pager: previous / next.

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
- New chapter: add an entry to `course-data.js`, copy the nearest chapter html, replace the title and `S`.
- Visual and pacing rules: `html-lessons.md`. Teaching rhythm: `teaching-style.md`.
