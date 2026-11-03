# Single-file HTML lessons

One page per concept, opened straight from disk. The page carries the explanation; chat carries one sentence and the path. `templates/lesson-page.html` is the starting skeleton.

## Page skeleton

1. Title plus one line of context (no more).
2. Diagram and a fixed field table side by side: the diagram holds nodes and one moving dot; the table shows the packet or item fields for the current step.
3. Step caption directly above the diagram, as a plain speech bubble: white, hairline border, 12 px radius, small tail pointing down at the figure, 16.5 px at weight 500. It is part of the figure, not a control; a tinted band reads as decoration and plain body styling makes it disappear. Exact values in `ui-spec.md`.
4. Controls (previous / next / restart) and the "terms on this step" row docked to the bottom of the viewport: two or three terms, each expanding to `ABBR｜full name｜plain name: one sentence`.
5. Chapter pager at the bottom when pages form a course.

## Drawing rules

- Short labels only: abbreviations or two-to-three-character role names. Full names never go on the diagram — a 180-310 px box overflows and covers connectors.
- Full names live in hover tooltips (`title`) and the term row.
- Field values (source IP, MAC, VLAN tag) belong in a fixed side table, never in a floating card that follows the moving dot; the card always covers a node label at some frame.
- Structural relationships get a static diagram; anything that changes over time gets stepped animation.

## Timing

- Movement 200-300 ms per segment; change flash 0.2 s; autoplay step gap 250 ms.
- Colour distinguishes direction (outbound vs return) faster than text does.
- Highlight only what changed; keep everything else neutral.

## Fidelity of each step

Every step's visible state is a factual claim. Check it against the real mechanism, not against what looks tidy.

- Encapsulation is symmetric: whatever is added at ingress is removed at the far end. If the terminal host is shown still holding the transit wrapper, the page teaches the wrong model.
- Terminal delivery shows the payload as the terminal actually receives it (untagged frame, decoded value), never "with the transit header still on".
- When a learner's question exposes a contradiction between two steps, fix the state arrays of both; patching only the step they looked at leaves the same error one click away.
- Before adding a step, read its fields aloud as a sentence ("at this point the frame carries X, addressed to Y"). If the sentence is false, the step is false.

## State and checks

- Support `?step=N` for deep links and headless assertions.
- Assert logic, not pixels: load with headless Chrome and read the DOM.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --virtual-time-budget=3000 --dump-dom "file:///abs/path/page.html?step=3" \
  | grep -o 'id="msg">[^<]*'
```

- Do not build screenshot-plus-vision review loops; screenshot review is banned outright (see "Order of operations"). Read the DOM instead.

## Page chrome: both bars one row, caption in the body

Chrome that eats vertical space is a defect: the learner reads diagrams, so anything fixed to the top or bottom must stay a single row and give the height back to the figure.

- **Top nav**: brand, chapter pills and the language toggle on one line. Pills scroll horizontally (`overflow-x: auto; flex-wrap: nowrap`, hidden scrollbar) instead of wrapping to a second line; padding 4-6 px, pill font ~12 px.
- **Bottom dock**: one flex row holding the three buttons, the step counter and the term chips. Buttons come from `.bar`, judged by `display: contents` so its children join the dock row; the caption is *not* in the dock. Long captions ellipsize there only if they stayed; in the current design they sit above the figure.
- **Term definition**: absolutely positioned above the dock (`bottom: calc(100% + 4px)`), so expanding a term never grows the bar.
- **Body padding**: `dock.offsetHeight + 18px` reserved on load and resize, otherwise the last paragraphs hide behind the dock.
- **Caption**: speech bubble above the figure — white, 1 px border, 12 px radius, tail at lower left, 16.5 px / 500 weight, 14 px above and 20 px below (the tail needs the space). Tinted bands and caption-inside-the-dock were both rejected.
- Header padding stays ≤ 20 px so the diagram starts high on the page.

## Order of operations: open first, verify second

The learner wants to see the new state immediately, and does not want to wait for the teacher's self-review. So the order is fixed:

1. **Edit** the page.
2. **Open it right away** (`open <file>`), before any check runs. One sentence in chat says what changed.
3. **Then verify without looking at pixels**: `python3 scripts/check_svg_overlap.py page.html [--allow l0,...]` (must print `no collisions`) and a DOM check of the first and last `?step=N`.
4. **Fix silently and reopen** if a check fails; report the fix in one line. Do not hold the page back until the checks pass.

Screenshot-plus-vision review is banned: the learner rejected it twice as too slow. Geometry and DOM checks are the substitutes — keep the collision script current (it scans every `<svg>` block) instead of adding new visual tooling.

## Opening pages and data on file://

- Open pages with `file://` and no local server; no reload-polling either, because a page that reloads itself loses the user's step and needs manual scrolling back.
- `fetch('terms.json')` fails on `file://`. Generate `assets/terms-data.js` with `scripts/build_terms.py` and load it via `<script src>` before the page script; the page then reads `window.__TERMS`.
- Keep the JSON as the editable source and the generated `.js` as the runtime artifact; do not hand-edit the generated file.

## Course layout

- Pages live next to the studied material in a `可视化/` (or `lessons/`) folder, never scattered on the desktop.
- Each page carries `<title>` and `<meta name="note" content="one line">`; `scripts/build_index.py <dir>` renders the entry page from those two fields.
- Shared CSS and JS go in `assets/`; keep one stylesheet so the chapters look like one course.
- Chapter order encodes dependencies. Do not let the learner jump before the prerequisite chapter.
- Progress is tracked in `localStorage` under a single key; mark a chapter visited on load and highlight the current one.

## Reworked mistakes

| Symptom | Cause | Fix |
|---|---|---|
| "It overflows the container" | full names drawn inside the diagram | abbreviations on the diagram, full names in tooltips |
| "This part is bad" | floating field card covering nodes | fixed side table, one moving dot only |
| "Animation is too slow" | 700 ms moves, 650 ms gaps | 300 ms per segment at most |
| "Too much at once" | layer table, rules and terms all on one page | hide or delete anything not needed at the current step |
| "Terms should not be a separate page" | standalone glossary page | terms inline per step, generated from one JSON |
| "I have to click back to the page every time" | reload-polling hot reload | open the page after each edit instead |
| "上下区域太大了" | nav wrapping to rows, dock stacking caption above terms | one row each; caption moved into the body |
| "描述性文字跟普通文字一样" | caption left at body font weight | speech bubble: border, tail, 16.5 px / 500 |
| "追问内容占用了主体" | follow-up answer appended to the step flow | `.extra` + `<details>` appendix at the page bottom |
| connector through a cabinet | straight line between distant nodes, drawn after the nodes | connectors first, elbows outside the container row, `check_svg_overlap.py` |
