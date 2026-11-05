---
name: active-recall-drill
description: Drill recall and build visual courses from notes.
version: 1.25.1
author: cnatom
license: MIT
compatibility: Python 3.9+ with the standard library; any agent that can run shell commands.
metadata:
  tags: [learning, spaced-repetition, recall, quiz, course]
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
- All paths below are relative to this skill directory, whatever directory the agent installed it into.
- Public mirror: `github.com/cnatom/active-recall-drill` installs via `npx skills add cnatom/active-recall-drill` and keeps the skill at `skills/active-recall-drill/`. This local copy is the working source; fold each change into the mirror, bump `version` and prepend the CHANGELOG entry in one release, or the installed copies silently fall behind.
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
- Course content is authored in one language. Only the shell (buttons, labels, map states) switches.
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

`references/teaching-style.md` holds an opinionated classroom style: diagnose before teaching, one concept per page, progressive disclosure (now: one complete figure plus points ordered 由浅入深), predict-then-reveal only for partially known material, and a strict accuracy rule for numbers and device roles.

A single concept question gets one or two sentences naming the distinguishing mechanism; detail belongs on the page or in the note, not in chat. When the learner asks for a term definition mid-course, answer that short and then patch the page if the page itself was unclear.

Answer category first. When the question is "what IS this, a concept, a device or a protocol", the first sentence classifies it (architecture, protocol, device, role) and gives the one test that decides membership, then the parts. A component list before the category leaves the learner unable to place the term and asking again.

Assume no telecom background even though the learner works at a carrier. Expand every acronym at first use in the lead, keep one name per object, and prefer the everyday word over the standards word (`插头` before `收发器`). Only the term card carries the formal name.

Load `references/teaching-style.md` when actually teaching; the mechanics above work without it.

## New Subject → New Course (default for fresh material)

When the learner starts a subject rather than reviewing one, do not emit loose pages: scaffold a course, then fill it chapter by chapter.

```bash
python3 scripts/new_course.py <dir> --title "Networking basics" \
  --chapters "Devices|what each box does,Layer 2: VLAN|one switch, several groups,Layer 3: IP and gateway|crossing groups"
```

The script creates `index.html` (course map with progress), `ch01.html`…`chNN.html`, `assets/{course.css,course.js,i18n.js,course-data.js,terms-data.js}`, and an empty `术语.json`. Chapter titles may carry a `|description`. Upgrading an older course to a newer shell is a separate recipe in `references/course-layout.md`.

Conventions (details in `references/course-layout.md`):

