#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""review_extract.py — 第二层审稿的素材提取器（零依赖）

只做一件事：把人工审稿需要看的东西从稿子里抽出来，按 review-layers.md
的四层顺序摆好，省得审稿时在原文里来回找。它不评分、不判断。

用法：
    python3 scripts/review_extract.py 稿子.md
    python3 scripts/review_extract.py --json 稿子.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ai_tell_lint import (  # noqa: E402
    IMAGERY_WORDS,
    cjk_count,
    clean_text,
    split_paragraphs,
    split_sentences,
)

QUOTE_RE = re.compile(r"[「“\"]([^」”\"]{1,60})[」”\"]")
SAY_RE = re.compile(r"(?:说|问|答|道|喊|念叨)[，,：:]\s*([^。！？!?\n]{2,40})[。！？!?]")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?|[一二三四五六七八九十百千万两]+(?:分钟|小时|天|周|个月|年|岁|个|节|道|页|块|米|次|遍|版|点|步|句|篇)")
TIME_WORDS = ["早上", "上午", "中午", "下午", "晚上", "昨天", "今天", "明天", "上周", "下周", "去年", "今年", "后来", "当时", "以前"]


def short(s: str, n: int = 46) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def extract(text: str) -> dict:
    clean = clean_text(text)
    paragraphs = split_paragraphs(clean)
    sentences = split_sentences(clean)

    quotes = [q.strip() for q in QUOTE_RE.findall(clean)]
    said = [s.strip() for s in SAY_RE.findall(clean)]
    numbers = NUMBER_RE.findall(clean)
    times = [w for w in TIME_WORDS if w in clean]
    imagery = [w for w in IMAGERY_WORDS if w in clean]

    skeleton = []
    for i, para in enumerate(paragraphs, 1):
        ps = split_sentences(para)
        if not ps:
            continue
        skeleton.append({
            "段": i,
            "字数": cjk_count(para),
            "首句": short(ps[0]),
            "末句": short(ps[-1]),
        })

    return {
        "字数": cjk_count(clean),
        "段数": len(paragraphs),
        "句数": len(sentences),
        "段落骨架": skeleton,
        "引号内台词": list(dict.fromkeys(quotes))[:20],
        "说/问/答后的台词": list(dict.fromkeys(said))[:20],
        "数字与数量": list(dict.fromkeys(numbers))[:20],
        "时间词": times,
        "意象词候选": imagery,
        "结尾三段": [short(p, 120) for p in paragraphs[-3:]],
    }


def print_report(path: str, data: dict) -> None:
    print(f"\n== 审稿素材：{path} ==")
    print(f"字数 {data['字数']} | 段 {data['段数']} | 句 {data['句数']}")
    print("\n[L2 逻辑 / 结构] 段落骨架（看行动线、时间线、首尾是否都在推进）")
    for row in data["段落骨架"]:
        print(f"  {row['段']:>2}. ({row['字数']}字) 首：{row['首句']}")
        print(f"      末：{row['末句']}")
    print("\n[L3 人物台词] 引号内台词")
    for q in data["引号内台词"]:
        print(f"  - {q}")
    print("\n[L3 人物台词] 说 / 问 / 答 后的台词（重点看是否格言化）")
    for q in data["说/问/答后的台词"]:
        print(f"  - {q}")
    print("\n[L3 细节] 数字与数量")
    print("  " + ("、".join(data["数字与数量"]) if data["数字与数量"] else "（无）"))
    print("[L3 细节] 时间词")
    print("  " + ("、".join(data["时间词"]) if data["时间词"] else "（无）"))
    print("[L3 细节] 意象词候选（作文：超过 1 个要删）")
    print("  " + ("、".join(data["意象词候选"]) if data["意象词候选"] else "（无）"))
    print("\n[L4 结构] 结尾三段")
    for p in data["结尾三段"]:
        print(f"  - {p}")
    print("\n下一步：按 references/review-layers.md 回答 L2–L4，并打 A 卡（真实感）/ B 卡（文笔）。")


def main() -> int:
    parser = argparse.ArgumentParser(description="第二层审稿素材提取器")
    parser.add_argument("file", nargs="?", help="待审文件；留空则读 stdin")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
        label = args.file
    else:
        raw = sys.stdin.read()
        label = "<stdin>"

    data = extract(raw)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_report(label, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
