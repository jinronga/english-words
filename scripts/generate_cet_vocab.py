#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import urllib.request

from generate_primary_vocab import PHONETIC_NOTE, PhoneticResolver, format_phone


ROOT = pathlib.Path(__file__).resolve().parents[1]
TODAY = dt.date.today().isoformat()
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
)
WHITESPACE_RE = re.compile(r"\s+")
TABLE_HEADER = "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 | 例句 | 例句翻译 |"
TABLE_DIVIDER = "| --- | --- | --- | --- | --- | --- | --- |"
CET_MANUAL_PHONETICS = {
    "against": ("əˈɡenst; əˈɡeɪnst", "əˈɡenst; əˈɡeɪnst"),
    "proximately": ("ˈprɒksɪmətli", "ˈprɑːksɪmətli"),
    "reservior": ("ˈrezəvwɑː(r)", "ˈrezərvwɑːr"),
}

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


def resolve_cet_phonetics(
    resolver: PhoneticResolver, word: str
) -> tuple[str | None, str | None, bool]:
    manual = CET_MANUAL_PHONETICS.get(word)
    if manual:
        return manual[0], manual[1], False
    return resolver.resolve_term(word)


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


def build_vocab_page(
    source: dict,
    rows: list[dict],
    resolved_phonetics: list[tuple[str, str, bool]],
    missing_terms: list[str],
    composed_terms: list[str],
) -> str:
    lines = [
        "---",
        f"title: {source['title']}",
        f"description: {source['title']}，共 {len(rows)} 个词条。",
        "---",
        "",
        f"# {source['title']}",
        "",
        f"- 词表来源：[{source['code']} 顺序词库]({source['url']})",
        "- 音标来源：有道词典（英式 / 美式）",
        f"- 整理日期：{TODAY}",
        f"- 词条数量：{len(rows)}",
    ]
    if composed_terms:
        lines.append(f"- 音标备注：{PHONETIC_NOTE}（{'、'.join(composed_terms)}）")
    if missing_terms:
        lines.append(f"- 音标缺失：{'、'.join(missing_terms)}")
    lines.extend(["", TABLE_HEADER, TABLE_DIVIDER])
    example_rows: list[tuple[str, str, str]] = []

    for index, (entry, (uk, us, _)) in enumerate(
        zip(rows, resolved_phonetics), start=1
    ):
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
                    format_phone(uk),
                    format_phone(us),
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


def build_category_readme(
    source: dict,
    count: int,
    missing_terms: list[str],
    composed_terms: list[str],
) -> str:
    filename = source["filename"]
    note = "顺序版；含英式/美式音标、中文释义、例句与例句翻译"
    if composed_terms:
        note += f"；含词组拼接音标：{'、'.join(composed_terms)}"
    if missing_terms:
        note += f"；缺音标：{'、'.join(missing_terms)}"
    return "\n".join(
        [
            f"# {source['name']}单词整理",
            "",
            f"- 根目录：`{source['name']}/`",
            f"- 词表来源：[{source['code']} 顺序词库]({source['url']})",
            "- 音标补充自有道词典",
            f"- 说明：{PHONETIC_NOTE}",
            "",
            "| 文件 | 词条数量 | 备注 |",
            "| --- | --- | --- |",
            f"| [{filename}]({filename}) | {count} | {note} |",
            "",
        ]
    )


def main() -> None:
    resolver = PhoneticResolver()
    for source in SOURCES:
        rows = fetch_json(source["url"])
        resolved_phonetics: list[tuple[str, str, bool]] = []
        missing_terms: list[str] = []
        composed_terms: list[str] = []
        for entry in rows:
            word = normalize(entry.get("word"))
            uk, us, used_composition = resolve_cet_phonetics(resolver, word)
            resolved_phonetics.append((uk or "", us or "", used_composition))
            if used_composition:
                composed_terms.append(word)
            if not uk and not us:
                missing_terms.append(word)

        output_dir = ROOT / source["name"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source["filename"]).write_text(
            build_vocab_page(
                source,
                rows,
                resolved_phonetics,
                missing_terms,
                composed_terms,
            ),
            encoding="utf-8",
        )
        (output_dir / "README.md").write_text(
            build_category_readme(
                source,
                len(rows),
                missing_terms,
                composed_terms,
            ),
            encoding="utf-8",
        )
        print(
            f"{source['name']}: wrote {len(rows)} entries, "
            f"missing phonetics: {len(missing_terms)}"
        )


if __name__ == "__main__":
    main()