- Start with 5 to 7 chapters; `00` is always the map. That count is a ceiling on what is taught at once, not a cap on the course: a production system grows to 10-15 chapters along the coverage chain in `references/course-layout.md` (roles → physical → redundancy → how services attach → isolation → addressing/numbering → real topology → management plane → operations → automation). Add in role order instead of explaining the missing link in chat, keep one concept per chapter, and never let two chapters carry the same title after a reorder.
- For any subject with hardware — networks, servers, data centres — one chapter is physical: racks, which box sits where, how many cables per server, uplink speeds, A/B zones. Logical chapters alone leave "why two NICs, why two switches" unanswerable, and a quiz on device roles then fails even though every logical page was read. Place the physical chapter right after the role chapter and before any device-role quiz.
- One concept per page. A follow-up question patches the chapter it belongs to; a genuinely new concept becomes a new chapter, not a new page beside the course.
- Every chapter carries one visual analogy: a small SVG scene labelled `生活中的样子`, placed under the technical figure and above the dock, mapping the mechanism to an everyday scene (traffic control centre, building floors, courier parcel, two gatekeepers). It is a picture, not a paragraph: the learner with zero telecom background should be able to retell the mechanism from the scene plus one caption line. Keep diagram labels plain function words, put the acronym in the term card, and never put a number or device name in the analogy that the step does not also show.
- A page that explains an architecture also needs the end-to-end flow: from the top-level system that raises the request (OSS/portal) through every layer to the workload running, then the result and alarms travelling back. Draw the sequence as a U-shaped chain of labelled boxes in one figure, put each interface name in the box subtitle rather than floating it between boxes, and follow it with one line per step plus what happens on failure and rollback. Figure recipe: `references/ui-spec.md` → End-to-end flow figure.
- When the learner can follow the pages but cannot present the material, add a spoken walkthrough to every chapter that has a figure, one chapter at a time and topology chapter first: that chapter gets four plain beats (structure → management layer → one business path → one-line distinction), a simpler chapter gets three beats on its own figure; each ends with a 30-second version and five likely questions with one-line answers. Add it per chapter as the learner asks, not as one course-wide outline. Write speaking notes, not prose: short factual sentences, no "remember that", no slogan or metaphor ("司令部", "落点"), no em dashes, no parallel triads. The walkthrough goes after the flow section and before the terms. Recipe: `references/teaching-style.md` → Spoken walkthrough.
- If the learner supplies a reference architecture (a vendor or 集团 slide), reproduce every module, layer and interface label from it. A simplified "essence" diagram reads as cutting corners and will be rejected; draw the full stack, keep interface labels legible with a white halo (`paint-order: stroke`), and let the numbered points do the explaining.
- Never hide, fade or grey out parts of the figure to stage a story. The learner reads the whole picture first and found the fragments hard to reassemble; every box, label and connector stays visible from step 0. Cross-highlighting replaces steps: each figure part carries `data-p="1"` (or `data-p="2,5"`) and `assets/hover-points.js` lets hovering that part light its numbered point while the other points drop to about 35 % opacity but stay legible; leaving the figure restores every point to full opacity, and hovering a point mirrors the highlight on the figure. Do not print the numbers on the figure itself: the circled numbers live only in the right-rail points list. The points sit beside the figure, never far below it. If a mechanism really is sequential (encapsulation, failure and failover), draw the sequence as labelled frames side by side in one figure.
- Merge chapters instead of letting the course grow by accretion: one `<h1>`, and each additional concept opens with `<h2 class="part">` plus a one-line `.partlead`, keeping its own complete figure and points rail below.
- Wide figures do not stretch the page: put the SVG in `.mapview`, a fixed-height (`clamp(440px, 64vh, 700px)`) framed canvas that pans by dragging and zooms with the wheel or the `－ / ＋ / 复位` buttons, with the points in a 300 px rail beside it. Content is fluid up to 1560 px (`.wrap` and the dock inner), so a wide window has no empty side margins. Start at 100 % when the frame is at least 860 px wide and 135 % below that. The frame carries `按住拖动查看细节，滚轮缩放`; a detached instruction line or a sticky figure taller than the viewport was rejected. Contract: `references/ui-spec.md` → wide figure.
- Navigation has two vertical rails, never one long list: the left 课程地图 rail lists modules only, and the 目录 rail beside it shows level-1 chapter groups with their level-2 chapters, only the current group expanded. Keep the chapter list out of the 课程地图 rail; it grows past the viewport on any real course. Both rails collapse independently through a button attached to each rail (collapsed rail keeps a 28 px strip), and the level-1 groups expand and collapse natively. A control that collapses a panel belongs on that panel; detached floating handles were rejected. The active level-1 item carries `.cur`, and the 目录 rail always shows that item's children only: an item with no children (a reference page registered in `window.__COURSE_REFS`) hides the rail and its toggle entirely instead of leaving the previous item's chapters on screen.
- Every page: title + one-line lead, one complete figure (nothing hidden, no per-step dimming), a numbered points list beside the figure in the right rail with every point visible at once and ordered 由浅入深, then the note, the `生活中的样子` analogy figure, and the term chips. The stage is two columns: `.fig` holds the SVG and nothing else, `.side` holds only the points list. Field tables go in a full-width `.tables` block below the stage; when the points rail is taller than the figure, they move to the foot of the `.fig` column instead. Either way, neither column may be left with a few hundred pixels of empty space — measure `.fig` and `.side` heights after any layout edit and rebalance until the gap is under ~150 px. No step controls and no `?step` state: the learner must not click through fragments. Dock carries the term chips and `复制上下文` only; chapter switching stays on the pager and `↑/↓`. Full contract and rejected variants: `references/ui-spec.md`; converting a legacy step-based course: `references/course-layout.md` → Converting to step-free.
- A single external document that needs its own walkthrough (a 规范, a vendor deck, a design doc) gets a standalone reference page at the course root, not a new chapter and not a slide of prose: sections run 全局 → 局部 (总体架构 → 组网链路 → 分区与安全 → 编号 → 地址/AS → 落地配置), each with one complete figure, its own points rail, and a table where the source is tabular. Register it in `window.__COURSE_REFS` (in `assets/course-data.js`) so the rail renders it as a level-1 item with a selected state and hides the 目录 rail while it is open; keep it out of `course-data.js` so it has no number, pager entry or progress. Terms used by the page still go through `术语.json` and the chips call. Recipe: `references/course-layout.md` → Standalone source-document page.
- Loose facts that belong to no single chapter go into the reference page `notes.html` (细碎知识), not into chapter prose: one question per collapsible card with a one-line answer and a source, stored in `assets/notes-data.js`, searchable and filterable by category. Layout and empty-state contract: `references/ui-spec.md` → Reference page. A real artifact the learner meets at work — an alarm, a device code, a vendor term — becomes a nugget card in the same turn: explain it in a few sentences in chat, then add the card with how to read it, what causes it, and the first checks, source marked 现网/同事, and label any step still awaiting field confirmation. Add a term card too when the abbreviation is new.
- Terms are a hard gate, not a nicety: every abbreviation that appears in a page's visible text must already have a card in `术语.json`. Add it in the same edit that introduces it, rerun `build_terms.py`, then run `python3 scripts/check_terms.py <course-dir>` and do not finish while it exits non-zero. `showTerms` auto-appends every ASCII term it finds in the page, so a missing card shows up as a blank chip; Chinese term keys still have to be passed explicitly.
- Terms live in `术语.json`; a step-free page shows its whole term set as chips through one `showTerms('tchips', [...])` call after `course.js`. After adding or editing pages run `python3 scripts/check_terms.py <course-dir>`; it diffs every page's `terms:` array against the JSON and exits non-zero on a key that has no card. Every page also gets a global term search: a floating `术语 ⌘K` button opens an overlay with an input and result list (`/` or ⌘K anywhere, Enter opens the first hit, Esc closes), and the arrow-key chapter shortcuts are suppressed while it is open. A standalone glossary page is allowed when the learner wants to memorise them: cards with the abbreviation always visible and independent toggles for the English full name and the Chinese explanation (`遮住英文`, `遮住中文`, `只看缩写` hides both), a card click revealing what is masked, plus `全部遮住/翻开`, `随机一张` and search. Link it from the nav as its own pill; it stays outside the chapter sequence.
- Follow-up material produced while answering questions goes into a `.extra` section at the bottom inside `<details>`, never into the main step flow or the chapter list; the chapter sequence stays what it was when the course was designed.
- All pages share `assets/`; never fork the stylesheet per chapter.
- Open with `file://` after each edit. No reload polling, no local server. Open first, verify second with `check_svg_overlap.py` plus DOM checks of the points list and chips. Shell geometry is checked by pixel sampling, never by a vision pass; one vision read of a dense figure for label legibility is allowed under Verification.

