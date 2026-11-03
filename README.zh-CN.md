# Active Recall Drill（中文）

[English](README.md) | 中文

离线间隔重复工具：先出题，等作答，再揭示，评分后按 1/3/7/15/30 天自动排下一次复习。数据是一个 JSON 文件，不上传、不联网，除 Python 标准库外没有依赖。

它既是 Agent Skill，也能当普通命令行工具用。

## 与常见抽认卡的区别

- **先猜后揭**：`card` 只给题面，答案是单独一条命令；偷看答案是刻意的一步。
- **数据可读可 diff**：`data/reviews.json` 是纯 JSON，字段见 `references/data-model.md`。
- **为 Agent 陪学设计**：技能里写明了怎么判分、一次最多入几道、连续答错怎么拆题。

## 安装

作为 Hermes 技能：

```bash
git clone <repo-url> ~/.hermes/skills/learning/active-recall-drill
```

作为独立 CLI，克隆到任意目录后：

```bash
python3 scripts/drill.py --help
```

多个题库用环境变量 `DRILL_STORE` 分开，例如 `DRILL_STORE=~/notes/networking.json`。

## 用法

```bash
python3 scripts/drill.py add --topic 网络/子网 \
  --question "10.0.1.5 和 10.0.2.7 在 /24 下同网段吗？" \
  --answer "不同。前三个数字固定，10.0.1 与 10.0.2 不一样。" \
  --source "Kurose & Ross 第 4 章"

python3 scripts/drill.py due --limit 5
python3 scripts/drill.py card 1
python3 scripts/drill.py reveal 1
python3 scripts/drill.py grade 1 --result right
python3 scripts/drill.py stats
```

批量导入支持 JSON 数组或 `{"items": [...]}`，见 `examples/items.sample.json`。

## 排期

| 评分 | 下次复习 |
|---|---|
| right | 1 → 3 → 7 → 15 → 30 天，之后标为已掌握 |
| partial | 推 1 天，连对清零 |
| wrong | 推 1 天，间隔清零，记一次失误 |

已掌握的题不再出现在 `due`。规则常量在 `scripts/drill.py` 顶部（`INTERVALS`、`MASTERED_STREAK`）。

## 语言

- 命令行默认跟随系统语言（`LANG` / `LC_ALL`），可用 `--lang zh|en` 或 `DRILL_LANG` 覆盖。
- `--json` 输出的字段永远是英文，便于脚本处理。
- 课程页面（`new_course.py` 生成）带语言切换按钮，默认取脚手架时的语言，用户切换后记在 localStorage。

## 数据

```
data/reviews.json     题库（第一次 add 时创建）
data/notes/<topic>.md 每次会话一句小结
```

`data/` 已被 gitignore，全部留在本地。

## 附带工具

- `scripts/new_course.py <目录> --title "..." --chapters "A,B,C"`：生成多章课程骨架（课程地图、章节页、共享 assets、空术语表）。
- `scripts/build_index.py <dir>`：为一堆单页教学页生成入口。
- `scripts/build_glossary.py <terms.json>`：生成可搜索术语表。
- `scripts/build_terms.py <terms.json>`：术语转 `assets/terms-data.js`，让页面在 `file://` 下可用。
- `templates/lesson-page.html`：单页骨架；`templates/course/`：整门课骨架。

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 scripts/drill.py selftest
```

## 许可

MIT，见 `LICENSE`。
