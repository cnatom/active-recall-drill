# 数据模型

## 文件

默认 `data/reviews.json`，可用 `DRILL_STORE` 覆盖。写入是原子的：先写 `*.tmp` 再 `replace`，解析失败时脚本直接退出，不覆盖原文件。

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

## 字段

| 字段 | 含义 |
|---|---|
| `id` | 自增整数，只用于命令行引用 |
| `topic` | `领域/主题` 短标签，统计按它分组 |
| `question` / `answer` | 题面与答案，答案一到两句 |
| `source` | 出处，答错时回查 |
| `status` | `new` 未复习过，`learning` 在学，`mastered` 已掌握 |
| `due` | 下次复习日期（本地日历日，`YYYY-MM-DD`）；`mastered` 时为空 |
| `streak` | 连续答对次数 |
| `interval_idx` | 已走过的间隔下标，`-1` 表示还没对过 |
| `lapses` | 答错次数，用于找薄弱题 |
| `reviews` | 逐次评分流水，含时间、结果、备注 |

## 状态迁移

```
new --(right)--> learning, interval_idx 0, due +1d
learning --(right)--> interval_idx +1, due +INTERVALS[idx]；越界后转 mastered
learning --(partial)--> streak 0, interval_idx 不变, due +1d
learning --(wrong)--> streak 0, interval_idx 0, lapses +1, due +1d
mastered --(right)--> 不变，命令提示已掌握，不重复计数
```

`INTERVALS = [1, 3, 7, 15, 30]`，`MASTERED_STREAK = 6`：走完全部五个间隔后再对一次才算掌握。

## 兼容性

- `version` 目前为 1；新增字段按向后兼容方式追加，不改既有字段含义。
- 手工合并两份库时按 `id` 取并集并重排 `next_id`，再核对 `due`；不要按文件时间覆盖。
