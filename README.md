# Active Recall Drill

A small, offline spaced-repetition tool for people who study with an agent. Ask the question, wait for the answer, reveal, grade — the store then schedules the next review at 1, 3, 7, 15, 30 days. One JSON file, no accounts, no network, no dependencies beyond the Python standard library.

It ships as an [Agent Skill](https://hermes-agent.nousresearch.com/docs) and also works as a plain command-line tool.

## Why another SRS

- **Predict-then-reveal, not flashcard flipping.** `card` shows only the question; the answer is a separate command, so the temptation to peek is a deliberate step.
- **One file you can read, diff and sync.** `data/reviews.json` is plain JSON with a stable schema (`references/data-model.md`).
- **Built for agent-driven study.** The skill tells the agent how to score, when to stop adding items, and how to split an item that keeps failing.

## Install

As a Hermes skill:

```bash
git clone <repo-url> ~/.hermes/skills/learning/active-recall-drill
```

As a standalone CLI, clone anywhere and run:

```bash
python3 scripts/drill.py --help
```

Set `DRILL_STORE` to keep separate stores, e.g. `DRILL_STORE=~/notes/networking.json`.

## Usage

```bash
# add three facts studied today
python3 scripts/drill.py add --topic networking/subnetting \
  --question "Do 10.0.1.5 and 10.0.2.7 share a subnet under /24?" \
  --answer "No. /24 fixes the first three octets; 10.0.1 differs from 10.0.2." \
  --source "Kurose & Ross, ch. 4"

# daily loop
python3 scripts/drill.py due --limit 5
python3 scripts/drill.py card 1
python3 scripts/drill.py reveal 1
python3 scripts/drill.py grade 1 --result right
python3 scripts/drill.py stats
```

Bulk import accepts either a JSON array or `{"items": [...]}`; see `examples/items.sample.json`.

## Scheduling

| Result | Next review |
|---|---|
| right | 1 → 3 → 7 → 15 → 30 days, then mastered |
| partial | +1 day, streak reset |
| wrong | +1 day, interval reset, lapse counted |

Mastered items stop appearing in `due`. Rules live in `scripts/drill.py` (`INTERVALS`, `MASTERED_STREAK`).

## Data

```
data/reviews.json     the store (created on first add)
data/notes/<topic>.md one dated line per session takeaway
```

`data/` is git-ignored. Everything stays local; nothing is uploaded.

## Extras

- `scripts/new_course.py <dir> --title "..." --chapters "A,B,C"` — scaffold a multi-chapter HTML course (map, chapter pages, shared assets, empty terms file). See `references/course-layout.md`.
- `scripts/build_index.py <dir>` — entry page for a folder of HTML lessons.
- `scripts/build_glossary.py <terms.json>` — standalone searchable glossary.
- `scripts/build_terms.py <terms.json>` — converts terms to `assets/terms-data.js` so lessons work from `file://`.
- `templates/lesson-page.html` — lesson skeleton; conventions in `references/html-lessons.md`.
- `references/teaching-style.md` — an opinionated one-to-one teaching style (Chinese) for zero-background learners.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 scripts/drill.py selftest
```

## 中文

一个离线间隔重复工具：先出题、等作答、再揭示、评分，之后按 1/3/7/15/30 天自动排下一次复习。数据是一个 JSON 文件，不上传、不依赖第三方库。

```bash
python3 scripts/drill.py due --limit 5     # 今天该复习什么
python3 scripts/drill.py card 1            # 只出题面
python3 scripts/drill.py reveal 1          # 作答后再揭示
python3 scripts/drill.py grade 1 --result right
```

CLI 输出为英文，便于脚本与跨语言使用；数据字段同样为英文。教学风格说明见 `references/teaching-style.md`，页面写法见 `references/html-lessons.md`。

## License

MIT. See `LICENSE`.
