"""Zero-dependency static blog generator for this personal site."""

from __future__ import annotations

import html
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content" / "posts"
TEMPLATE_DIR = ROOT / "templates"
INCLUDE_DIR = ROOT / "includes"
POST_OUTPUT_DIR = ROOT / "posts"
EN_OUTPUT_DIR = ROOT / "en"

CATEGORIES = {
    "tech": {"zh": "技术实践", "en": "Technical Practice"},
    "theory": {"zh": "理论学习", "en": "Theory"},
    "thought": {"zh": "思考随笔", "en": "Reflections"},
}

UI = {
    "zh": {
        "html_lang": "zh-CN",
        "other_html_lang": "en",
        "language_switch_label": "EN",
        "language_switch_aria": "切换到英文",
        "home_aria": "返回首页",
        "menu_label": "打开导航",
        "nav_label": "主导航",
        "nav_home": "首页",
        "nav_tech": "技术",
        "nav_theory": "理论",
        "nav_thought": "思考",
        "theme_label": "切换深浅色主题",
        "footer_tagline": "技术 · 理论 · 思考",
        "home_title_suffix": "技术、理论与思考",
        "home_eyebrow": "一座持续生长的个人知识库",
        "home_hero_title": "记录技术，<br>也追问它背后的<span class=\"name-mark\">理论</span>。",
        "home_lede": "这里存放我关于技术实践、理论学习与长期问题的笔记。它不是答案的陈列柜，而是一张不断修订的思维地图。",
        "home_note": "我会尽量写清楚：问题从哪里来、假设是什么、推导如何成立，以及实验究竟说明了什么。",
        "home_start": "开始阅读",
        "home_view_map": "查看内容地图",
        "tracks_title": "三条写作线",
        "tracks_intro": "同一个问题，往往需要从实现、理论和经验三个方向来理解。",
        "tech_card_title": "从想法到可运行的系统",
        "tech_card_text": "算法实现、工程工具、实验复现，以及真实系统中的取舍。",
        "theory_card_title": "从定义到可以迁移的直觉",
        "theory_card_text": "概念、假设、推导和证明；记录我如何把一个理论真正想明白。",
        "thought_card_title": "保留尚未收敛的问题",
        "thought_card_text": "研究方法、认知工具、失败复盘，以及还没有标准答案的事情。",
        "latest_title": "最近更新",
        "all_posts_label": "全部文章",
        "manifesto_quote": "“写下来，不是因为已经想明白；而是为了让模糊的直觉有机会变成可以检查的结构。”",
        "manifesto_text": "如果一篇笔记能让未来的我少走一点弯路，或让另一个人更快地进入一个问题，它就已经有价值。",
        "blog_title": "文章与笔记",
        "blog_description": "按时间整理的技术实践、理论学习与思考随笔。",
        "blog_intro": "按时间保留想法的变化。文章可能会在理解加深后继续修订。",
        "archive_aria": "文章列表",
        "filter_aria": "文章分类",
        "filter_all": "全部",
        "filter_tech": "技术",
        "filter_theory": "理论",
        "filter_thought": "思考",
        "search_label": "搜索文章",
        "search_placeholder": "搜索标题、摘要或标签…",
        "empty_state": "没有找到对应的文章，试试别的关键词。",
        "back_prefix": "返回",
        "reading_time_format": "{minutes} 分钟阅读",
        "archive_time_format": "{minutes} 分钟",
        "updated_prefix": "最后更新于",
        "post_footer": "如果这篇笔记对你有帮助，或你发现了错误，欢迎通过",
        "post_footer_suffix": "交流。",
        "continue_reading": "继续阅读",
        "read_aria_format": "阅读《{title}》",
    },
    "en": {
        "html_lang": "en",
        "other_html_lang": "zh-CN",
        "language_switch_label": "中",
        "language_switch_aria": "Switch to Chinese",
        "home_aria": "Back to home",
        "menu_label": "Open navigation",
        "nav_label": "Main navigation",
        "nav_home": "Home",
        "nav_tech": "Tech",
        "nav_theory": "Theory",
        "nav_thought": "Reflections",
        "theme_label": "Toggle light and dark theme",
        "footer_tagline": "Technology · Theory · Reflection",
        "home_title_suffix": "Technology, Theory and Reflection",
        "home_eyebrow": "A personal knowledge base in continual growth",
        "home_hero_title": "Documenting technology,<br>and questioning the <span class=\"name-mark\">theory</span> behind it.",
        "home_lede": "This is where I keep notes on technical practice, theoretical learning, and long-running questions. It is not a cabinet of answers, but an evolving map of thought.",
        "home_note": "I try to make four things explicit: where a problem comes from, what assumptions it rests on, why a derivation works, and what an experiment actually shows.",
        "home_start": "Start reading",
        "home_view_map": "View the content map",
        "tracks_title": "Three lines of inquiry",
        "tracks_intro": "The same problem often needs to be understood through implementation, theory, and experience.",
        "tech_card_title": "From an idea to a working system",
        "tech_card_text": "Algorithms, engineering tools, reproducible experiments, and trade-offs in real systems.",
        "theory_card_title": "From definitions to transferable intuition",
        "theory_card_text": "Concepts, assumptions, derivations, and proofs—and how I work toward genuine understanding.",
        "thought_card_title": "Keeping unresolved questions alive",
        "thought_card_text": "Research methods, cognitive tools, lessons from failure, and questions without settled answers.",
        "latest_title": "Latest writing",
        "all_posts_label": "All posts",
        "manifesto_quote": "“I write not because the thought is already clear, but to give a vague intuition the chance to become a structure that can be examined.”",
        "manifesto_text": "If a note helps my future self avoid a detour, or helps someone else enter a problem more quickly, it has already done something worthwhile.",
        "blog_title": "Writing and Notes",
        "blog_description": "Technical practice, theoretical learning, and reflections arranged over time.",
        "blog_intro": "A chronological record of changing ideas. Posts may continue to evolve as my understanding deepens.",
        "archive_aria": "Post archive",
        "filter_aria": "Post categories",
        "filter_all": "All",
        "filter_tech": "Tech",
        "filter_theory": "Theory",
        "filter_thought": "Reflections",
        "search_label": "Search posts",
        "search_placeholder": "Search titles, summaries, or tags…",
        "empty_state": "No matching posts. Try another search.",
        "back_prefix": "Back to",
        "reading_time_format": "{minutes} min read",
        "archive_time_format": "{minutes} min",
        "updated_prefix": "Last updated",
        "post_footer": "If this note was useful, or if you spotted an error, feel free to reach out on",
        "post_footer_suffix": ".",
        "continue_reading": "Keep reading",
        "read_aria_format": "Read “{title}”",
    },
}