## Knowing which chapter the learner is on

No daemon and no file access: the page cannot write to disk from `file://`, and both a recorder server and a file-picker sync were rejected as inelegant.

- The bottom dock carries a `复制上下文` button that copies a short block for pasting into the chat. Exact shape, no step line: `【课程进度】`, then `当前：<num> <title>（<file>）`, then `进度：已看过 N / M 章` (M excludes the map page), then `已看过：` followed by indented lines of four chapters each (`  01 …、02 …、03 …、04 …`), then `时间：YYYY-MM-DD HH:MM`. Long chapter lists on one line are unreadable in chat; wrapping four per line is the accepted format.
- When such a block arrives, treat it as authoritative for this turn: resume from that chapter, and do not ask again which page they are reading.
- Without a pasted block there is no signal; ask instead of guessing. Never claim to watch the screen, and do not reintroduce a background recorder or a full-screen overlay without an explicit request.

## After the learner finishes a course

A blank answer after "I read every page" is a content gap, not a memory gap. Handle it as such.

1. Grade the item `wrong` with a note naming the gap; do not re-ask the same item in the same turn.
2. Find the concept the item depends on. If the course never introduced it, the fix is a page change: patch the chapter it belongs to, or add one chapter that walks the chain in role order. A definition in chat is not a fix — the learner reads pages, not the transcript.
3. Re-test that item on the next scheduled day, not immediately after teaching; the scheduler already carries it.
4. If the learner names several related terms as unknown (`EMS MANO NFVO VNFM VIM`), treat them as one chain and teach the chain once, top-down, instead of five separate definitions.

