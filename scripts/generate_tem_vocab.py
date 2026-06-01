#!/usr/bin/env python3
from __future__ import annotations

import collections
import datetime as dt
import html
import pathlib
import re
import urllib.parse
import urllib.request

from generate_cet_vocab import (
    escape_cell,
    example_sentences,
    primary_chinese,
    translate_sentence,
)
from generate_primary_vocab import PhoneticResolver, format_phone


BASE_URL = "https://english.mikigo.site"
ROOT = pathlib.Path(__file__).resolve().parents[1]
TODAY = dt.date.today().isoformat()
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
)
WHITESPACE_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"<[^>]+>")
INDEX_LINK_RE = re.compile(
    r'<a href="([^"]+)" class="rp-overview-group__item__title__link rp-link">.*?</a>',
    re.S,
)
DOC_RE = re.compile(r'<div class="rp-doc rspress-doc">.*?</h1>(.*?)<div class="rp-doc-footer"', re.S)
ENTRY_RE = re.compile(
    r'<h2[^>]*>\s*<a[^>]*>.*?</a>\s*(\d+)\.\s*([^<]+)</h2>(.*?)(?=<h2[^>]*>|<div class="rp-doc-footer")',
    re.S,
)
PHONE_RE = re.compile(r"<p>\s*<code>(.*?)</code>\s*<strong>(.*?)</strong>\s*</p>", re.S)
EXAMPLE_CALLOUT_RE = re.compile(
    r'<div class="rp-callout__title">🎤例句</div><div class="rp-callout__content"><ul>(.*?)</ul>',
    re.S,
)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.S)

SOURCES = [
    {
        "name": "专四",
        "code": "TEM4",
        "index_url": "https://english.mikigo.site/%E4%B8%93%E5%9B%9B/index.html",
    },
    {
        "name": "专八",
        "code": "TEM8",
        "index_url": "https://english.mikigo.site/%E4%B8%93%E5%85%AB/index.html",
    },
]


def fetch_text(url: str) -> str:
    req = urllib.request.Request(encode_url(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def encode_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parsed.path, safe="/%")
    query = urllib.parse.quote_plus(parsed.query, safe="=&%")
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, path, query, parsed.fragment)
    )


def strip_tags(text: str) -> str:
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    return WHITESPACE_RE.sub(" ", text).strip()


def clean_phone(phone: str) -> str | None:
    return PhoneticResolver._clean_phone(strip_tags(phone))


def clean_translation(text: str) -> str:
    return strip_tags(text).replace("|", "\\|")


def page_sort_key(url: str) -> tuple[int, str]:
    filename = urllib.parse.unquote(url.rstrip("/").split("/")[-1])
    prefix = filename.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 0, filename)


def collect_index_links(index_url: str) -> dict[str, list[str]]:
    html_text = fetch_text(index_url)
    groups: dict[str, list[str]] = collections.OrderedDict()
    for href in INDEX_LINK_RE.findall(html_text):
        href = html.unescape(href)
        parts = urllib.parse.unquote(href).strip("/").split("/")
        if len(parts) < 3:
            continue
        group = parts[1]
        full_url = urllib.parse.urljoin(BASE_URL, href)
        groups.setdefault(group, [])
        if full_url not in groups[group]:
            groups[group].append(full_url)

    for urls in groups.values():
        urls.sort(key=page_sort_key)
    return groups


