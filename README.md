# Active Recall Drill

离线间隔重复复习工具：先出题，等作答，再揭示，按 1/3/7/15/30 天自动排下一次复习。数据是一个本地 JSON 文件，不联网，除 Python 标准库外没有依赖。

可作为任意智能体的 Skill 使用，也能当普通命令行工具。

中文 | [English](README.en.md)

## 功能

- **先猜后揭**：出题与揭示是两条命令，答案默认不跟着题面出现。
- **间隔排期**：答对按 1→3→7→15→30 天推进，走完再对一次标记为已掌握；半对退回 1 天，答错重置。
- **本地数据**：题库是纯 JSON，可读、可 diff、可随网盘同步。
- **双语**：命令行与课程页面壳支持中英文，默认跟随系统语言，可 `--lang` 覆盖。
- **课程脚手架**：一个主题生成一门课（课程地图 + 章节页 + 共享样式 + 术语表），不只是一张页面。

## 安装

通过 skills.sh 安装：

```sh
npx skills add cnatom/active-recall-drill --skill active-recall-drill
```

需要 Node.js / npx 执行安装命令；运行只需 Python 3.9+，没有第三方包。

也可以直接克隆当 CLI 用：

```sh
git clone https://github.com/cnatom/active-recall-drill
python3 active-recall-drill/skills/active-recall-drill/scripts/drill.py --help
```

## 使用

安装后直接对智能体说：

> 考我今天该复习的题。

> 把这段内容做成 5 道复习题。

> 帮我为这个主题建一门课。

手动用时：

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

## 使用须知

数据只存在本地，不上传、不调模型判分；判分由使用者或智能体对照答案完成。

## License

[MIT](LICENSE). Copyright 2026 cnatom.
