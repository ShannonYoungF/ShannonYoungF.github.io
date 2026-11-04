# 技术、理论与思考博客

一个零依赖静态博客。文章使用 Markdown 编写，运行 `build.py` 后自动生成首页、文章归档和独立文章页，可直接部署到 GitHub Pages。

## 写一篇新文章

根据文章类型，在对应目录中新建 Markdown 文件：

- `content/posts/tech/`：技术实践
- `content/posts/theory/`：理论学习
- `content/posts/thought/`：思考随笔

```markdown
---
title: 文章标题
date: 2026-10-19
updated: 2026-10-19
category: tech
lang: zh
translation_key: article-url
summary: 用一两句话概括文章。
tags: Python, 实验, 工程方法
slug: article-url
---

从这里开始写正文。
```

`category` 支持三个值：

- `tech`：技术实践
- `theory`：理论学习
- `thought`：思考随笔

`lang` 使用 `zh` 或 `en`。中英文版本应使用相同的 `translation_key`，构建器会据此生成文章页上的语言切换链接。两种语言可以使用相同的 `slug`，因为英文页面会输出到独立的 `en/` 目录。

正文支持标题、段落、粗体、斜体、链接、行内代码、代码块、引用、有序/无序列表、表格、分隔线和 MathJax 数学公式。

## 管理课程

课程独立于文章分类，每门课程使用自己的文件夹：

```text
content/courses/deeponet-eki-uncertainty/
├── course.zh.html   # 中文完整阅读稿
└── course.en.md     # 英文课程原稿
assets/courses/deeponet-eki/
└── *.svg            # 两种语言共用的公式资源
```

新增课程时，在 `content/courses/<slug>/` 下放置中文和英文原稿，支持 Markdown 或 HTML。文件开头同样需要元数据，但不需要 `category`：

```yaml
---
title: 课程标题
date: 2026-11-01
updated: 2026-11-04
lang: zh
translation_key: course-url
summary: 课程简介。
tags: 主题一, 主题二
slug: course-url
---
```

两个版本的 `translation_key` 和 `slug` 必须相同，文件夹名也必须等于 `slug`。Markdown 使用 `##` 表示章节、`###` 表示小节；HTML 使用 `<h2>` 和 `<h3>`。以“第 1 讲”或“Lecture 1”开头的章节自动获得统一的 `lecture-01` 锚点，中英文切换会保留当前讲次。

英文 Markdown 的折叠答案可以写为：

```text
:::answers
1. 第一题的参考答案。
2. 第二题的参考答案。
:::endanswers
```

本课程的中文原稿保留了原 HTML 的公式和折叠答案。若需要重新从阅读版导入，可运行 `python scripts/import_deeponet_course.py "阅读版 HTML 的完整路径"`；这会更新中文原稿及引用的 SVG，不会改动英文原稿。导入后再运行 `python build.py`。

课程入口会出现在全站导航、首页和文章归档页。详情页支持章节目录、展开答案、打印为 PDF、深浅色主题和中英文切换。

## 生成网站

```powershell
cd D:\0Postdoctoral\05NoteSpace\personal-site
python build.py
```

脚本会更新：

- `index.html`：首页与最近文章
- `blog.html`：可搜索、可分类筛选的文章归档
- `posts/*.html`：独立文章页面
- `en/index.html`、`en/blog.html`：英文首页与归档
- `en/posts/*.html`：英文文章页面
- `courses.html`、`en/courses.html`：课程列表
- `courses/*.html`、`en/courses/*.html`：中英文课程详情

这些是生成文件。日常写作应修改 `content/posts/<分类>/*.md` 或 `content/courses/<课程>/` 下的原稿，页面结构修改 `templates/` 和 `includes/`。构建时会自动删除已不存在原稿所对应的旧文章和课程详情页面。

## 修改个人资料

编辑 `site.json`，替换姓名、邮箱、GitHub 和站点域名，然后再次运行 `python build.py`。

## 本地预览

可以直接打开 `index.html`。为避免浏览器对本地文件的限制，也可以运行：

```powershell
python -m http.server 8000
```

然后访问 `http://localhost:8000`。

## 部署到 GitHub Pages

1. 新建一个公开仓库，例如 `yourname.github.io`。
2. 将本目录提交并推送到仓库。
3. 在 **Settings → Pages** 中选择从 `main` 分支根目录发布。
4. 每次新增文章后，先运行 `python build.py`，再提交生成的 HTML。

## 目录结构

```text
personal-site/
├── content/posts/             # Markdown 原稿
│   ├── tech/                  # 技术实践
│   ├── theory/                # 理论学习（中英文译文可放在同一分类）
│   └── thought/               # 思考随笔
├── content/courses/           # 按课程文件夹管理的中英文原稿
├── assets/courses/            # 课程公式、配图等静态资源
├── includes/        # 共享导航、页头和页脚
├── templates/       # 首页、归档页和文章页模板
├── posts/           # 自动生成的文章 HTML
├── courses/         # 自动生成的中文课程 HTML
├── en/              # 自动生成的英文站点
├── build.py         # 零依赖构建脚本
├── site.json        # 个人资料与站点配置
├── index.html       # 自动生成的首页
├── blog.html        # 自动生成的文章归档
├── styles.css       # 全站样式
└── script.js        # 主题、筛选、搜索与动效
```
