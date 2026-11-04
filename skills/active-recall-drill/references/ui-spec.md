# Course page visual spec

The shell the learner approved. `templates/course/assets/course.css` and `course.js` implement it; copy them, do not restyle per course.

## Layout order (top to bottom)

1. **Nav — two rails.** The left 课程地图 rail is 212 px and lists modules only (plus 术语表 and the language switch). Immediately to its right, a 196 px 目录 rail is the table of contents: one collapsible group per level-1 category (章节分组), chapters (`NN title`) as level-2 items inside, and only the group containing the current chapter open. Content and the dock start at 408 px (`body { padding-left: 408px }`, `.dock { left: 408px }`). Below 1200 px the 目录 rail is hidden and the content keeps a 212 px offset; below 900 px both rails collapse to the one-row top bar with horizontally scrolling module pills. The chapter list never sits in the 课程地图 rail again. The 目录 rail itself collapses: a `收起目录 / 目录 ›` button under the module list sets `body.toc-collapsed` (persisted in `localStorage`), the rail animates to zero width and the content and dock move back to 212 px; groups inside the rail expand and collapse natively via `<details>`.
2. **Header** — chapter number, title, one sentence of lead. Compact: about 18 px top padding.
3. **Points list** — inside `.side`, beside the figure, nothing else in the rail. One column, every point visible at once, numbered, ordered 由浅入深 (what it is → how it works → what it means). One sentence per point, bold lead phrase, badge number. The figure carries `data-p` links but no printed numbers; hovering a figure part highlights the matching point.
4. **Figure + tables** — one complete figure; nothing hidden or dimmed. Field tables never share the points rail: they go full-width in `.tables` below the stage, or, when the rail is taller than the figure, at the foot of the `.fig` column so neither column is left hundreds of pixels empty.
5. **Cards / notes** — two cards at most, each one sentence. The plain-language layer is a **visual analogy** (`.analogy` block: small SVG scene labelled `生活中的样子`), not a text paragraph; place it after the points and before the dock.
6. **Follow-up appendix** (optional) — `.extra` section, a `<details>` block titled by the question, collapsed by default. Never placed between points.
7. **Dock** — fixed to the viewport bottom, one row: term chips for the whole page and the `复制上下文` button. No step counter and no step buttons; chapter switching stays on the pager and `↑/↓`. The body reserves padding equal to its height.

## Interactions

- **Chapter labels**: on the desktop rail they scroll vertically like any list; the horizontal-wheel handler only applies to the collapsed mobile strip, where a vertical wheel over the strip scrolls it horizontally (`scrollLeft += deltaY`, only when the strip overflows and the gesture is vertical).
- **Hover linking**: figure parts carry `data-p`, and `assets/hover-points.js` dims every non-matching numbered point to ~35 % (still legible) while hovering; leaving the figure restores all points to 100 %. Hovering a point mirrors the highlight on the figure. The figure itself carries no printed numbers and no badge circles: the circled numbers exist only in the rail list, so delete any badge-generation block that reappears. No clicks, no step state.
- **Keyboard**: `↑`/`↓` open the previous/next chapter. Ignore the handler while focus is in `input`, `textarea` or `contenteditable`, and do nothing at the first/last chapter instead of wrapping. There is no `←`/`→` step binding because pages have no steps.
- **`复制上下文`**: copies `【课程进度】`, `当前：<num> <title>（<file>）`, `进度：已看过 N / M 章`, `已看过：` with indented lines of four chapters each (`  01 …、02 …、03 …、04 …`), and `时间：YYYY-MM-DD HH:MM`. No step line. Derived from `localStorage` and the chapter array, never from a server, a file picker or a background process.
- No full-screen overlay: a capture-phase listener is enough, and an overlay swallows the learner's real clicks.

## Rules that came from rejected versions

| Rejected | Why | Spec |
|---|---|---|
| Per-step caption bubble | fragmented reading; the learner asked to see every point at once | numbered points list beside one complete figure |
| Two-row nav and three-row dock | wasted half the viewport | dock stays one row; chapters move to the left rail |
| Horizontal chapter pills across the top (19 chapters) | scroll hunting; the learner asked for a vertical rail | fixed left rail, one stacked label per chapter |
| Fading nodes in and out per step | learner could not assemble the whole picture and asked for one complete diagram | full figure always visible; hover lights the matching point |
| Manual prev/next step switching | learner refused to click through fragments ("完全取消分步骤") | numbered points all visible under one complete figure |
| Follow-up answers appended as extra steps or chapters | inflated the main flow with material that was not in the course design | `.extra` + `<details>` at the bottom |
| Screenshot + vision review of shell geometry | too slow, learner cancelled it twice | geometry script + DOM checks + pixel samples; one vision read of a dense figure for label legibility is allowed |

