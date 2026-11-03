# 课程形态（多章）

一个主题 = 一门课，不是一个页面列表。判断标准：学完之后要能按顺序复述整条链路，而不是记住几个孤立的解释。

## 目录

```
<主题目录>/
├── index.html            课程地图：章节卡片 + 进度
├── ch01.html … chNN.html 一章一页
├── 术语.json             术语源（abbr/full/cn/note/cat/src）
└── assets/
    ├── course.css        唯一的一份样式
    ├── course.js         章节导航、进度、术语渲染
    ├── course-data.js    章节数组（window.__COURSE_CHAPTERS）
    └── terms-data.js     由 术语.json 生成（file:// 用）
```

用 `scripts/new_course.py` 生成骨架：

```bash
python3 scripts/new_course.py <目录> --title "网络云组网" \
  --chapters "设备与位置|各在哪一层,二层 VLAN|同组直通跨组上三层,三层地址|掩码与网关,路由表|表怎么长出来"
```

## 章节数量与顺序

- 5 到 7 章。`00` 固定是课程地图，不承担教学内容。
- 顺序就是依赖顺序：前一章不点头，后一章不讲。教材里并列的知识点也要排出先后。
- 一章只讲一个概念。追问产生的是「同一章补一张图」，不是新开一章；确实是新概念才追加章节。

## 每页的固定形状

1. 小字章号 + 标题 + 一句导语（一句话说这一章解决什么问题）。
2. 主体：左图右表。图里只有节点和一个会移动的点；字段值放右侧固定表，不做跟随浮层。
3. 控制条：上一步 / 下一步 / 从头 + 当前步的一句话（≤ 25 字）。
4. 本步术语：2 到 3 个，点开 `缩写｜全称｜中文：一句话`。
5. 章末翻页：上一章 / 下一章。

`S` 数组是唯一内容源，一步一条：

```js
const S = [
  { msg: '一句话', pos: [x, y], a: '字段一', b: '字段二', terms: ['VLAN', '二层'] },
];
```

## 进度与导航

- 顶部 `#cnav` 由 `assets/course.js` 注入；当前章高亮，看过的章打勾。
- 进度存在 `localStorage` 的同一个键里（默认 `netcloud-course-progress`），键名在 `course.js` 顶部，可改。
- 章节数组在 `assets/course-data.js`，由脚本生成；增删章节改这里并同步生成对应 html。

## 交付与检查

- 改完直接 `open <绝对路径>`，用 `file://` 打开；不做热更新轮询，不依赖本地服务。
- 数据类文件（术语）要转成 `.js` 才能被 `file://` 页面读到。
- 逻辑自查用 `?step=N` 加无头浏览器读 DOM，不看截图：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --virtual-time-budget=3000 --dump-dom "file:///abs/path/ch03.html?step=4" \
  | grep -o 'id="msg">[^<]*'
```

## 维护

- 术语只改 `术语.json`，然后跑 `scripts/build_terms.py 术语.json`，不手改 `terms-data.js`。
- 新章节：在 `course-data.js` 加一条，复制最近一章的 html 改名，替换标题与 `S`。
- 视觉与节奏规则见 `html-lessons.md`；教学节奏见 `teaching-style.md`。
