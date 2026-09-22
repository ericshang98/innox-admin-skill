#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a static, scenario-based handbook. Evidence stays in rules.json."""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "skills/innox-invoice/references/decision-guide.json").read_text(encoding="utf-8"))


def table(block):
    heads = "".join(f"<th scope='col'>{e(h)}</th>" for h in block["heads"])
    rows = "".join(
        "<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in block["rows"]
    )
    return f"<div class='table-wrap'><table><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table></div>"


def split_name(name):
    if "·" in name:
        left, right = name.split("·", 1)
        return left.strip(), right.strip()
    return "", name


def render(block):
    kind = block["type"]
    if kind == "table":
        return table(block)
    if kind == "heading":
        return f"<h3>{e(block['text'])}</h3>"
    if kind == "note":
        return f"<div class='callout'><strong>{e(block['title'])}</strong><p>{e(block['body'])}</p></div>"
    if kind == "map":
        items = "".join(
            f"<li><b>{e(t)}</b><span>{e(s)}</span></li>" for t, s in block["items"]
        )
        return f"<ol class='spine'>{items}</ol>"
    if kind == "steps":
        items = "".join(
            f"<li><strong>{e(t)}</strong><p>{e(b)}</p></li>" for t, b in block["items"]
        )
        return f"<ol class='decision-order'>{items}</ol>"
    if kind == "cases":
        html = []
        for c in block["items"]:
            kicker, title = split_name(c["name"])
            kicker_html = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
            rows = "".join(
                f"<div><dt>{label}</dt><dd>{e(c[key])}</dd></div>"
                for key, label in (
                    ("entry", "系统入口"),
                    ("fill", "填写内容"),
                    ("materials", "准备材料"),
                    ("next", "下一步"),
                )
            )
            html.append(
                f'<article class="scenario" id="{e(c["id"])}">{kicker_html}<h3>{e(title)}</h3>'
                f'<p class="condition">{e(c["when"])}</p>'
                f'<div class="now"><span>现在做什么</span><strong>{e(c["action"])}</strong></div>'
                f'<dl class="route-detail">{rows}</dl></article>'
            )
        return "".join(html)
    if kind == "examples":
        parts = []
        for c in block["items"]:
            steps = "".join(f"<li>{e(s)}</li>" for s in c["steps"])
            parts.append(
                f"<article class='worked-example'><h3>{e(c['title'])}</h3>"
                f"<p class='condition'>{e(c['facts'])}</p>"
                f"<p class='example-decision'><b>判断结果</b>{e(c['decision'])}</p>"
                f"<ol>{steps}</ol>"
                f"<p class='example-missing'><b>此例还需注意：</b>{e(c['ask'])}</p></article>"
            )
        return "".join(parts)
    raise ValueError(kind)


parts = [
    """<div class="overview"><p class="overview-title">每次调用，按这个顺序推进</p><p class="decision-line"><span>读取长期档案</span><span>识别本次事项</span><span>判断流程</span><span>填写并备料</span><span>保存进度</span></p><p class="muted">团队信息不重复问，采购信息不混用。Agent 根据已有资料准备本次材料，仅补问影响办理的缺项。</p></div>"""
]
nav = []
for i, section in enumerate(data["sections"], 1):
    nav.append(f"<a href='#{section['id']}'><span>{i:02}</span>{e(section['nav'])}</a>")
    body = "".join(render(b) for b in section["blocks"])
    parts.append(
        f"<section id='{section['id']}'><div class='section-head'>"
        f"<p class='section-label'>{i:02} / Agent 填写指南</p>"
        f"<h2>{e(section['title'])}</h2>"
        f"<p class='section-desc'>{e(section['intro'])}</p></div>{body}</section>"
    )

layout = (ROOT / "scripts/rules-layout.html").read_text(encoding="utf-8")
assert layout.count("__BODY__") == 1 and layout.count("__NAV__") == 1
html = layout.replace("__BODY__", "\n".join(parts)).replace("__NAV__", "\n".join(nav))
low = html.lower()
assert not any(tag in low for tag in ("<script", "<select", "<input", "<button", "<textarea", "<details"))
assert "正文条款追溯" not in html and "evidence-" not in html
assert "127.0.0.1" not in html and "localhost" not in low
for name in ("rules-review.html", "review-template.html"):
    (ROOT / "docs" / name).write_text(html, encoding="utf-8")
print(
    "Built v0.6: single-file handbook, no server, no questionnaire, "
    f"{len(data['sections'])} sections."
)
