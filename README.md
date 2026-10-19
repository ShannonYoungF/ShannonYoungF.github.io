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

正文支持标题、段落、粗体、斜体、链接、行内代码、代码块、引用、有序/无序列表、表格、分隔线和 MathJax 数学公式。

## 生成网站

```powershell
cd D:\0Postdoctoral\05NoteSpace\personal-site
python build.py
```

脚本会更新：

- `index.html`：首页与最近文章
- `blog.html`：可搜索、可分类筛选的文章归档
- `posts/*.html`：独立文章页面

这些是生成文件。日常写作应修改 `content/posts/<分类>/*.md`，页面结构修改 `templates/` 和 `includes/`。构建时会自动删除已不存在原稿所对应的旧文章页面。

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
│   ├── theory/                # 理论学习
│   └── thought/               # 思考随笔
├── includes/        # 共享导航、页头和页脚
├── templates/       # 首页、归档页和文章页模板
├── posts/           # 自动生成的文章 HTML
├── build.py         # 零依赖构建脚本
├── site.json        # 个人资料与站点配置
├── index.html       # 自动生成的首页
├── blog.html        # 自动生成的文章归档
├── styles.css       # 全站样式
└── script.js        # 主题、筛选、搜索与动效
```
