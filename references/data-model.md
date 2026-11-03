# Data model

## File

Default `data/reviews.json`; override with `DRILL_STORE`. Writes are atomic (`*.tmp` then `replace`), and a parse failure exits without touching the original file.

```json
{
  "version": 1,
  "next_id": 2,
  "items": [
    {
      "id": 1,
      "topic": "networking/subnetting",
      "question": "…",
      "answer": "…",
      "source": "Kurose & Ross, ch. 4",
      "tags": ["subnet"],
      "status": "learning",
      "due": "2026-11-05",
      "created": "2026-11-02T21:10:00+08:00",
      "last_reviewed": "2026-11-03T09:02:11+08:00",
      "streak": 1,
      "interval_idx": 0,
      "lapses": 0,
      "reviews": [
        {"date": "2026-11-03T09:02:11+08:00", "result": "right", "note": ""}
      ]
    }
  ]
}
```

## Fields

| Field | Meaning |
|---|---|
| `id` | Auto-increment integer, only used to address items on the command line |
| `topic` | Short `domain/subtopic` label; `stats` groups by it |
| `question` / `answer` | Prompt and answer; the answer stays at one or two sentences |
| `source` | Where the fact comes from, for tracing a wrong answer |
| `status` | `new` never reviewed, `learning` in rotation, `mastered` done |
| `due` | Next review date (local calendar day, `YYYY-MM-DD`); empty when mastered |
| `streak` | Consecutive correct answers |
| `interval_idx` | Index of the interval already walked; `-1` means never correct |
| `lapses` | Wrong-answer count, used to spot weak items |
| `reviews` | Per-review log: timestamp, result, note |

## Transitions

```
new      --(right)-->   learning, interval_idx 0, due +1d
learning --(right)-->   interval_idx +1, due +INTERVALS[idx]; past the end → mastered
learning --(partial)--> streak 0, interval_idx unchanged, due +1d
learning --(wrong)-->   streak 0, interval_idx 0, lapses +1, due +1d
mastered --(right)-->   unchanged; the command reports it as mastered, no recount
```

`INTERVALS = [1, 3, 7, 15, 30]`, `MASTERED_STREAK = 6`: all five intervals plus one more correct answer.

## Compatibility

- `version` is 1. New fields are appended in a backward-compatible way; existing fields keep their meaning.
- To merge two stores by hand, union by `id`, renumber `next_id`, then re-check `due`; do not pick a winner by file timestamp.