## Change requests on a running course

Learners take these courses chapter by chapter, and they usually ask for a small concrete change long before they have read every page. Their reading position lives only in their own browser `localStorage`, so never assume a chapter has been seen.

- Do exactly what was asked, at the size asked. "Move the directory" means move the directory: no module split, no renumbering, no page plan attached.
- Scope the course to what the learner asked about or handed over. Every chapter must trace to a question they asked or a file they supplied; the remaining sections of a spec, a course number, or a syllabus is not a mandate to build pages. A large unread map is not progress, and this learner will say so.
- When growth is explicitly asked for, split the directory into modules first (recipe in `references/course-layout.md`), then add only the new chapters. Do not bundle content expansion, renumbering and page rewrites into one change.
- Do not answer a one-line request with a roadmap. Module tables, target page counts, priorities and phases for material the learner has not opened yet are noise, not planning. Expansion is proposed when they ask for new content or report finishing the current sequence, and then one module at a time.
- A relocation is a whole-directory move. Every page and the terms data use relative paths (`assets/…`, `术语.json`), so move the folder as a unit, change nothing inside, headless-dump one page to confirm `assets/` still resolves, then update the single index line that names the old path.
- When a layout or interaction change is meant as a convention rather than a one-off tweak, backport it in the same pass: a running course's `assets/course.css` and `course.js` are copies of `templates/course/assets/`, so edit the template and `references/ui-spec.md` (plus `course-layout.md` when navigation or file layout changes), then commit and push the skill repo. A convention left only in the course diverges on the next scaffold and the learner has to ask for it again.
- Renaming, renumbering and relocating are three separate operations. Combining them turns a one-command move into a multi-file rewrite and breaks the `localStorage` progress ids keyed on `data-chapter`.

## Lesson Pages (optional, single page)

`references/ui-spec.md` is the visual contract: left rail, one complete figure, numbered points list, visual analogy, dock, appendix, with the rejected variants and their replacements. `references/html-lessons.md` covers the drawing mechanics: skeleton, field tables, fast animation, the `file://` JSON pitfall, and the pre-delivery geometry check (its step-array sections describe the legacy shell). Start from `templates/lesson-page.html`; `scripts/build_index.py` builds an entry page and `scripts/build_terms.py` turns a terms JSON into a `<script>`-loadable data file.

## Pitfalls

