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
TABLE_HEADER = "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 | 例句 | 例句翻译 |"
TABLE_DIVIDER = "| --- | --- | --- | --- | --- | --- | --- |"

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


def primary_chinese(translations: str) -> str:
    text = normalize(translations)
    text = re.sub(r"\b[a-z]+\.\s*", "", text, flags=re.I)
    text = re.sub(r"[（(][^）)]*[）)]", "", text)
    text = re.sub(r"^[^一-龥]*", "", text).strip()
    for part in re.split(r"[；;，,、/]| 或 | 和 |及|等", text):
        part = part.strip(" .。:：；;，,、")
        if part:
            return part
    return text or "这个词"


def quote_word(word: str) -> str:
    return f"“{word}”"


def example_sentences(word: str) -> list[str]:
    return [
        f'We learned the word "{word}" today.',
        f'Please read "{word}" aloud.',
        f'Can you use "{word}" in your own sentence?',
    ]


def translate_sentence(sentence: str, word: str, translations: str) -> str:
    quoted = quote_word(word)
    meaning = primary_chinese(translations)
    if sentence == f'We learned the word "{word}" today.':
        return f"我们今天学习了单词{quoted}，意思与“{meaning}”有关。"
    if sentence == f'Please read "{word}" aloud.':
        return f"请大声读出单词{quoted}。"
    if sentence == f'Can you use "{word}" in your own sentence?':
        return f"你能用单词{quoted}造一个自己的句子吗？"
    return f"这个句子使用了单词{quoted}，意思与“{meaning}”有关。"


def append_more_examples(lines: list[str], rows: list[tuple[str, str, str]]) -> None:
    lines.extend(["", "## 更多例句", ""])
    for idx, word, translations in rows:
        lines.append(f"### {idx}. {word}")
        for sentence_idx, sentence in enumerate(example_sentences(word), start=1):
            lines.append(f"{sentence_idx}. {sentence}")
            lines.append(f"   中文：{translate_sentence(sentence, word, translations)}")
        lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()


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
        "- 说明：本页保留单词、中文释义、例句与例句翻译，音标暂以 `-` 占位。",
        "",
        TABLE_HEADER,
        TABLE_DIVIDER,
    ]
    example_rows: list[tuple[str, str, str]] = []

    for index, entry in enumerate(rows, start=1):
        word = normalize(entry.get("word"))
        translations = format_translations(entry)
        sentence = example_sentences(word)[0]
        sentence_translation = translate_sentence(sentence, word, translations)
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    escape_cell(word),
                    "-",
                    "-",
                    escape_cell(translations),
                    escape_cell(sentence),
                    escape_cell(sentence_translation),
                ]
            )
            + " |"
        )
        example_rows.append((str(index), word, translations))

    append_more_examples(lines, example_rows)
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
            "- 说明：本词表保留单词、中文释义、例句与例句翻译，音标暂以 `-` 占位。",
            "",
            "| 文件 | 词条数量 | 备注 |",
            "| --- | --- | --- |",
            f"| [{filename}]({filename}) | {count} | 顺序版；含中文释义、例句与例句翻译 |",
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
