#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re

import generate_primary_vocab as base


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "初中"
GRADE_ORDER = {"七年级": 0, "八年级": 1, "九年级": 2}
TABLE_ROW_RE = re.compile(r"^\| (?P<file>[^|]+) \| (?P<count>\d+) \| (?P<note>.*) \|$")


def grade_sort_key(grade: str) -> tuple[int, str]:
    return GRADE_ORDER.get(grade, 999), grade


def write_grade_readme(
    grade: str,
    output_dir: pathlib.Path,
    summary_rows: list[tuple[str, int, str]],
) -> None:
    lines = [
        f"# 初中{grade}单词整理",
        "",
        f"- 目录结构：`初中/{grade}/`",
        "- 翻译保留自原学习网站页面",
        "- 音标补充自有道词典",
        f"- 说明：{base.PHONETIC_NOTE}",
        "",
        "| 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- |",
    ]
    for filename, count, note in summary_rows:
        lines.append(f"| {filename} | {count} | {note} |")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_grade_readme(readme_path: pathlib.Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        match = TABLE_ROW_RE.match(line)
        if not match:
            continue
        rows.append(
            (
                match.group("file"),
                int(match.group("count")),
                match.group("note"),
            )
        )
    return rows


def load_grade_summaries() -> dict[str, list[tuple[str, int, str]]]:
    summary: dict[str, list[tuple[str, int, str]]] = {}
    if not OUTPUT_ROOT.exists():
        return summary

    for grade_dir in sorted(
        (path for path in OUTPUT_ROOT.iterdir() if path.is_dir()),
        key=lambda path: grade_sort_key(path.name),
    ):
        readme_path = grade_dir / "README.md"
        if not readme_path.exists():
            continue
        rows = parse_grade_readme(readme_path)
        if rows:
            rows.sort(key=lambda item: item[0])
            summary[grade_dir.name] = rows
    return summary


def build_status_text(summary: dict[str, list[tuple[str, int, str]]]) -> str:
    titles: list[str] = []
    for grade in sorted(summary, key=grade_sort_key):
        for filename, _, _ in summary[grade]:
            titles.append(pathlib.Path(filename).stem.replace("人教版初中英语-", ""))
    return "已整理人教版初中英语" + "、".join(titles) if titles else "待整理"


def write_root_readme(summary: dict[str, list[tuple[str, int, str]]]) -> None:
    lines = [
        "# 初中单词整理",
        "",
        "- 根目录：`初中/`",
        "- 翻译来源：`https://english.mikigo.site/`",
        "- 音标来源：有道词典（英式 / 美式）",
        "- 说明：词组缺少直出音标时，按组成词音标拼接供参考",
        f"- 当前状态：{build_status_text(summary)}",
        "",
        "| 年级 | 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- | --- |",
    ]
    for grade in sorted(summary, key=grade_sort_key):
        for filename, count, note in summary[grade]:
            lines.append(f"| {grade} | {filename} | {count} | {note} |")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def rewrite_grade_readmes(summary: dict[str, list[tuple[str, int, str]]]) -> None:
    for grade, rows in summary.items():
        write_grade_readme(grade, OUTPUT_ROOT / grade, rows)


def main() -> None:
    base.PRIMARY_INDEX_URL = (
        f"{base.BASE_URL}/%E4%BA%BA%E6%95%99%E7%89%88%E5%88%9D%E4%B8%AD/index.html"
    )
    base.TARGET_GRADES = {"八年级", "九年级"}
    base.OUTPUT_ROOT = OUTPUT_ROOT
    base.BOOK_LINK_RE = re.compile(
        r'href="(/人教版初中/人教版初中英语-[^"/]+/\d+_[^"]+\.html)"'
    )
    base.GRADE_RE = re.compile(r"(七年级|八年级|九年级)")
    base.write_grade_readme = write_grade_readme

    base.main()
    summary = load_grade_summaries()
    rewrite_grade_readmes(summary)
    write_root_readme(summary)


if __name__ == "__main__":
    main()