- **`fetch()` is blocked on `file://`.** Convert JSON data to a `.js` file that assigns a global and load it with `<script src>` when pages are opened from disk.
- **A corrupted store exits instead of writing.** By design. Back up, fix, rerun; never let the script silently recreate an empty store.
- **Due dates are local calendar days.** A learner crossing timezones may see items a day early or late; migrate data deliberately rather than switching to UTC ad hoc.
- **Double grading.** One grade per review; re-running `grade ... right` on a mastered item is ignored.
- **Import needs all three fields.** Every row requires `topic`, `question`, `answer`.
- **A figure's state is a factual claim.** Verify every drawn field against the real mechanism in both directions; a wrong state (e.g. a transit tag left on the payload at delivery) teaches the inverse model and the learner spots it before you do.
- **A term chip renders empty when the key is missing from `术语.json`.** Adding a chapter that uses new terms requires adding those entries and rerunning `build_terms.py`; otherwise the row is blank and looks broken. Check every page, not just the one you edited: a chip added in an earlier pass goes unnoticed until the learner opens that page, so run `scripts/check_terms.py <course-dir>` before delivery.
- **Appending to `notes-data.js` needs the comma.** The file is a JS array of objects; a missing `,` between two entries leaves the reference page blank while the HTML still loads, because the script throws before assigning the global. After every edit run `node --check assets/notes-data.js` and assert the rendered card count in a headless dump, not just that the file opens.
- **A .docx is not a clean XML read.** `python-docx` can reject an archive whose zip lists a `NULL` entry, and a naive `<w:t[^>]*>` regex also matches `<w:txbxContent>`, spraying raw XML into the text. Extract by splitting on `</w:p>` and matching `<w:t(?:\s[^>]*)?>(.*?)</w:t>`, then dedupe: text-box content repeats the same paragraph two or three times.
- **A headless dump taken too early reads as a broken shell.** At 900 ms the nav can still show 0 pills because `course.js` has not run; poll until `window.COURSE_LANG` is a string or re-dump at ≥1.5 s before concluding a script failed. The error is timing, not syntax.
- **Stacked labels teach neither name.** A diagram box labelled `vSwitch（VTEP）` assumes the learner already knows one of the two terms; a non-telecom learner reads it as one confusing object and asks what it means. Label the box with its plain function (`软件交换机，负责封包与拆包`) and leave the acronym to the term chip and glossary. Same rule for prose: never introduce two names for one box in the same sentence.
- **Two abbreviations with near-identical localized names teach each other's meaning.** `EMS` (Element Management System) and `VNFM` (VNF Manager) both read as "网元管理…"; a learner who says "the element manager" may mean either. When such a pair appears, one term card must contrast them in a line (EMS governs a running element's config and alarms; VNFM creates and scales the element), and an answer that swaps the names is `partial`.
- **When the learner says two terms are indistinguishable, teach the contrast, not the definitions.** Give each word the object it changes (`SDN defines the network's path; NFV virtualizes the device`), add one points-list item that states the contrast and one callout on the figure, and add two or three drill items. Longer prose in chat is the failure mode: they already read the page once and forgot it, so the fix is a shorter hook plus a scheduled recall, not more explanation.
- **A logical-roles course introduces no physical referents.** After chapters on VLANs, gateways and routing, the learner can still be unable to answer "why two NICs per server, why two switches". That is a coverage gap, not a memory gap: add the physical chapter described under course conventions, then quiz.
- **A mechanism chapter needs a failure frame, not just a description.** When a component exists to survive something (escape port, peer-link, standby gateway), a card saying "used when the uplink fails" does not teach why it is needed. Since pages are step-free, draw the normal frame and the failed frame side by side in the one figure, with the traffic visibly leaving through the mechanism; the learner's question "what triggers it, why is it necessary" is the signal that the description alone failed.
- **A figure with no `data-p` is inert, and nothing else catches it.** Pages copied before hover-linking existed still render, still pass the points/chips check, and still look finished; only a hover test shows that nothing lights up. After a merge, rename or scaffold, audit interaction per stage across all chapters, not only the page just edited, and treat a stage that has a points list but no `[data-p]` as unfinished.
- **SVG paints in document order.** A connector written after the node groups covers the boxes it crosses, and a straight line between two distant nodes cuts through whatever sits between them. Put connectors first, route elbows around containers, and run the overlap check before opening the page. The moving dot is a node too: a coordinate that reads as "inside the box" usually lands on a label baseline and hides a line of text, so park it on empty canvas or below the box. The checker ignores paint order: a connector emitted before the boxes is painted over and invisible, yet still reported as a collision. Confirm the paint order before rerouting; only a line that actually shows through the box is a defect.
- **Scripted HTML restructuring silently drops wrappers.** Moving blocks across a batch of pages (tables out of the rail, SVG into a `.fig`) with regex or index slicing can leave out the opening `<div class="stage">`, close a parent early, or eat the `.note` block; the page still renders, so only a later measurement or the learner sees a missing section. After any batch rewrite, assert every page has balanced `<div>`/`</div>` counts, the expected `.stage`/`.fig`/`.side` counts, and that `.note`, `.terms` and `.pager` still resolve with `.wrap` as parent; then measure column heights. When replacing one whole `<section>`, cut to the next `<section` tag rather than searching for the next identical heading: a heading that appears twice (a failed previous replace) makes the slice swallow the section in between. After the edit list every `<h2>` in order and assert each expected section is present exactly once; a missing or duplicated number is the signal.
- **A base rule written after a media query silently wins at every width.** Appending `body { padding-left: 408px }` or `.dock { left: 408px }` after the `max-width: 900px` block overrides the mobile layout while the media query still reports as applied. Put each breakpoint's offsets in a media block that comes after the base rule (or add `!important` only for the offset), and after any nav change read computed values at 1440, 1100 and 900 px: 目录 rail visible only above 1200 px, content offset 408 / 212 / 0, dock left matching. The page looks fine at desktop width while being broken on the laptop the learner actually uses.
- **Don't hand-animate `<details>` height.** Driving `open` with `requestAnimationFrame` plus a `height` transition and clearing it on `transitionend` leaves the panel stuck at `height: 0` whenever that event is missed, and headless virtual time misses it every time. Let `<details>`/`<summary>` toggle natively; if a smooth reveal is required, keep the animation CSS-only and verify the final state with transitions disabled. The same rule applies to the collapsible 目录 rail: inline width plus a CSS transition is fine, but the verification pass must disable the transition first.
- **Chapter numbers live in `course-data.js`, not in filenames.** A reorder rewrites `num` and the array order but keeps file names, so `第 05 章` can sit in `ch08.html`. Read the sequence from the data array, never from a filename sort; do not "fix" the names during an unrelated change, and never delete a page as a duplicate because two numbers look swapped.

