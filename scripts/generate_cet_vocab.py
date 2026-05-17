#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
TODAY = dt.date.today().isoformat()
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
)
WHITESPACE_RE = re.compile(r"\s+")

SOURCES = [
    {
        "name": "四级",
        "code": "CET4",
        "title": "四级英语词汇",
        "filename": "四级英语词汇.md",
        "url": "https://raw.githubusercontent.com/KyleBing/english-vocabulary/master/json/3-CET4-%E9%A1%BA%E5%BA%8F.json",
    },
    {
        "name": "六级",
        "code": "CET6",
        "title": "六级英语词汇",
        "filename": "六级英语词汇.md",
        "url": "https://raw.githubusercontent.com/KyleBing/english-vocabulary/master/json/4-CET6-%E9%A1%BA%E5%BA%8F.json",
    },
]


def normalize(text: object) -> str:
    return WHITESPACE_RE.sub(" ", str(text or "")).strip()


def escape_cell(text: object) -> str:
    value = normalize(text)
    if not value:
        return "-"
    return value.replace("|", "\\|")


def fetch_json(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def format_translations(entry: dict) -> str:
    parts: list[str] = []
    for item in entry.get("translations", []):
        translation = normalize(item.get("translation"))
        if not translation:
            continue
        word_type = normalize(item.get("type"))
        if word_type:
            parts.append(f"{word_type}. {translation}")
        else:
            parts.append(translation)
    return "；".join(parts)


def build_vocab_page(source: dict, rows: list[dict]) -> str:
    lines = [
        "---",
        f"title: {source['title']}",
        f"description: {source['title']}，共 {len(rows)} 个词条。",
        "---",
        "",
        f"# {source['title']}",
        "",
        f"- 词表来源：[{source['code']} 顺序词库]({source['url']})",
        f"- 整理日期：{TODAY}",
        f"- 词条数量：{len(rows)}",
        "- 说明：本页保留单词和中文释义，暂不含音标和例句。",
        "",
        "| 序号 | 单词 | 释义 |",
        "| --- | --- | --- |",
    ]

    for index, entry in enumerate(rows, start=1):
        word = escape_cell(entry.get("word"))
        translations = escape_cell(format_translations(entry))
        lines.append(f"| {index} | {word} | {translations} |")
    return "\n".join(lines) + "\n"


def build_category_readme(source: dict, count: int) -> str:
    filename = source["filename"]
    return "\n".join(
        [
            f"# {source['name']}单词整理",
            "",
            f"- 根目录：`{source['name']}/`",
            f"- 词表来源：[{source['code']} 顺序词库]({source['url']})",
            "- 当前状态：已整理顺序版词汇",
            "- 说明：本词表暂只保留单词和中文释义。",
            "",
            "| 文件 | 词条数量 | 备注 |",
            "| --- | --- | --- |",
            f"| [{filename}]({filename}) | {count} | 顺序版；含中文释义 |",
            "",
        ]
    )


def main() -> None:
    for source in SOURCES:
        rows = fetch_json(source["url"])
        output_dir = ROOT / source["name"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source["filename"]).write_text(
            build_vocab_page(source, rows),
            encoding="utf-8",
        )
        (output_dir / "README.md").write_text(
            build_category_readme(source, len(rows)),
            encoding="utf-8",
        )
        print(f"{source['name']}: wrote {len(rows)} entries")


if __name__ == "__main__":
    main()