## Numbers

- Nav rails: 课程地图 212 px with module labels only; 目录 196 px with 12 px group summaries and 12.5 px chapter items, 1 px gap, 4 px vertical padding, current item on the accent-soft background.
- Collapsed mobile bar: 5 px vertical padding, pills 12 px, 5 px gaps.
- Dock: 6 px vertical padding, chips 12 px, caption ellipsised when too long, offset 408 px from the left on desktop (212 px between 900 and 1200 px).
- Points list: one column, the only content of `.side`, 13 px text, 8 px gap, 20 px badge, 8 px inner padding; it moves below the figure only in the mobile stack.
- Figure column: the points rail takes ~290 px, so the SVG keeps at least 380 px; a viewBox wider than 900 units uses `.stage.wide` and moves the rail below the figure.
- Analogy block: 12 px padding, 12 px caption, full-width SVG; it sits after the points and before the dock.
- Content max width 1080 px; body bottom padding = dock height + 18 px.
- Stage columns: `.fig` (figure only) and `.side` (points only) should end within ~150 px of each other. Field tables in `.tables` below the stage stretch the page evenly; if the rail is still much taller, move the tables to the foot of `.fig`, and if the figure is much taller, leave them full-width below. Never ship a column with a few hundred pixels of blank canvas.

## Layout verification

DOM dumps prove text, links, points count and term chips; they say nothing about geometry. For a shell change (rail width, dock offset, column split) do a pixel check instead of a vision pass:

1. Render at the real width: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --window-size=1440,900 --screenshot=/tmp/nav.png "file:///abs/page.html"`.
2. Sample columns with PIL: 课程地图 background at x ≈ 60, its border at x ≈ 211, 目录 background at x ≈ 300, its border at x ≈ 407, content background at x ≈ 420, dock background only to the right of x = 408.
3. A rail that overlaps content, a dock still anchored at x = 0, or a page whose `body` padding was never applied each show up as the wrong colour in one of those samples.

A default 800×600 headless window is below the 900 px breakpoint, so it renders the mobile top bar; pass `--window-size` explicitly when checking the rail.

## Typography inside diagrams

The earlier spec set no font sizes, so a 1100-unit-wide viewBox squeezed into a 700 px column scaled 11 px labels down to ~7 px and the learner could not read them.

- **Layout decides legibility first**: a diagram with more than ~15 nodes, or any viewBox wider than 900 units, uses `.stage.wide` — the figure spans the full content width and the side table moves below it. Never shrink a wide diagram into the two-column slot.
- **Minimum SVG font 11.5 units**; node title 14, secondary line 12, annotation/footnote 11.5. Nothing below 11, ever (no 10 px labels).
- **No dimmed nodes**: step-free pages show everything at full opacity. Point at a region through `data-p` hover highlighting and a light callout, never by fading the rest to grey and never by stamping numbers on the artwork.
- Effective size is what counts: with the diagram at full width a 900-unit viewBox renders near 1:1, so 12 units ≈ 12 px on screen.

## End-to-end flow figure

A business-flow page (request → provisioning → workload running → result back) uses one wide figure, not a second sidebar.

- **U-shaped chain**: 6–7 boxes, top row left → right, a vertical arrow down the right edge, bottom row right → left ending at the system that confirms completion. Each box carries a small lane label (`OSS`, `MANO · NFVO`, `资源 · VIM`, `控制 · SDNC`, `网元 · VNF`), a title, and one subtitle line.
- **Put the interface name in the subtitle** (`经 Or-Vnfm 调用，先申请 Grant`). Do not float separate interface labels in the narrow gaps between boxes: a 10–11-unit label is wider than a 40-unit gap and lands on the arrowhead or the box border. Folding the name into the box removes that class of collision entirely.
- **Keep box subtitles at 11.5 units minimum**, same floor as every other diagram label; a 10-unit subtitle reads as fine print at 1440 px.
- Below the figure: numbered steps in two columns (left 1–4, right 5–7), one line each, ending with a short failure/rollback paragraph. The steps repeat the figure in words; the figure never relies on the steps to be understood.

## Changing the shell

Edit `templates/course/assets/course.css` / `course.js` first, then copy both into the live course's `assets/` so every chapter picks it up at once. Existing courses keep their own copy; a shell change must be applied to each course directory explicitly, and the change recorded in that course's worklog.