def split_example(text: str) -> tuple[str, str]:
    text = strip_tags(text)
    match = re.match(r"^(.*?)（(.+?)）$", text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return text, ""


def first_example(block: str, word: str, translations: str) -> tuple[str, str]:
    match = EXAMPLE_CALLOUT_RE.search(block)
    if match:
        for item in LI_RE.findall(match.group(1)):
            sentence, translation = split_example(item)
            if sentence:
                return sentence, translation

    sentence = example_sentences(word)[0]
    return sentence, translate_sentence(sentence, word, translations)


def parse_entries(page_html: str) -> list[dict[str, str]]:
    doc_match = DOC_RE.search(page_html)
    doc_html = doc_match.group(1) if doc_match else page_html
    entries: list[dict[str, str]] = []

    for _, raw_word, block in ENTRY_RE.findall(doc_html):
        word = strip_tags(raw_word)
        phone_rows = PHONE_RE.findall(block)
        phones: list[str] = []
        translations: list[str] = []
        for raw_phone, raw_translation in phone_rows:
            phone = clean_phone(raw_phone)
            translation = clean_translation(raw_translation)
            if phone and phone not in phones:
                phones.append(phone)
            if translation and translation not in translations:
                translations.append(translation)

        if not word or not translations:
            continue

        translation_text = "；".join(translations)
        example, example_translation = first_example(block, word, translation_text)
        phone_text = phones[0] if phones else ""
        entries.append(
            {
                "word": word,
                "uk": phone_text,
                "us": phone_text,
                "translation": translation_text,
                "example": example,
                "example_translation": example_translation,
            }
        )

    return entries


def append_more_examples(lines: list[str], rows: list[dict[str, str]]) -> None:
    lines.extend(["", "## 更多例句", ""])
    for idx, row in enumerate(rows, start=1):
        word = row["word"]
        translations = row["translation"]
        lines.append(f"### {idx}. {word}")
        if row["example"]:
            lines.append(f"1. {row['example']}")
            lines.append(f"   中文：{row['example_translation'] or primary_chinese(translations)}")
        for sentence_idx, sentence in enumerate(example_sentences(word)[1:], start=2):
            lines.append(f"{sentence_idx}. {sentence}")
            lines.append(f"   中文：{translate_sentence(sentence, word, translations)}")
        lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()


def build_vocab_page(source: dict, group: str, rows: list[dict[str, str]], urls: list[str]) -> str:
    source_links = "、".join(f"[{page_sort_key(url)[0]}]({url})" for url in urls)
    lines = [
        "---",
        f"title: {group}",
        f"description: {group}，共 {len(rows)} 个词条。",
        "---",
        "",
        f"# {group}",
        "",
        f"- 词表来源：{source_links}",
        "- 音标来源：english.mikigo.site 原页面",
        f"- 整理日期：{TODAY}",
        f"- 词条数量：{len(rows)}",
        "",
        "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 | 例句 | 例句翻译 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for idx, row in enumerate(rows, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(idx),
                    escape_cell(row["word"]),
                    format_phone(row["uk"]),
                    format_phone(row["us"]),
                    escape_cell(row["translation"]),
                    escape_cell(row["example"]),
                    escape_cell(row["example_translation"]),
                ]
            )
            + " |"
        )

    append_more_examples(lines, rows)
    return "\n".join(lines) + "\n"


def build_category_readme(source: dict, summaries: list[tuple[str, int]]) -> str:
    lines = [
        f"# {source['name']}单词整理",
        "",
        f"- 根目录：`{source['name']}/`",
        f"- 词表来源：[{source['code']} 分类词库]({source['index_url']})",
        "- 翻译、例句与音标保留自 english.mikigo.site 原页面",
        "",
        "| 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- |",
    ]
    for filename, count in summaries:
        lines.append(f"| [{filename}]({filename}) | {count} | 含音标、中文释义、例句与例句翻译 |")
    return "\n".join(lines) + "\n"


def main() -> None:
    for source in SOURCES:
        output_dir = ROOT / source["name"]
        output_dir.mkdir(parents=True, exist_ok=True)
        summaries: list[tuple[str, int]] = []
        groups = collect_index_links(source["index_url"])

        for group, urls in groups.items():
            rows: list[dict[str, str]] = []
            for url in urls:
                rows.extend(parse_entries(fetch_text(url)))

            filename = f"{group}.md"
            (output_dir / filename).write_text(
                build_vocab_page(source, group, rows, urls),
                encoding="utf-8",
            )
            summaries.append((filename, len(rows)))
            print(f"{source['name']} {group}: wrote {len(rows)} entries")

        (output_dir / "README.md").write_text(
            build_category_readme(source, summaries),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
