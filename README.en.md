# Active Recall Drill

Offline spaced repetition: ask, answer, reveal, then schedule the next review at 1, 3, 7, 15 and 30 days. The store is one local JSON file — no network, no third-party packages.

[中文](README.md) | English

## Features

- Question and answer are separate commands, so the answer never appears with the prompt.
- 1 → 3 → 7 → 15 → 30 days on correct answers; mastered after one more pass; partial backs off a day, wrong resets.
- CLI and course page shell in English and Chinese, following the system locale, overridable with `--lang`.
- One command scaffolds a multi-chapter course: map, chapter pages, shared stylesheet, glossary.

## Install

```sh
npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

Ask your agent to run it:

```text
Install the skill: npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

Install needs Node.js; running needs Python 3.9+.

Clone and use the CLI:

```sh
git clone https://github.com/cnatom/active-recall-drill
python3 active-recall-drill/skills/active-recall-drill/scripts/drill.py --help
```

## Usage

```text
Quiz me on what is due today.
Turn this into five review questions.
Build a course for this subject.
```

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

The store and notes stay local; nothing is uploaded. Grading is done by the learner or the agent against the stored answer.

## License

[MIT](LICENSE). Copyright 2026 cnatom.
