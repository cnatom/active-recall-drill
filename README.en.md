# Active Recall Drill

[![skills.sh](https://img.shields.io/badge/skills.sh-cnatom%2Factive--recall--drill-111)](https://www.skills.sh/cnatom/active-recall-drill)

Offline spaced repetition: ask, answer, reveal, schedule the next review at 1, 3, 7, 15 and 30 days. The store is one local JSON file; no network.

[中文](README.md) | English

## Install

```sh
npx skills add cnatom/active-recall-drill
```

Ask your agent to run it:

```text
Install the skill: npx skills add cnatom/active-recall-drill
```

Installs into `.agents/skills/`; Claude Code gets a symlink, other agents read the directory directly.

CLI only:

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

## Contents

```
skills/active-recall-drill/
├── SKILL.md              workflow, grading, item rules
├── scripts/drill.py      store and CLI
├── scripts/i18n.py       English and Chinese messages
├── scripts/new_course.py multi-chapter course scaffolder
├── scripts/build_*.py    index, glossary and terms-data builders
├── references/           data model, course layout, lesson pages, teaching style
└── templates/            single-page and full-course HTML skeletons
```

## Requirements

Node.js for the install command; Python 3.9+ to run, no third-party packages.

## Notes

The store and notes stay local; nothing is uploaded. Grading is done by the learner or the agent against the stored answer.

## License

[MIT](LICENSE). Copyright 2026 cnatom.