def parse_front_matter(source: str) -> tuple[dict[str, str], str]:
    if not source.startswith("---\n"):
        raise ValueError("Post must start with a front matter block")
    _, raw_meta, body = source.split("---", 2)
    metadata: dict[str, str] = {}
    for raw_line in raw_meta.strip().splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            raise ValueError(f"Invalid front matter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def render_inline(text: str) -> str:
    value = html.escape(text, quote=False)
    placeholders: list[str] = []

    def protect_code(match: re.Match[str]) -> str:
        placeholders.append(f'<code>{match.group(1)}</code>')
        return f"\x00CODE{len(placeholders) - 1}\x00"

    value = re.sub(r"`([^`]+)`", protect_code, value)
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    for index, replacement in enumerate(placeholders):
        value = value.replace(f"\x00CODE{index}\x00", replacement)
    return value


def render_markdown(source: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_language = ""
    code_lines: list[str] = []
    in_math = False
    math_lines: list[str] = []
    in_table = False

    def table_cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def is_table_separator(line: str) -> bool:
        cells = table_cells(line)
        return len(cells) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            output.append("</tbody></table></div>")
            in_table = False

    for raw_line in source.splitlines():
        line = raw_line.rstrip()

        if in_code:
            if line.strip().startswith("```"):
                language_class = f' class="language-{html.escape(code_language)}"' if code_language else ""
                output.append(f"<pre><code{language_class}>{html.escape(chr(10).join(code_lines))}</code></pre>")
                in_code = False
                code_lines.clear()
            else:
                code_lines.append(line)
            continue

        if in_math:
            if line.strip() == "$$":
                output.append(f'<div class="math-block">$${html.escape(chr(10).join(math_lines))}$$</div>')
                in_math = False
                math_lines.clear()
            else:
                math_lines.append(line)
            continue

        if in_table:
            if line.strip().startswith("|") and line.count("|") >= 2:
                cells = "".join(f"<td>{render_inline(cell)}</td>" for cell in table_cells(line))
                output.append(f"<tr>{cells}</tr>")
                continue
            close_table()

        if line.strip().startswith("```"):
            flush_paragraph()
            close_list()
            in_code = True
            code_language = line.strip()[3:].strip()
            continue

        if line.strip() == "$$":
            flush_paragraph()
            close_list()
            in_math = True
            continue

        if is_table_separator(line) and paragraph and paragraph[-1].startswith("|"):
            header = paragraph.pop()
            flush_paragraph()
            close_list()
            cells = "".join(f"<th>{render_inline(cell)}</th>" for cell in table_cells(header))
            output.append(f'<div class="table-wrap"><table><thead><tr>{cells}</tr></thead><tbody>')
            in_table = True
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1)) + 1
            heading_text = heading.group(2)
            heading_id = slugify(re.sub(r"[`*_]", "", heading_text))
            output.append(f'<h{level} id="{heading_id}">{render_inline(heading_text)}</h{level}>')
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", line)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            target_type = "ul" if unordered else "ol"
            if list_type != target_type:
                close_list()
                output.append(f"<{target_type}>")
                list_type = target_type
            item = (unordered or ordered).group(1)  # type: ignore[union-attr]
            output.append(f"<li>{render_inline(item)}</li>")
            continue

        if line.startswith("> "):
            flush_paragraph()
            close_list()
            output.append(f"<blockquote><p>{render_inline(line[2:])}</p></blockquote>")
            continue

        if re.fullmatch(r"-{3,}", line.strip()):
            flush_paragraph()
            close_list()
            output.append("<hr>")
            continue

        paragraph.append(line.strip())

    flush_paragraph()
    close_list()
    close_table()
    if in_code:
        raise ValueError("Unclosed fenced code block")
    if in_math:
        raise ValueError("Unclosed display math block")
    return "\n".join(output)


