# Active Recall Drill

[![skills.sh](https://img.shields.io/badge/skills.sh-cnatom%2Factive--recall--drill-111)](https://www.skills.sh/cnatom/active-recall-drill)

离线间隔重复复习。出题、作答、揭示，按 1/3/7/15/30 天排下一次。题库是一个本地 JSON 文件，不联网。

中文 | [English](README.en.md)

## 安装

```sh
npx skills add cnatom/active-recall-drill
```

交给智能体执行：

```text
安装技能：npx skills add cnatom/active-recall-drill
```

装到 `.agents/skills/`，Claude Code 走软链，其他 agent 直接读该目录。

只用 CLI：

```sh
git clone https://github.com/cnatom/active-recall-drill
python3 skills/active-recall-drill/scripts/drill.py --help
```

## 用法

```text
考我今天该复习的题。
把这段内容做成 5 道复习题。
为这个主题建一门课。
```

```sh
python3 scripts/drill.py due --limit 5
python3 scripts/drill.py card 1
python3 scripts/drill.py reveal 1
python3 scripts/drill.py grade 1 --result right
```

多个题库用 `DRILL_STORE=/path/reviews.json` 分开。

## 内容

```
skills/active-recall-drill/
├── SKILL.md              流程、评分、入库规则
├── scripts/drill.py      排期库与命令行
├── scripts/i18n.py       中英文案
├── scripts/new_course.py 多章课程脚手架
├── scripts/build_*.py    入口页、术语表、术语数据
├── references/           数据模型、课程形态、页面规范、教学风格
└── templates/            单页与整门课的 HTML 模板
tests/                    标准库单元测试
.github/workflows/        CI
```

## 要求

安装要 Node.js；运行只要 Python 3.9+，无第三方包。

## 须知

题库与笔记只存在本地，不联网；判分由使用者或智能体对照答案完成。

## License

[MIT](LICENSE). Copyright 2026 cnatom.
