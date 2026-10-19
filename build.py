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

CATEGORIES = {
    "tech": "技术实践",
    "theory": "理论学习",
    "thought": "思考随笔",
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

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

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
    required = {"title", "date", "category", "summary", "tags", "slug"}
    for path in sorted(CONTENT_DIR.glob("*.md")):
        metadata, markdown = parse_front_matter(path.read_text(encoding="utf-8"))
        missing = required - metadata.keys()
        if missing:
            raise ValueError(f"{path.name} is missing: {', '.join(sorted(missing))}")
        if metadata["category"] not in CATEGORIES:
            raise ValueError(f"Unknown category in {path.name}: {metadata['category']}")
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
                "category_label": CATEGORIES[metadata["category"]],
                "tags_list": [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()],
                "reading_time": reading_time(markdown),
            }
        )
    return sorted(posts, key=lambda item: item["date_obj"], reverse=True)


def post_row(post: dict[str, Any], prefix: str = "") -> str:
    return f'''<a class="note-row" href="{prefix}posts/{quote(post['slug'])}.html">
  <time datetime="{post['date']}">{post['date_display']}</time>
  <span><strong>{html.escape(post['title'])}</strong><small>{post['category_label']} · {post['reading_time']} min</small></span>
  <span class="arrow" aria-hidden="true">↗</span>
</a>'''


def archive_card(post: dict[str, Any]) -> str:
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in post["tags_list"])
    search_value = " ".join([post["title"], post["summary"], *post["tags_list"]]).lower()
    return f'''<article class="entry-card" data-category="{post['category']}" data-search="{html.escape(search_value, quote=True)}">
  <div class="entry-date"><time datetime="{post['date']}">{post['date_display']}</time></div>
  <div class="entry-content">
    <div class="entry-overline"><span class="category-dot {post['category']}"></span>{post['category_label']} · {post['reading_time']} 分钟</div>
    <h2><a href="posts/{quote(post['slug'])}.html">{html.escape(post['title'])}</a></h2>
    <p>{html.escape(post['summary'])}</p>
    <div class="entry-tags">{tags}</div>
  </div>
  <a class="entry-arrow" href="posts/{quote(post['slug'])}.html" aria-label="阅读《{html.escape(post['title'], quote=True)}》">↗</a>
</article>'''


def common_context(site: dict[str, str], root: str, title: str, description: str) -> dict[str, str]:
    values = {
        "root": root,
        "page_title": title,
        "page_description": description,
        "site_name": site["name"],
        "site_short_name": site["short_name"],
        "site_description": site["description"],
        "site_email": site["email"],
        "site_github": site["github"],
    }
    values["head"] = render_template((INCLUDE_DIR / "head.html").read_text(encoding="utf-8"), values)
    values["nav"] = render_template((INCLUDE_DIR / "nav.html").read_text(encoding="utf-8"), values)
    values["footer"] = render_template((INCLUDE_DIR / "footer.html").read_text(encoding="utf-8"), values)
    return values


def build() -> None:
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    posts = load_posts()
    counts = {key: sum(post["category"] == key for post in posts) for key in CATEGORIES}

    index_context: dict[str, Any] = common_context(
        site,
        "",
        f"{site['name']} — 技术、理论与思考",
        site["description"],
    )
    index_context.update(
        {
            "latest_posts": "\n".join(post_row(post) for post in posts[:5]),
            "tech_count_padded": f"{counts['tech']:02d}",
            "theory_count_padded": f"{counts['theory']:02d}",
            "thought_count_padded": f"{counts['thought']:02d}",
        }
    )
    index_html = render_template((TEMPLATE_DIR / "index.html").read_text(encoding="utf-8"), index_context)
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")

    blog_context: dict[str, Any] = common_context(
        site,
        "",
        f"文章与笔记 — {site['name']}",
        "按时间整理的技术实践、理论学习与思考随笔。",
    )
    blog_context.update(
        {
            "all_posts": "\n".join(archive_card(post) for post in posts),
            "total_count": len(posts),
            "tech_count": counts["tech"],
            "theory_count": counts["theory"],
            "thought_count": counts["thought"],
        }
    )
    blog_html = render_template((TEMPLATE_DIR / "blog.html").read_text(encoding="utf-8"), blog_context)
    (ROOT / "blog.html").write_text(blog_html, encoding="utf-8")

    POST_OUTPUT_DIR.mkdir(exist_ok=True)
    post_template = (TEMPLATE_DIR / "post.html").read_text(encoding="utf-8")
    for post in posts:
        post_context: dict[str, Any] = common_context(
            site,
            "../",
            f"{post['title']} — {site['name']}",
            post["summary"],
        )
        post_context.update(post)
        post_context["tags_html"] = "".join(
            f"<span>{html.escape(tag)}</span>" for tag in post["tags_list"]
        )
        rendered = render_template(post_template, post_context)
        (POST_OUTPUT_DIR / f"{post['slug']}.html").write_text(rendered, encoding="utf-8")

    print(f"Built {len(posts)} posts, index.html, and blog.html")


if __name__ == "__main__":
    build()
