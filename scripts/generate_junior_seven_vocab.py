#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re

import generate_primary_vocab as base


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "初中"


def write_root_readme(summary: dict[str, list[tuple[str, int, str]]]) -> None:
    lines = [
        "# 初中单词整理",
        "",
        "- 根目录：`初中/`",
        "- 翻译来源：`https://english.mikigo.site/`",
        "- 音标来源：有道词典（英式 / 美式）",
        "- 说明：词组缺少直出音标时，按组成词音标拼接供参考",
        "- 当前状态：已整理人教版初中英语七年级上、下册",
        "",
        "| 年级 | 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- | --- |",
    ]
    for grade in sorted(summary):
        for filename, count, note in summary[grade]:
            lines.append(f"| {grade} | {filename} | {count} | {note} |")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base.PRIMARY_INDEX_URL = (
        f"{base.BASE_URL}/%E4%BA%BA%E6%95%99%E7%89%88%E5%88%9D%E4%B8%AD/index.html"
    )
    base.TARGET_GRADES = {"七年级"}
    base.OUTPUT_ROOT = OUTPUT_ROOT
    base.BOOK_LINK_RE = re.compile(
        r'href="(/人教版初中/人教版初中英语-[^"/]+/\d+_[^"]+\.html)"'
    )
    base.GRADE_RE = re.compile(r"(七年级|八年级|九年级)")
    summary = base.main()
    write_root_readme(summary)


if __name__ == "__main__":
    main()