def slugify(value: str) -> str:
    value = value.strip().lower().replace(" ", "-")
    value = re.sub(r"[^\w\u4e00-\u9fff-]", "", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "section"


def reading_time(source: str) -> int:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", source))
    latin_words = len(re.findall(r"\b[a-zA-Z0-9_]+\b", source))
    return max(1, round(chinese_chars / 350 + latin_words / 220))


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_date(value: date) -> str:
    return value.strftime("%Y.%m.%d")


def render_template(template: str, context: dict[str, Any]) -> str:
    result = template
    for key, value in context.items():
        result = result.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"{{([\w_]+)}}", result)))
    if unresolved:
        raise ValueError(f"Unresolved template values: {', '.join(unresolved)}")
    return result


def load_posts() -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    seen_slugs: set[tuple[str, str]] = set()
    required = {"title", "date", "category", "lang", "translation_key", "summary", "tags", "slug"}
    for path in sorted(CONTENT_DIR.rglob("*.md")):
        metadata, markdown = parse_front_matter(path.read_text(encoding="utf-8"))
        missing = required - metadata.keys()
        if missing:
            raise ValueError(f"{path.name} is missing: {', '.join(sorted(missing))}")
        if metadata["category"] not in CATEGORIES:
            raise ValueError(f"Unknown category in {path.name}: {metadata['category']}")
        if metadata["lang"] not in UI:
            raise ValueError(f"Unknown language in {path.name}: {metadata['lang']}")
        category_dir = path.relative_to(CONTENT_DIR).parts[0]
        if category_dir != metadata["category"]:
            raise ValueError(
                f"Category mismatch in {path.name}: move it to "
                f"content/posts/{metadata['category']}/"
            )
        slug_key = (metadata["lang"], metadata["slug"])
        if slug_key in seen_slugs:
            raise ValueError(f"Duplicate {metadata['lang']} slug: {metadata['slug']}")
        seen_slugs.add(slug_key)
        published = parse_date(metadata["date"])
        updated = parse_date(metadata.get("updated", metadata["date"]))
        posts.append(
            {
                **metadata,
                "source_path": path,
                "markdown": markdown,
                "body": render_markdown(markdown),
                "date_obj": published,
                "updated_obj": updated,
                "date_display": format_date(published),
                "updated_display": format_date(updated),
                "tags_list": [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()],
                "reading_time": reading_time(markdown),
            }
        )
    return sorted(posts, key=lambda item: item["date_obj"], reverse=True)


