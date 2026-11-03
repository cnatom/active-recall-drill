# Active Recall Drill

离线间隔重复复习。出题、作答、揭示，然后按 1/3/7/15/30 天排下一次。题库是一个本地 JSON 文件，不联网，不需要第三方包。

中文 | [English](README.en.md)

## 功能

- 出题与揭示是两条命令，答案不会跟着题面一起出现。
- 答对按 1 → 3 → 7 → 15 → 30 天推进，走完再对一次记为已掌握；半对退回一天，答错重置。
- 命令行与课程页面壳有中英两套，默认跟随系统语言，`--lang` 覆盖。
- 一条命令生成多章课程页面：课程地图、章节页、共享样式、术语表。

## 安装

```sh
npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

交给智能体执行：

```text
安装技能：npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

安装要 Node.js；运行只要 Python 3.9+。

克隆后用 CLI：

```sh
git clone https://github.com/cnatom/active-recall-drill
python3 active-recall-drill/skills/active-recall-drill/scripts/drill.py --help
```

## 使用

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

## 文档

- [数据模型](skills/active-recall-drill/references/data-model.md)
- [课程形态](skills/active-recall-drill/references/course-layout.md)
- [单页教学页规范](skills/active-recall-drill/references/html-lessons.md)
- [教学风格](skills/active-recall-drill/references/teaching-style.md)

## 须知

题库与笔记只存在本地，不联网；判分由使用者或智能体对照答案完成。

## License

[MIT](LICENSE). Copyright 2026 cnatom.
