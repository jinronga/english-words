#!/usr/bin/env python3
from __future__ import annotations

import collections
import datetime as dt
import html
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request


BASE_URL = "https://english.mikigo.site"
PRIMARY_INDEX_URL = f"{BASE_URL}/%E4%BA%BA%E6%95%99%E7%89%88%E5%B0%8F%E5%AD%A6/index.html"
YOUDAO_API = "https://dict.youdao.com/jsonapi?q={query}"
TARGET_GRADES = {"四年级", "五年级", "六年级"}
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "小学"
TODAY = dt.date.today().isoformat()
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
)

BOOK_LINK_RE = re.compile(
    r'href="(/人教版小学/人教版小学英语-[^"/]+/\d+_[^"]+\.html)"'
)
ENTRY_RE = re.compile(
    r"<h2[^>]*>(?:<a[^>]*>.*?</a>)?\s*(\d+)\.\s*(.*?)</h2>\s*<p>(.*?)</p>",
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
GRADE_RE = re.compile(r"(三年级|四年级|五年级|六年级)")
PUNCT_TRIM_CHARS = " \t\r\n!?.,;:()[]{}\"“”‘’"
COMPOSITION_SKIP_TOKENS = {"sb", "sth"}

PHONETIC_NOTE = "词组缺少直出音标时，按组成词音标拼接供参考"
SIBILANT_ENDINGS = ("s", "z", "ʃ", "ʒ", "tʃ", "dʒ")
VOICELESS_ENDINGS = ("p", "k", "f", "s", "ʃ", "tʃ", "θ")
TERM_QUERY_ALIASES = {
    "have...class": "have class",
    "having...class": "having class",
    "how about...": "how about",
}
MANUAL_PHONETICS = {
    "P.E.": ("ˌpiː ˈiː", "ˌpiː ˈiː"),
    "do kung fu": ("duː; də ˌkʌŋ ˈfuː", "duː; də ˌkʌŋ ˈfuː"),
    "heavier": ("ˈhevɪə(r)", "ˈhevɪər"),
    "pipa": ("pɪˈpɑː; ˈpaɪpə; ˈpɪpə", "pɪˈpɑː; ˈpaɪpə; ˈpɪpə"),
}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(encode_url(url), headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}")


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(encode_url(url), headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}")


def strip_tags(text: str) -> str:
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    return WHITESPACE_RE.sub(" ", text).strip()


def encode_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parsed.path, safe="/%")
    query = urllib.parse.quote_plus(parsed.query, safe="=&%")
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, path, query, parsed.fragment)
    )


def normalize_translation(text: str) -> str:
    text = strip_tags(text)
    first_cjk = re.search(r"[\u4e00-\u9fff（《【“‘]", text)
    if first_cjk:
        text = text[first_cjk.start() :].strip()
    return text


def normalize_word(text: str) -> str:
    return strip_tags(text)