def post_row(post: dict[str, Any], lang: str) -> str:
    category_label = CATEGORIES[post["category"]][lang]
    reading_time = UI[lang]["archive_time_format"].format(minutes=post["reading_time"])
    return f'''<a class="note-row" href="posts/{quote(post['slug'])}.html">
  <time datetime="{post['date']}">{post['date_display']}</time>
  <span><strong>{html.escape(post['title'])}</strong><small>{category_label} · {reading_time}</small></span>
  <span class="arrow" aria-hidden="true">↗</span>
</a>'''


def archive_card(post: dict[str, Any], lang: str) -> str:
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in post["tags_list"])
    search_value = " ".join([post["title"], post["summary"], *post["tags_list"]]).lower()
    category_label = CATEGORIES[post["category"]][lang]
    reading_time = UI[lang]["archive_time_format"].format(minutes=post["reading_time"])
    read_aria = UI[lang]["read_aria_format"].format(title=post["title"])
    return f'''<article class="entry-card" data-category="{post['category']}" data-search="{html.escape(search_value, quote=True)}">
  <div class="entry-date"><time datetime="{post['date']}">{post['date_display']}</time></div>
  <div class="entry-content">
    <div class="entry-overline"><span class="category-dot {post['category']}"></span>{category_label} · {reading_time}</div>
    <h2><a href="posts/{quote(post['slug'])}.html">{html.escape(post['title'])}</a></h2>
    <p>{html.escape(post['summary'])}</p>
    <div class="entry-tags">{tags}</div>
  </div>
  <a class="entry-arrow" href="posts/{quote(post['slug'])}.html" aria-label="{html.escape(read_aria, quote=True)}">↗</a>
</article>'''


def absolute_url(site: dict[str, str], path: str) -> str:
    return f"{site['url'].rstrip('/')}/{path.lstrip('/')}"


def common_context(
    site: dict[str, str],
    lang: str,
    asset_root: str,
    locale_root: str,
    title: str,
    description: str,
    language_switch_url: str,
    canonical_path: str,
    alternate_paths: dict[str, str],
) -> dict[str, str]:
    values = {
        **UI[lang],
        "asset_root": asset_root,
        "locale_root": locale_root,
        "language_switch_url": language_switch_url,
        "page_title": title,
        "page_description": description,
        "canonical_url": absolute_url(site, canonical_path),
        "alternate_links": "\n".join(
            f'<link rel="alternate" hreflang="{UI[alternate_lang]["html_lang"]}" href="{absolute_url(site, path)}">'
            for alternate_lang, path in alternate_paths.items()
        ),
        "site_name": site["name"],
        "site_short_name": site["short_name"],
        "site_description": site["description"] if lang == "zh" else site["description_en"],
        "site_email": site["email"],
        "site_github": site["github"],
    }
    values["head"] = render_template((INCLUDE_DIR / "head.html").read_text(encoding="utf-8"), values)
    values["nav"] = render_template((INCLUDE_DIR / "nav.html").read_text(encoding="utf-8"), values)
    values["footer"] = render_template((INCLUDE_DIR / "footer.html").read_text(encoding="utf-8"), values)
    return values


