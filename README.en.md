# Active Recall Drill

Offline spaced-repetition review: show the question, wait for the answer, reveal, then schedule the next review at 1, 3, 7, 15 and 30 days. The store is one local JSON file — no network, no third-party packages.

Works as a Skill for any agent, and as a plain command-line tool.

[中文](README.md) | English

## Features

- **Predict then reveal**: the question and the answer are separate commands, so the answer does not appear next to the prompt.
- **Spaced scheduling**: 1 → 3 → 7 → 15 → 30 days on correct answers, mastered after one more pass; partial backs off a day, wrong resets.
- **Local data**: plain JSON, diffable, syncs with any file sync.
- **Bilingual**: CLI and course page shell in English and Chinese, following the system locale, overridable with `--lang`.
- **Course scaffolder**: one subject becomes a course (map + chapter pages + shared assets + glossary), not a pile of pages.

## Install

From skills.sh:

```sh
npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

Node.js / npx is needed for the install command only; running needs Python 3.9+ and nothing else.

Or clone and use it as a CLI:

```sh
git clone https://github.com/cnatom/active-recall-drill
python3 active-recall-drill/skills/active-recall-drill/scripts/drill.py --help
```

## Usage

Once installed, just tell the agent:

> Quiz me on what is due today.

> Turn this into five review questions.

> Build a course for this subject.

Or run it yourself:

```sh
python3 scripts/drill.py due --limit 5
python3 scripts/drill.py card 1
python3 scripts/drill.py reveal 1
python3 scripts/drill.py grade 1 --result right
```

Keep separate stores with `DRILL_STORE=/path/reviews.json`.

## Docs

- [Data model](skills/active-recall-drill/references/data-model.md)
- [Course layout](skills/active-recall-drill/references/course-layout.md)
- [Lesson pages](skills/active-recall-drill/references/html-lessons.md)
- [Teaching style](skills/active-recall-drill/references/teaching-style.md)

## Notes

Everything stays local: no upload, no model grading — the learner or the agent grades against the stored answer.

## License

[MIT](LICENSE). Copyright 2026 cnatom.
