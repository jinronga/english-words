#!/usr/bin/env python3
from __future__ import annotations

import collections
import pathlib
import re
import urllib.parse

import generate_primary_vocab as base


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "高中"
CATEGORY_ORDER = {"必修": 0, "选修": 1}
TABLE_ROW_RE = re.compile(r"^\| (?P<file>[^|]+) \| (?P<count>\d+) \| (?P<note>.*) \|$")
BOOK_NUM_RE = re.compile(r"(必修|选修)(\d+)")
BOOK_LINK_RE = re.compile(
    r'href="(/人教版高中/人教版高中英语-[^"/]+/\d+_[^"]+\.html)"'
)
TARGET_BOOK_TITLES = {
    *(f"人教版高中英语-必修{i}" for i in range(1, 6)),
    *(f"人教版高中英语-选修{i}" for i in range(6, 10)),
}


def category_sort_key(category: str) -> tuple[int, str]:
    return CATEGORY_ORDER.get(category, 999), category


def book_sort_key(value: str) -> tuple[int, int, str]:
    match = BOOK_NUM_RE.search(value)
    if not match:
        return 999, 999, value
    category, number = match.groups()
    return CATEGORY_ORDER.get(category, 999), int(number), value


def parse_category(book_title: str) -> str:
    match = BOOK_NUM_RE.search(book_title)
    if not match:
        raise ValueError(f"cannot infer category from {book_title}")
    return match.group(1)


def parse_book_links(index_html: str) -> collections.OrderedDict[str, list[str]]:
    books: collections.OrderedDict[str, list[str]] = collections.OrderedDict()
    for href in BOOK_LINK_RE.findall(index_html):
        decoded = urllib.parse.unquote(href)
        parts = decoded.strip("/").split("/")
        if len(parts) < 3:
            continue
        book_title = parts[1]
        if book_title not in TARGET_BOOK_TITLES:
            continue
        full_url = urllib.parse.urljoin(base.BASE_URL, href)
        books.setdefault(book_title, [])
        if full_url not in books[book_title]:
            books[book_title].append(full_url)

    ordered_books = collections.OrderedDict()
    for book_title in sorted(books, key=book_sort_key):
        urls = books[book_title]
        urls.sort(key=base.page_sort_key)
        ordered_books[book_title] = urls
    return ordered_books


def write_category_readme(
    category: str,
    output_dir: pathlib.Path,
    summary_rows: list[tuple[str, int, str]],
) -> None:
    lines = [
        f"# 高中{category}单词整理",
        "",
        f"- 目录结构：`高中/{category}/`",
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


def parse_category_readme(readme_path: pathlib.Path) -> list[tuple[str, int, str]]:
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


def load_category_summaries() -> dict[str, list[tuple[str, int, str]]]:
    summary: dict[str, list[tuple[str, int, str]]] = {}
    if not OUTPUT_ROOT.exists():
        return summary

    for category_dir in sorted(
        (path for path in OUTPUT_ROOT.iterdir() if path.is_dir()),
        key=lambda path: category_sort_key(path.name),
    ):
        readme_path = category_dir / "README.md"
        if not readme_path.exists():
            continue
        rows = parse_category_readme(readme_path)
        if rows:
            rows.sort(key=lambda item: book_sort_key(item[0]))
            summary[category_dir.name] = rows
    return summary


def build_status_text(summary: dict[str, list[tuple[str, int, str]]]) -> str:
    titles: list[str] = []
    for category in sorted(summary, key=category_sort_key):
        for filename, _, _ in summary[category]:
            titles.append(pathlib.Path(filename).stem.replace("人教版高中英语-", ""))
    return "已整理人教版高中英语" + "、".join(titles) if titles else "待整理"


def write_root_readme(summary: dict[str, list[tuple[str, int, str]]]) -> None:
    lines = [
        "# 高中单词整理",
        "",
        "- 根目录：`高中/`",
        "- 翻译来源：`https://english.mikigo.site/`",
        "- 音标来源：有道词典（英式 / 美式）",
        "- 说明：词组缺少直出音标时，按组成词音标拼接供参考",
        f"- 当前状态：{build_status_text(summary)}",
        "",
        "| 类别 | 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- | --- |",
    ]
    for category in sorted(summary, key=category_sort_key):
        for filename, count, note in summary[category]:
            lines.append(f"| {category} | {filename} | {count} | {note} |")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def rewrite_category_readmes(summary: dict[str, list[tuple[str, int, str]]]) -> None:
    for category, rows in summary.items():
        write_category_readme(category, OUTPUT_ROOT / category, rows)


def main() -> None:
    base.PRIMARY_INDEX_URL = (
        f"{base.BASE_URL}/%E4%BA%BA%E6%95%99%E7%89%88%E9%AB%98%E4%B8%AD/index.html"
    )
    base.OUTPUT_ROOT = OUTPUT_ROOT
    base.BOOK_LINK_RE = BOOK_LINK_RE
    base.GRADE_RE = re.compile(r"(必修|选修)")
    base.TARGET_GRADES = {"必修", "选修"}
    base.parse_book_links = parse_book_links
    base.parse_grade = parse_category
    base.write_grade_readme = write_category_readme

    base.main()
    summary = load_category_summaries()
    rewrite_category_readmes(summary)
    write_root_readme(summary)


if __name__ == "__main__":
    main()