def build_locale(
    site: dict[str, str],
    all_posts: list[dict[str, Any]],
    translations: dict[str, dict[str, dict[str, Any]]],
    lang: str,
) -> None:
    posts = [post for post in all_posts if post["lang"] == lang]
    counts = {key: sum(post["category"] == key for post in posts) for key in CATEGORIES}
    is_english = lang == "en"
    page_dir = EN_OUTPUT_DIR if is_english else ROOT
    post_output_dir = page_dir / "posts"
    page_asset_root = "../" if is_english else ""
    post_asset_root = "../../" if is_english else "../"
    index_switch = "../index.html" if is_english else "en/index.html"
    blog_switch = "../blog.html" if is_english else "en/blog.html"
    index_path = "en/" if is_english else ""
    blog_path = "en/blog.html" if is_english else "blog.html"
    page_dir.mkdir(exist_ok=True)

    index_context: dict[str, Any] = common_context(
        site,
        lang,
        page_asset_root,
        "",
        f"{site['name']} — {UI[lang]['home_title_suffix']}",
        site["description"] if lang == "zh" else site["description_en"],
        index_switch,
        index_path,
        {"zh": "", "en": "en/"},
    )
    index_context.update(
        {
            "latest_posts": "\n".join(post_row(post, lang) for post in posts[:5]),
            "tech_count_padded": f"{counts['tech']:02d}",
            "theory_count_padded": f"{counts['theory']:02d}",
            "thought_count_padded": f"{counts['thought']:02d}",
            "tech_category_label": CATEGORIES["tech"][lang],
            "theory_category_label": CATEGORIES["theory"][lang],
            "thought_category_label": CATEGORIES["thought"][lang],
        }
    )
    index_html = render_template((TEMPLATE_DIR / "index.html").read_text(encoding="utf-8"), index_context)
    (page_dir / "index.html").write_text(index_html, encoding="utf-8")

    blog_context: dict[str, Any] = common_context(
        site,
        lang,
        page_asset_root,
        "",
        f"{UI[lang]['blog_title']} — {site['name']}",
        UI[lang]["blog_description"],
        blog_switch,
        blog_path,
        {"zh": "blog.html", "en": "en/blog.html"},
    )
    blog_context.update(
        {
            "all_posts": "\n".join(archive_card(post, lang) for post in posts),
            "total_count": len(posts),
            "tech_count": counts["tech"],
            "theory_count": counts["theory"],
            "thought_count": counts["thought"],
        }
    )
    blog_html = render_template((TEMPLATE_DIR / "blog.html").read_text(encoding="utf-8"), blog_context)
    (page_dir / "blog.html").write_text(blog_html, encoding="utf-8")

    post_output_dir.mkdir(exist_ok=True)
    expected_outputs = {f"{post['slug']}.html" for post in posts}
    for path in post_output_dir.glob("*.html"):
        if path.name not in expected_outputs:
            path.unlink()

    post_template = (TEMPLATE_DIR / "post.html").read_text(encoding="utf-8")
    for post in posts:
        translation_group = translations[post["translation_key"]]
        other_lang = "zh" if lang == "en" else "en"
        counterpart = translation_group.get(other_lang)
        if counterpart:
            if is_english:
                language_switch_url = f"../../posts/{quote(counterpart['slug'])}.html"
            else:
                language_switch_url = f"../en/posts/{quote(counterpart['slug'])}.html"
        else:
            language_switch_url = "../../blog.html" if is_english else "../en/blog.html"

        canonical_path = (
            f"en/posts/{quote(post['slug'])}.html"
            if is_english
            else f"posts/{quote(post['slug'])}.html"
        )
        alternate_paths = {
            alternate_lang: (
                f"en/posts/{quote(item['slug'])}.html"
                if alternate_lang == "en"
                else f"posts/{quote(item['slug'])}.html"
            )
            for alternate_lang, item in translation_group.items()
        }
        post_context: dict[str, Any] = common_context(
            site,
            lang,
            post_asset_root,
            "../",
            f"{post['title']} — {site['name']}",
            post["summary"],
            language_switch_url,
            canonical_path,
            alternate_paths,
        )
        post_context.update(post)
        post_context["category_label"] = CATEGORIES[post["category"]][lang]
        post_context["reading_time_label"] = UI[lang]["reading_time_format"].format(
            minutes=post["reading_time"]
        )
        post_context["tags_html"] = "".join(
            f"<span>{html.escape(tag)}</span>" for tag in post["tags_list"]
        )
        rendered = render_template(post_template, post_context)
        (post_output_dir / f"{post['slug']}.html").write_text(rendered, encoding="utf-8")


def build() -> None:
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    posts = load_posts()
    translations: dict[str, dict[str, dict[str, Any]]] = {}
    for post in posts:
        group = translations.setdefault(post["translation_key"], {})
        if post["lang"] in group:
            raise ValueError(
                f"Duplicate {post['lang']} translation for {post['translation_key']}"
            )
        group[post["lang"]] = post

    for lang in UI:
        build_locale(site, posts, translations, lang)

    print(f"Built {len(posts)} localized posts and {len(UI)} site languages")


if __name__ == "__main__":
    build()