## Verification

- Layout changes: screenshot at a fixed viewport (`--headless --window-size=1440,900 --screenshot=…`) and sample pixels with PIL instead of opening the page or a vision pass. With two rails, check 课程地图 background at `(60, 400)`, its border at `x=211`, 目录 background at `(300, 400)`, its border at `x=407`, content background at `(420, 400)`, and the dock offset at `x=408`; then repeat the DOM measurement at 1100 px (no 目录, offset 212) and 900 px (top bar, offset 0). A wrong rail width, a dock still starting at 212, or a 目录 rail that refuses to hide shows up as a pixel or computed-style mismatch. A screenshot taller than `document.scrollHeight` is blank canvas at the bottom, not a missing section: compare the document height before treating that white space as a layout defect, and photograph the region you actually changed. At 1700 px, read the computed `.wrap` width and assert it uses the available space up to 1560 px with no horizontal overflow; a 1080 px cap leaves the side margins the learner complains about. For a `.mapview`, verify panning by comparing `scrollLeft` before and after a synthetic pointer drag and zooming by the canvas width plus the `%` label; a sticky figure or one taller than the viewport is the wrong shape. Animated columns read their start value under headless virtual time: a rail with `width: 0px` inline still reports 196 px computed, so inject `#tocnav{transition:none!important}` (or measure with transitions disabled) before calling it a CSS bug.
- Hover linking is per `.stage`, and every chapter with a figure must answer. Loop every `.stage` of every page, dispatch `mouseover` on its first `[data-p]`, and assert `.hot` ≥ 1 and `.dim` = its points − hot; a stage returning 0/0 has no listener, and a stage that has points but no `[data-p]` is a missing interaction, not an intentionally plain figure. `hover-points.js` binds each stage to the list in its own `.side`, so a merged page keeps independent highlighting; a single global binding silently breaks the second figure because its list restarts at 1. Where an SVG has no group wrappers, add transparent `<rect data-p="…" fill="transparent"/>` hotzones before `</svg>`. A `mouseleave` on the svg clears `.hot`, `.dim` and `.ph`. Figures carry no printed numbers: a `.pbadge` count above zero means a stale badge generator must be deleted.
- Dense reference diagrams: the geometry script does not read text, so give one rendered screenshot a single vision read for labels sitting on connectors or clipped at the edge before delivery, then fix with a white text halo (`paint-order: stroke`) or by moving the label. This is not the banned full visual review of shell geometry — it is a legibility check on one figure.
- Diagram geometry is a separate gate from the static checker: after any figure edit, run the browser audit in `references/ui-spec.md` → Diagram layout rules. Sample every `line`/`path` with `getPointAtLength` at ~5 px and flag points landing inside a non-container `rect` (skip row bands and intentional icon paths like an envelope), then compare every `text` pair's `getBBox` for overlap; fix the route or the label and rerun both. A clean `check_svg_overlap.py` run proves neither — it models no paint order and no text, reports connectors that are painted over by their boxes, and misses a label colliding with another label.
- `python3 scripts/audit_course.py <course-dir>` is the pre-delivery gate for structure and interactions: balanced divs, one `h1`, every stage with a points list and `[data-p]`, `hover-points.js` present, a `生活中的样子` analogy on chapter pages, and no dead local links. It exits non-zero listing offenders; run it after any merge, rename or batch edit.
- `python3 scripts/drill.py selftest` prints `selftest ok` and asserts interval math, mastery, wrong reset and partial handling.
- `python3 -m unittest discover -s tests -v` passes against a temporary `DRILL_STORE`.
- Smoke test: `DRILL_STORE=$(mktemp)/d.json` then `add`, `due`, `card`, `reveal`, `grade right`, `stats`; the item moves to a future date and status `learning`.