def normalize_query_term(term: str) -> str:
    term = (
        term.replace("...", " ")
        .replace("…", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
    )
    return WHITESPACE_RE.sub(" ", term.strip()).strip(PUNCT_TRIM_CHARS)


def parse_book_links(index_html: str) -> collections.OrderedDict[str, list[str]]:
    books: collections.OrderedDict[str, list[str]] = collections.OrderedDict()
    for href in BOOK_LINK_RE.findall(index_html):
        decoded = urllib.parse.unquote(href)
        parts = decoded.strip("/").split("/")
        if len(parts) < 3:
            continue
        book_title = parts[1]
        grade_match = GRADE_RE.search(book_title)
        if not grade_match or grade_match.group(1) not in TARGET_GRADES:
            continue
        full_url = urllib.parse.urljoin(BASE_URL, href)
        books.setdefault(book_title, [])
        if full_url not in books[book_title]:
            books[book_title].append(full_url)
    for urls in books.values():
        urls.sort(key=page_sort_key)
    return books


def page_sort_key(url: str) -> int:
    filename = urllib.parse.unquote(url.rstrip("/").split("/")[-1])
    prefix = filename.split("_", 1)[0]
    return int(prefix)


def parse_entries(page_html: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for _, word_html, translation_html in ENTRY_RE.findall(page_html):
        word = normalize_word(word_html)
        translation = normalize_translation(translation_html)
        if word and translation:
            entries.append((word, translation))
    return entries


def parse_grade(book_title: str) -> str:
    match = GRADE_RE.search(book_title)
    if not match:
        raise ValueError(f"cannot infer grade from {book_title}")
    return match.group(1)


def format_phone(phone: str | None) -> str:
    return f"[{phone}]" if phone else "-"


class PhoneticResolver:
    def __init__(self) -> None:
        self.term_cache: dict[str, tuple[str | None, str | None, bool]] = {}
        self.token_cache: dict[str, tuple[str | None, str | None]] = {}

    def resolve_term(self, term: str) -> tuple[str | None, str | None, bool]:
        if term in self.term_cache:
            return self.term_cache[term]

        manual = MANUAL_PHONETICS.get(term)
        if manual:
            self.term_cache[term] = (manual[0], manual[1], False)
            return self.term_cache[term]

        uk, us = self._query_youdao_simple(term)
        if not uk or not us:
            token_uk, token_us = self._resolve_token(term)
            if not uk:
                uk = token_uk
            if not us:
                us = token_us
        used_composition = False
        if any(mark in term for mark in (" ", "'", "-", "...", "…", "/", "(", ")")) and (not uk or not us):
            composed_uk, composed_us = self._compose_phrase(term)
            if composed_uk or composed_us:
                if not uk:
                    uk = composed_uk
                if not us:
                    us = composed_us
                used_composition = True

        self.term_cache[term] = (uk, us, used_composition)
        return self.term_cache[term]

    def _compose_phrase(self, term: str) -> tuple[str | None, str | None]:
        raw_term = (
            term.replace("...", " ")
            .replace("…", " ")
            .replace("/", " ")
            .replace("(", " ")
            .replace(")", " ")
        )
        raw_tokens = re.split(r"[ -]+", raw_term)
        tokens = [normalize_query_term(token) for token in raw_tokens]
        tokens = [token for token in tokens if token and token.lower() not in COMPOSITION_SKIP_TOKENS]
        uk_parts: list[str] = []
        us_parts: list[str] = []
        all_uk = True
        all_us = True

        for token in tokens:
            token_uk, token_us = self._resolve_token(token)
            if token_uk:
                uk_parts.append(token_uk)
            else:
                all_uk = False
            if token_us:
                us_parts.append(token_us)
            else:
                all_us = False

        return (
            " ".join(uk_parts) if all_uk and uk_parts else None,
            " ".join(us_parts) if all_us and us_parts else None,
        )

    def _resolve_token(self, token: str) -> tuple[str | None, str | None]:
        token = normalize_query_term(token)
        if token in self.token_cache:
            return self.token_cache[token]

        manual = MANUAL_PHONETICS.get(token)
        if manual:
            self.token_cache[token] = manual
            return self.token_cache[token]

        uk, us = self._query_youdao_simple(token)
        if token.endswith("'s") and (not uk or not us):
            base = token[:-2]
            base_uk, base_us = self._resolve_token(base)
            if base_uk and not uk:
                uk = self._append_possessive(base_uk)
            if base_us and not us:
                us = self._append_possessive(base_us)
        elif token.endswith("s") and len(token) > 3 and (not uk or not us):
            base = token[:-1]
            base_uk, base_us = self._resolve_token(base)
            if base_uk and not uk:
                uk = self._append_plural(base_uk)
            if base_us and not us:
                us = self._append_plural(base_us)
        elif token.endswith("ed") and len(token) > 4 and (not uk or not us):
            base = token[:-2]
            base_uk, base_us = self._resolve_token(base)
            if base_uk and not uk:
                uk = self._append_past_tense(base_uk)
            if base_us and not us:
                us = self._append_past_tense(base_us)

        self.token_cache[token] = (uk, us)
        return self.token_cache[token]

    def _query_youdao_simple(self, term: str) -> tuple[str | None, str | None]:
        for query_term in self._candidate_query_terms(term):
            url = YOUDAO_API.format(query=urllib.parse.quote(query_term))
            data = fetch_json(url)
            words = ((data.get("simple") or {}).get("word") or [])
            if not words:
                continue
            item = words[0]
            uk = self._clean_phone(item.get("ukphone"))
            us = self._clean_phone(item.get("usphone"))
            if uk or us:
                return uk, us
        return None, None

    @staticmethod
    def _candidate_query_terms(term: str) -> list[str]:
        candidates: list[str] = []
        seen: set[str] = set()
        for value in (
            term,
            TERM_QUERY_ALIASES.get(term),
            normalize_query_term(term),
            TERM_QUERY_ALIASES.get(normalize_query_term(term)),
            normalize_query_term(term).replace(".", ""),
        ):
            if not value:
                continue
            normalized = WHITESPACE_RE.sub(" ", value).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                candidates.append(normalized)
        return candidates

    @staticmethod
    def _clean_phone(phone: str | None) -> str | None:
        if not phone:
            return None
        phone = WHITESPACE_RE.sub(" ", str(phone)).strip()
        phone = re.sub(r"(^|\s),(?=\S)", r"\1ˌ", phone)
        phone = re.sub(r"(^|\s)'(?=\S)", r"\1ˈ", phone)
        phone = re.sub(r"'(?=\S)", "ˈ", phone)
        phone = phone.replace(":", "ː")
        return phone or None

    @staticmethod
    def _append_possessive(phone: str) -> str:
        base = phone.replace("(r)", "")
        suffix = "ɪz" if base.endswith(SIBILANT_ENDINGS) else "z"
        return f"{base}{suffix}"

    @staticmethod
    def _append_plural(phone: str) -> str:
        base = phone.replace("(r)", "")
        suffix = "ɪz" if base.endswith(SIBILANT_ENDINGS) else "z"
        return f"{base}{suffix}"

    @staticmethod
    def _append_past_tense(phone: str) -> str:
        base = phone.replace("(r)", "")
        if base.endswith(("t", "d")):
            suffix = "ɪd"
        elif base.endswith(VOICELESS_ENDINGS):
            suffix = "t"
        else:
            suffix = "d"
        return f"{base}{suffix}"


def write_markdown(
    book_title: str,
    source_urls: list[str],
    rows: list[tuple[str, str, str, str]],
    output_path: pathlib.Path,
    used_composition_terms: list[str],
    missing_terms: list[str],
) -> None:
    source_links = "、".join(f"[{url}]({url})" for url in source_urls)
    lines = [
        f"# {book_title}",
        "",
        f"- 来源页面：{source_links}",
        "- 翻译来源：english.mikigo.site 原页面",
        "- 音标来源：有道词典（英式 / 美式）",
        f"- 整理日期：{TODAY}",
        f"- 词条数量：{len(rows)}",
    ]
    if used_composition_terms:
        joined_terms = "、".join(used_composition_terms)
        lines.append(f"- 音标备注：{PHONETIC_NOTE}（{joined_terms}）")
    if missing_terms:
        joined_terms = "、".join(missing_terms)
        lines.append(f"- 音标缺失：{joined_terms}")
    lines.extend(
        [
            "",
            "| 序号 | 单词 | 英式音标 | 美式音标 | 中文翻译 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for idx, (word, uk, us, translation) in enumerate(rows, start=1):
        lines.append(f"| {idx} | {word} | {uk} | {us} | {translation} |")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_grade_readme(
    grade: str,
    output_dir: pathlib.Path,
    summary_rows: list[tuple[str, int, str]],
) -> None:
    lines = [
        f"# 小学{grade}单词整理",
        "",
        f"- 目录结构：`小学/{grade}/`",
        "- 翻译保留自原学习网站页面",
        "- 音标补充自有道词典",
        f"- 说明：{PHONETIC_NOTE}",
        "",
        "| 文件 | 词条数量 | 备注 |",
        "| --- | --- | --- |",
    ]
    for filename, count, note in summary_rows:
        lines.append(f"| {filename} | {count} | {note} |")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> dict[str, list[tuple[str, int, str]]]:
    index_html = fetch_text(PRIMARY_INDEX_URL)
    books = parse_book_links(index_html)
    resolver = PhoneticResolver()
    grade_summary: dict[str, list[tuple[str, int, str]]] = collections.defaultdict(list)

    for book_title, page_urls in books.items():
        seen_words: set[str] = set()
        book_entries: list[tuple[str, str]] = []
        for page_url in page_urls:
            page_html = fetch_text(page_url)
            for word, translation in parse_entries(page_html):
                if word in seen_words:
                    continue
                seen_words.add(word)
                book_entries.append((word, translation))

        rows: list[tuple[str, str, str, str]] = []
        composed_terms: list[str] = []
        missing_terms: list[str] = []
        for word, translation in book_entries:
            uk, us, used_composition = resolver.resolve_term(word)
            rows.append((word, format_phone(uk), format_phone(us), translation))
            if used_composition:
                composed_terms.append(word)
            if not uk and not us:
                missing_terms.append(word)

        grade = parse_grade(book_title)
        grade_dir = OUTPUT_ROOT / grade
        output_path = grade_dir / f"{book_title}.md"
        write_markdown(
            book_title,
            page_urls,
            rows,
            output_path,
            composed_terms,
            missing_terms,
        )

        note = "完整"
        if composed_terms:
            note = f"含词组拼接音标：{'、'.join(composed_terms)}"
        if missing_terms:
            missing_note = f"缺音标：{'、'.join(missing_terms)}"
            note = f"{note}；{missing_note}" if note != "完整" else missing_note
        grade_summary[grade].append((output_path.name, len(rows), note))

    for grade, summary_rows in grade_summary.items():
        summary_rows.sort(key=lambda item: item[0])
        write_grade_readme(grade, OUTPUT_ROOT / grade, summary_rows)

    return grade_summary


if __name__ == "__main__":
    main()
