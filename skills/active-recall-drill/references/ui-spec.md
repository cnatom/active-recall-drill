# Course page visual spec

The shell the learner approved. `templates/course/assets/course.css` and `course.js` implement it; copy them, do not restyle per course.

## Layout order (top to bottom)

1. **Nav** — one row only: course-map link, chapter pills scrolling horizontally, language switch at the right. Never wrap to a second row; never increase the padding to fit more pills.
2. **Header** — chapter number, title, one sentence of lead. Compact: about 18 px top padding.
3. **Step caption** — a speech bubble directly above the figure. White background, 1 px border, 12 px radius, small tail at the lower left pointing down at the diagram. Font 16.5 px, weight 500. It is the sentence for the current step and part of the figure, not a control and not body copy.
4. **Figure + side table** — as described in `html-lessons.md`.
5. **Cards / notes** — two cards at most, each one sentence.
6. **Follow-up appendix** (optional) — `.extra` section, a `<details>` block titled by the question, collapsed by default. Never placed between steps.
7. **Dock** — fixed to the viewport bottom, one row: previous / next / restart, step counter, term chips, and the `复制上下文` button at the right. It stays visible while scrolling; the body reserves padding equal to its height.

## Interactions

- **Chapter pills**: a vertical mouse wheel over the strip scrolls it horizontally (`scrollLeft += deltaY`, only when the strip overflows, and only when the gesture is vertical). A wheel-only mouse must be able to reach the last chapter.
- **Keyboard**: `←`/`→` trigger previous/next step; `↑`/`↓` open the previous/next chapter. Ignore the handler while focus is in `input`, `textarea` or `contenteditable`, and do nothing at the first/last chapter instead of wrapping.
- **`复制上下文`**: copies `【课程进度】` plus current chapter, file, `第 N 步 / 共 M 步`, chapters visited and a timestamp. Derived from the page itself, never from a server, a file picker or a background process.
- No full-screen overlay: a capture-phase listener is enough, and an overlay swallows the learner's real clicks.

## Rules that came from rejected versions

| Rejected | Why | Spec |
|---|---|---|
| Tinted band with accent border for the step caption | read as decoration, "AI-flavoured" | plain speech bubble |
| Step caption inside the bottom control bar | caption belongs to the figure, learner lost it while scrolling | bubble above the figure |
| Two-row nav and three-row dock | wasted half the viewport | one row each, pills scroll |
| Follow-up answers appended as extra steps or chapters | inflated the main flow with material that was not in the course design | `.extra` + `<details>` at the bottom |
| Screenshot + vision review | too slow, learner cancelled it twice | geometry script + DOM checks |

## Numbers

- Nav: 5 px vertical padding, pills 12 px, gaps 5 px.
- Dock: 6 px vertical padding, chips 12 px, caption ellipsised when too long.
- Step bubble: margin 14 px top, 20 px bottom (tail needs the space).
- Content max width 1080 px; body bottom padding = dock height + 18 px.

## Changing the shell

Edit `templates/course/assets/course.css` / `course.js` first, then copy both into the live course's `assets/` so every chapter picks it up at once. Existing courses keep their own copy; a shell change must be applied to each course directory explicitly, and the change recorded in that course's worklog.
