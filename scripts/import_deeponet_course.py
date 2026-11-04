"""Import the supplied Chinese reading edition and its referenced formula SVGs."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    root = Path(__file__).resolve().parents[1]
    original = source.read_text(encoding="utf-8")
    body_match = re.search(r"<body[^>]*>(.*?)</body>", original, flags=re.S | re.I)
    if not body_match:
        raise ValueError("The source does not contain an HTML body")
    body = body_match[1]
    body = re.sub(r'<div class="reader-tools">.*?</div>', "", body, flags=re.S)
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1, flags=re.S)
    body = re.sub(
        r'<li>本地原文：.*?</li>',
        '<li>论文公开入口：<a href="https://doi.org/10.1016/j.jcp.2024.113670">DOI / 出版页面</a>。</li>',
        body,
    )
    if re.search(r'<script\b|\son\w+\s*=|(?:href|src)=["\'](?:[A-Za-z]:|file:|javascript:)', body, re.I):
        raise ValueError("Remove scripts, event handlers, or private local links before importing")

    asset_source = source.parent / "assets" / "deeponet-eki-math"
    manifest = json.loads((asset_source / "formula-sources.json").read_text(encoding="utf-8"))
    formulas = {item["filename"]: item["tex"] for item in manifest["occurrences"]}
    referenced = set(re.findall(r'src="assets/deeponet-eki-math/([^"/]+\.svg)"', body))
    asset_dest = root / "assets" / "courses" / "deeponet-eki"
    asset_dest.mkdir(parents=True, exist_ok=True)
    for filename in sorted(referenced):
        shutil.copyfile(asset_source / filename, asset_dest / filename)

    def accessible_formula(match: re.Match[str]) -> str:
        tag = match[0]
        filename = re.search(r'src="assets/deeponet-eki-math/([^"/]+)"', tag)[1]
        tex = html.escape(formulas[filename], quote=True)
        return re.sub(r'alt="[^"]*"', lambda _: f'alt="{tex}"', tag)

    body = re.sub(r'<img\b[^>]*src="assets/deeponet-eki-math/[^"/]+\.svg"[^>]*>', accessible_formula, body)
    output = root / "content" / "courses" / "deeponet-eki-uncertainty"
    output.mkdir(parents=True, exist_ok=True)
    metadata = """---
title: 不确定性传播与量化：DeepONet–EKI 十讲
date: 2026-11-01
updated: 2026-11-04
lang: zh
translation_key: deeponet-eki-uncertainty
summary: 从概率分布、协方差和贝叶斯推断出发，逐步读懂 DeepONet 与集合卡尔曼反演，并学会检验不确定性估计。包含十讲、手算示例、自测答案和五个附录。
tags: 不确定性量化, DeepONet, EKI, 贝叶斯推断
slug: deeponet-eki-uncertainty
---

"""
    (output / "course.zh.html").write_text(metadata + body.strip() + "\n", encoding="utf-8")
    print(f"Imported Chinese course and {len(referenced)} formula SVGs")


if __name__ == "__main__":
    main()
