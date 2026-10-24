#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selftest.py — 验证「去AI味」项目自身是否自洽（零依赖）

做八件事：
1. 样本门槛：口播稿样本的 AI / 人话区分度；
2. 书面样本门槛：公众号文案样本的 AI / 人话区分度；
3. 作文样本门槛：AI 作文 / 人写作文的区分度；
4. 报告样本门槛：AI 总结 / 人写总结的区分度；
5. 案例回归：references/human-voice/rewrite-examples.md 里 13 组
   「AI 原稿 → 改后」逐组跑分，检查改写后是否稳定降分；
6. 分文体档案完整性检查；
7. 检测器单元检查 + 人工复核项 + 优秀文本不误伤；
8. 公文 / 官方文体模式 + 第二层审稿资产。

失败返回非零退出码，改脚本 / 改案例后跑这个做回归。

用法：
    python3 scripts/selftest.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from ai_tell_lint import clean_text, collect_metrics, suggestions  # noqa: E402

SAMPLES = ROOT / "samples"
EXAMPLES = ROOT / "references" / "human-voice" / "rewrite-examples.md"
GENRES = ROOT / "references" / "genres"

GENRE_FILES = [
    "00-文体矩阵.md",
    "01-作文与文学写作.md",
    "02-公众号与文章.md",
    "03-通知与公告.md",
    "04-视频口播.md",
    "05-朋友圈与聊天.md",
    "06-产品与课程文案.md",
    "07-润色与改稿.md",
    "08-报告与总结.md",
    "09-演讲稿.md",
]


def metrics_of(text: str) -> dict:
    return collect_metrics(clean_text(text))


def score(text: str) -> int:
    return metrics_of(text)["AI味风险分"]


def score_genre(text: str, genre: str) -> int:
    return collect_metrics(clean_text(text), genre=genre)["AI味风险分"]


def external_genre(name: str) -> str:
    if name.startswith("notice") or name.startswith("holdout-notice"):
        return "notice"
    if name.startswith("gov-") or name.startswith("holdout-gov"):
        return "gov"
    if name.startswith("article"):
        return "article"
    if name.startswith("report"):
        return "report"
    return "essay"


def hit_names(text: str) -> set[str]:
    m = metrics_of(text)
    names = {hit["类别"] for hit in m.get("词表命中", [])}
    names |= {hit["类别"] for hit in m.get("句式命中", [])}
    return names


def extract_blockquote(section: str, marker: str) -> str:
    """从 section 里 marker 之后抓 markdown 引用块（以 > 开头的行）。"""
    idx = section.find(marker)
    if idx < 0:
        return ""
    lines = section[idx + len(marker):].splitlines()
    out: list[str] = []
    started = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">"):
            started = True
            out.append(re.sub(r"^>\s?", "", stripped))
            continue
        if not started:
            # marker 后面可能剩 "**" 或「（三条消息）」这类尾缀，跳过直到引用块开始
            continue
        if stripped == "":
            # 引用块内的空行：后面还是引用就继续，否则结束
            rest = [s.strip() for s in lines[i + 1:] if s.strip()]
            if rest and rest[0].startswith(">"):
                out.append("")
                continue
            break
        break
    return "\n".join(out).strip()


def extract_pairs(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"\n## 案例 ", text)[1:]
    pairs = []
    for sec in sections:
        title = sec.split("\n", 1)[0].strip()
        original = extract_blockquote(sec, "**AI 原稿**")
        rewrite = extract_blockquote(sec, "**改后")
        if original and rewrite:
            pairs.append((title, original, rewrite))
    return pairs


def section_pair(failures: list[str], label: str, ai_file: str, human_file: str,
                 min_ai: int, max_human: int, min_delta: int, genre: str | None = None) -> None:
    ai_path = SAMPLES / ai_file
    human_path = SAMPLES / human_file
    if not ai_path.exists() or not human_path.exists():
        failures.append(f"{label}：样本文件缺失")
        return
    if genre:
        ai_score = score_genre(ai_path.read_text(encoding="utf-8"), genre)
        human_score = score_genre(human_path.read_text(encoding="utf-8"), genre)
    else:
        ai_score = score(ai_path.read_text(encoding="utf-8"))
        human_score = score(human_path.read_text(encoding="utf-8"))
    print(f"  {ai_file:<22}{ai_score:>3} / 100")
    print(f"  {human_file:<22}{human_score:>3} / 100")
    if ai_score < min_ai:
        failures.append(f"{label}：AI 样本得分过低（{ai_score} < {min_ai}），可能漏判")
    if human_score > max_human:
        failures.append(f"{label}：人话样本得分过高（{human_score} > {max_human}），可能误伤")
    if ai_score - human_score < min_delta:
        failures.append(f"{label}：区分度不足（差值 {ai_score - human_score} < {min_delta}）")


DETECTOR_CASES = [
    ("这不是技术问题，而是管理问题。", "防御性句式", True),
    ("首先，要明确目标。其次，拆解步骤。最后，复盘。", "说明文骨架", True),
    ("随着教育信息化的不断发展，课堂教学正在经历深刻变革。", "书面腔", True),
    ("我们对课堂流程进行了全面优化。", "书面腔", True),
    ("感谢您的反馈，我们会尽快改进。", "客服", True),
    ("今天早上我煮了碗面，吃完就出门了。", "书面腔", False),
    ("正如古人所言，欲速则不达。", "名言撑场", True),
    ("在这个快节奏的时代，我们总是步履匆匆。", "时代腔开场", True),
    ("看似缓慢，却在积蓄力量。", "对举套式", True),
    ("我们要与时俱进、开拓创新、砥砺前行。", "四字格堆砌", True),
    ("第一条：按时提交材料。", "序数词小标题", False),
]


def main() -> int:
    failures: list[str] = []

    print("== 1. 口播样本门槛 ==")
    section_pair(failures, "口播样本", "01-ai-koubo.md", "02-human-koubo.md",
                 min_ai=60, max_human=20, min_delta=40)

    print("\n== 2. 书面文案样本门槛 ==")
    section_pair(failures, "书面样本", "03-ai-copy.md", "04-human-copy.md",
                 min_ai=35, max_human=20, min_delta=25)

    print("\n== 3. 作文样本门槛 ==")
    section_pair(failures, "作文样本", "05-ai-essay.md", "06-human-essay.md",
                 min_ai=35, max_human=15, min_delta=25)

    print("\n== 3b. 报告样本门槛 ==")
    section_pair(failures, "报告样本", "10-ai-report.md", "11-human-report.md",
                 min_ai=30, max_human=15, min_delta=25, genre="report")

    print("\n== 4. 案例回归（references/human-voice/rewrite-examples.md）==")
    if not EXAMPLES.exists():
        failures.append(f"找不到案例文件：{EXAMPLES}")
        pairs = []
    else:
        pairs = extract_pairs(EXAMPLES)
    if len(pairs) != 13:
        failures.append(f"案例抽取数量异常：{len(pairs)}，应为 13")

    improved = 0
    print(f"  {'#':<3}{'案例':<34}{'原稿':>5}{'改后':>5}{'降分':>6}")
    for i, (title, original, rewrite) in enumerate(pairs, 1):
        before = score(original)
        after = score(rewrite)
        delta = before - after
        if after < before:
            improved += 1
        print(f"  {i:<3}{title[:32]:<34}{before:>5}{after:>5}{delta:>6}")

    if pairs:
        avg_before = sum(score(o) for _, o, _ in pairs) / len(pairs)
        avg_after = sum(score(r) for _, _, r in pairs) / len(pairs)
        print(f"\n  平均分：原稿 {avg_before:.1f} → 改后 {avg_after:.1f}"
              f"（平均降 {avg_before - avg_after:.1f}）")
        if improved < 11:
            failures.append(f"改写后降分案例太少：{improved}/13（要求 ≥11）")
        if avg_before - avg_after < 15:
            failures.append(f"平均降分不足：{avg_before - avg_after:.1f}（要求 ≥15）")

    print("\n== 5. 分文体档案完整性 ==")
    for name in GENRE_FILES:
        path = GENRES / name
        if not path.exists():
            print(f"  ✗ 缺失：{name}")
            failures.append(f"分文体档案缺失：{name}")
            continue
        text = path.read_text(encoding="utf-8")
        sections = len(re.findall(r"^## ", text, flags=re.M))
        examples = text.count("改后")
        if name.startswith("00"):
            ok = sections >= 7
            detail = f"{sections} 节"
        else:
            ok = sections >= 8 and examples >= 4
            detail = f"{sections} 节 / {examples} 处改后示例"
        print(f"  {'✓' if ok else '✗'} {name}（{detail}）")
        if not ok:
            failures.append(f"分文体档案结构不完整：{name}（{detail}）")

    print("\n== 6. 检测器单元检查 ==")
    for text, expected, should_hit in DETECTOR_CASES:
        names = hit_names(text)
        hit = any(expected in name for name in names)
        status = "✓" if hit == should_hit else "✗"
        action = "应命中" if should_hit else "不应误伤"
        print(f"  {status} {action}「{expected}」：{text[:22]}")
        if hit != should_hit:
            failures.append(f"检测器错误：{action}「{expected}」，实际命中 {sorted(names)}")

    zero = metrics_of("说实话，很难让人接受。\n\n今天天气不错，我们出门走走。")["人工复核项"]["段首疑似零回指"]
    ok = len(zero) >= 1
    print(f"  {'✓' if ok else '✗'} 人工复核项：段首零回指能被提示（不扣分）")
    if not ok:
        failures.append("人工复核项：段首零回指没有被提示")

    zero_negative = metrics_of(
        "上周听了一节公开课。老师在黑板上写完题，底下没人动笔。\n\n"
        "我后来翻了他的备课本，每道例题旁边都写着两行字。"
    )["人工复核项"]["段首疑似零回指"]
    ok_negative = len(zero_negative) == 0
    print(f"  {'✓' if ok_negative else '✗'} 人工复核项：正常段落不误报段首零回指")
    if not ok_negative:
        failures.append(f"人工复核项误报：{zero_negative}")

    notice_m = collect_metrics(clean_text("10月20日起，数学课换到实验楼302。"), genre="notice")
    ok_genre = notice_m["判定文体"] == "通知"
    print(f"  {'✓' if ok_genre else '✗'} --genre 别名：notice 显示为「通知」（实际：{notice_m['判定文体']}）")
    if not ok_genre:
        failures.append(f"genre 别名异常：notice → {notice_m['判定文体']}")

    print("\n== 6b. 文体豁免 ==")
    for text, genre, category in [
        ("收到，我明白了。", "chat", "收条式应答"),
        ("他仿佛听见了什么。", "essay", "拟人喻体/意义拔高"),
        ("因此，需要调整方案。", "notice", "通用连接/评价词"),
        ("因此，需要调整方案。", "auto", "通用连接/评价词"),
    ]:
        m = collect_metrics(clean_text(text), genre=genre)
        hit = category in m.get("扣分", {})
        print(f"  {'✓' if not hit else '✗'} {genre} 模式不误伤「{category}」：{text}")
        if hit:
            failures.append(f"文体豁免失效：{genre} 仍把「{category}」计入扣分")

    essay_manual = collect_metrics(clean_text("这并非失败，而是另一种开始。"), genre="essay")
    essay_tips = suggestions(essay_manual)
    ok_essay_hint = bool(essay_manual.get("人工复核（文体）")) and any("正常对举" in tip for tip in essay_tips)
    print(f"  {'✓' if ok_essay_hint else '✗'} essay 模式「并非……而是」转人工且有提示")
    if not ok_essay_hint:
        failures.append("essay 模式人工复核提示缺失（人工复核键或 suggestions 输出）")

    chat_formal = collect_metrics(clean_text("这并非失败，而是另一种开始。"), genre="chat")
    ok_chat_penalty = "防御性句式（不是X而是Y）" in chat_formal.get("扣分", {})
    print(f"  {'✓' if ok_chat_penalty else '✗'} chat 模式「并非……而是」仍按防御句式扣分")
    if not ok_chat_penalty:
        failures.append("chat 模式「并非……而是」被错误豁免")

    dense_text = "这并非失败，而是开始。那并非终点，而是过程。另一处并非偶然，而是必然。" * 2
    dense_m = collect_metrics(clean_text(dense_text), genre="essay")
    ok_dense = "防御性句式（不是X而是Y）" in dense_m.get("扣分", {})
    print(f"  {'✓' if ok_dense else '✗'} essay 模式高密度「并非……而是」仍扣分")
    if not ok_dense:
        failures.append("essay 模式高密度「并非……而是」被错误豁免")

    gov_manual = collect_metrics(clean_text("这不是技术问题，而是管理问题。"), genre="gov")
    gov_tips = suggestions(gov_manual)
    ok_gov_hint = bool(gov_manual.get("人工复核（文体）")) and any(
        "四测试" in tip or "official-style" in tip for tip in gov_tips)
    print(f"  {'✓' if ok_gov_hint else '✗'} gov 模式官方对举转人工且有提示")
    if not ok_gov_hint:
        failures.append("gov 模式人工复核提示缺失")

    slogan_m = collect_metrics(clean_text("停三秒，看一眼，再扔。\n\n我的演讲完了，谢谢大家。"), genre="speech")
    slogan_hint = slogan_m.get("人工复核项", {}).get("结尾疑似口号")
    slogan_tips = suggestions(slogan_m)
    ok_slogan = bool(slogan_hint) and any("结尾疑似口号" in tip for tip in slogan_tips)
    print(f"  {'✓' if ok_slogan else '✗'} speech 模式三连短句收尾被提示（不扣分）")
    if not ok_slogan:
        failures.append("speech 模式口号式收尾提示缺失")

    gov_m = collect_metrics(clean_text("在公司的正确领导下，我们围绕年度工作目标努力。"), genre="gov")
    ok_gov = "报告/总结套话" not in gov_m.get("扣分", {})
    print(f"  {'✓' if ok_gov else '✗'} gov 模式不因「报告/总结套话」扣分（交四测试）")
    if not ok_gov:
        failures.append("报告套话词表在 gov 模式仍计分")

    rep_m = collect_metrics(clean_text("在公司的正确领导下，我们围绕年度工作目标努力。"), genre="report")
    ok_rep = "报告/总结套话" in rep_m.get("扣分", {})
    print(f"  {'✓' if ok_rep else '✗'} report 模式仍能检出「报告/总结套话」")
    if not ok_rep:
        failures.append("报告套话词表在 report 模式漏检")

    print("\n== 7. 优秀文本不误伤 ==")
    for fname, label, limit in [
        ("07-excellent-essay.md", "优秀散文", 10),
        ("08-official-notice.md", "规范通知", 15),
    ]:
        path = SAMPLES / fname
        if not path.exists():
            print(f"  ✗ 缺失：{fname}")
            failures.append(f"优秀文本样本缺失：{fname}")
            continue
        s = score(path.read_text(encoding="utf-8"))
        ok = s <= limit
        print(f"  {'✓' if ok else '✗'} {label}（{fname}）风险分 {s} ≤ {limit}")
        if not ok:
            failures.append(f"优秀文本误伤：{label} {s} > {limit}")

    print("\n== 7b. 外部真实文本不误伤 ==")
    ext_dir = SAMPLES / "external"
    ext_files = sorted(ext_dir.glob("*.md")) if ext_dir.exists() else []
    ext_files = [p for p in ext_files if p.name != "README.md"]
    if not ext_files:
        failures.append("缺少外部样本 samples/external/*.md")
    tuning_external = {"gaokao-beijing-2020-shuo-weiji.md", "report-vocational-school-2024.md", "article-shmeea-essay-review.md"}
    tuning_files = [p for p in ext_files if p.name in tuning_external]
    holdout_files = [p for p in ext_files if p.name not in tuning_external]
    print(f"  调参集：{len(tuning_files)} 篇；回归集：{len(holdout_files)} 篇（只做回归，不作为对外误报率）")
    false_positives = 0
    for path in holdout_files:
        genre = external_genre(path.name)
        s = score_genre(path.read_text(encoding="utf-8"), genre)
        ok = s <= 15
        if not ok:
            false_positives += 1
        print(f"  {'✓' if ok else '✗'} {path.name}（{genre}）：风险分 {s} ≤ 15")
        if not ok:
            failures.append(f"外部真实文本误伤：{path.name} {s} > 15")
    if ext_files:
        print(f"  回归集通过：{false_positives}/{len(holdout_files)} 误报")

    print("\n== 7c. 真留出集（冻结后一次性评估） ==")
    hold_dir = SAMPLES / "external-holdout"
    hold_files = sorted(hold_dir.glob("*.md")) if hold_dir.exists() else []
    hold_files = [p for p in hold_files if p.name != "README.md"]
    if not hold_files:
        failures.append("缺少真留出集 samples/external-holdout/*.md")
    hold_fp = 0
    for path in hold_files:
        genre = external_genre(path.name)
        s = score_genre(path.read_text(encoding="utf-8"), genre)
        ok = s <= 15
        if not ok:
            hold_fp += 1
        print(f"  {'✓' if ok else '✗'} {path.name}（{genre}）：风险分 {s} ≤ 15")
        if not ok:
            failures.append(f"真留出集误报：{path.name} {s} > 15（不要为它调参，下一版换新留出集）")
    if hold_files:
        print(f"  真留出集误报率：{hold_fp}/{len(hold_files)}（一次性，不用于调参）")

    print("\n== 8. 公文 / 官方文体模式 ==")
    notice_text = (SAMPLES / "08-official-notice.md").read_text(encoding="utf-8")
    nm = collect_metrics(clean_text(notice_text), genre="notice")
    ok = nm["AI味风险分"] <= 10 and bool(nm.get("公文格式要素"))
    print(f"  {'✓' if ok else '✗'} 规范通知 notice 模式：风险分 {nm['AI味风险分']}，"
          f"识别公文格式 {nm.get('公文格式要素')}")
    if not ok:
        failures.append("notice 模式：规范通知未识别为公文格式或仍被扣分")

    officialese = (
        "各科室：\n为深入贯彻落实上级精神，为进一步加强管理，为切实保障安全，"
        "现将有关事项通知如下：\n"
        "一、高度重视，提高认识。二、认真落实，全面排查。三、加强领导，压实责任。"
        "确保取得实效。\n感谢大家的理解与支持。\n"
    )
    om = collect_metrics(clean_text(officialese), genre="notice")
    ok2 = om["AI味风险分"] >= 30 and any("空转" in k for k in om["扣分"])
    print(f"  {'✓' if ok2 else '✗'} 官腔通知不再漏检：风险分 {om['AI味风险分']}")
    if not ok2:
        failures.append(f"notice 模式：官腔通知漏检（{om['AI味风险分']} 分）")

    gov_text = (
        "中国的发展不是凌空蹈虚，而是长在产业里、生态里、场景里。"
        "我们坚持守正创新，因地制宜发展新质生产力，推动高质量发展。"
    )
    written_score = collect_metrics(clean_text(gov_text), genre="written")["AI味风险分"]
    gov_score = collect_metrics(clean_text(gov_text), genre="gov")["AI味风险分"]
    ok3 = gov_score < written_score and gov_score <= 5
    print(f"  {'✓' if ok3 else '✗'} 官方文体保护：书面模式 {written_score} → gov 模式 {gov_score}")
    if not ok3:
        failures.append(f"gov 模式：官方对举仍被扣分（{written_score} → {gov_score}）")

    print("\n== 9. 第二层审稿资产 ==")
    rl_path = ROOT / "references" / "review-layers.md"
    rl_text = rl_path.read_text(encoding="utf-8") if rl_path.exists() else ""
    ok = (
        rl_path.exists()
        and "L2 逻辑层" in rl_text
        and "卡 A｜真实感" in rl_text
        and "卡 B｜文笔与完成度" in rl_text
        and "卡 C｜议论类" in rl_text
        and "适用范围" in rl_text
        and "过度纠偏" in rl_text
    )
    print(f"  {'✓' if ok else '✗'} review-layers.md 存在且含叙事四层 + A/B/C 卡 + 适用范围 + 过度纠偏")
    if not ok:
        failures.append("review-layers.md 缺失或结构不完整")

    official_path = ROOT / "references" / "official-style.md"
    official_text = official_path.read_text(encoding="utf-8") if official_path.exists() else ""
    ok_off = (
        official_path.exists()
        and "四测试" in official_text
        and "A 类：必须保留" in official_text
        and "发布形态三档" in official_text
    )
    print(f"  {'✓' if ok_off else '✗'} reference/official-style.md 存在（四测试 + A 类惯例 + 发布形态三档）")
    if not ok_off:
        failures.append("official-style.md 缺失或结构不完整")

    hard_annotated = ROOT / "samples" / "hard-cases" / "01-ai-but-clean.md"
    hard_raw = ROOT / "samples" / "hard-cases" / "01-ai-but-clean.raw.md"
    hor = hard_annotated.read_text(encoding="utf-8") if hard_annotated.exists() else ""
    ok2 = hard_annotated.exists() and hard_raw.exists() and "卡 A 3 / 20" in hor and "卡 B 4 / 10" in hor
    print(f"  {'✓' if ok2 else '✗'} 坏样本原件 + 批注（卡 A 3/20、卡 B 4/10）")
    if not ok2:
        failures.append("坏样本文件缺失或批注不完整")

    if hard_raw.exists():
        hm = collect_metrics(clean_text(hard_raw.read_text(encoding="utf-8")), genre="essay")
        hint_keys = set(hm.get("人工复核项", {}))
        need = {"作文腔意象", "人物格言句", "无阻力", "过度洁净"}
        ok3 = hm["AI味风险分"] <= 10 and need <= hint_keys and hm.get("加分抵扣", 0) <= 4
        print(f"  {'✓' if ok3 else '✗'} 坏样本 lint：风险分 {hm['AI味风险分']}，"
              f"提示 {sorted(hint_keys - {'段首疑似零回指'})}，加分抵扣 {hm.get('加分抵扣', 0)} ≤ 4")
        if not ok3:
            failures.append("坏样本未触发第二层提示，或 lint 仍在用大额加分掩盖风险")
    else:
        failures.append("缺少坏样本原文 01-ai-but-clean.raw.md")

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    ok_skill = ("上限不是任务" in skill_text and "09-演讲稿" in skill_text
                and "金句" in skill_text)
    print(f"  {'✓' if ok_skill else '✗'} SKILL 明确「金句上限不是任务」并接入演讲稿档案")
    if not ok_skill:
        failures.append("SKILL 金句配额语义或演讲稿路由缺失")

    review_extract = ROOT / "scripts" / "review_extract.py"
    okx = review_extract.exists() and "第二层审稿的素材提取器" in review_extract.read_text(encoding="utf-8")
    print(f"  {'✓' if okx else '✗'} review_extract.py 存在（审稿素材提取器）")
    if not okx:
        failures.append("review_extract.py 缺失或说明不完整")

    good_sample = SAMPLES / "09-essay-zhineng.md"
    if good_sample.exists():
        gm = collect_metrics(clean_text(good_sample.read_text(encoding="utf-8")), genre="essay")
        extra = [k for k in gm.get("人工复核项", {}) if k != "段首疑似零回指"]
        okg = gm["AI味风险分"] <= 10 and not extra
        print(f"  {'✓' if okg else '✗'} 正样本 09-essay-zhineng.md：风险分 {gm['AI味风险分']}，"
              f"第二层提示 {extra if extra else '无'}")
        if not okg:
            failures.append("正样本 09-essay-zhineng.md 被误伤或仍有第二层提示")
    else:
        failures.append("缺少正样本 09-essay-zhineng.md")

    print("\n== 结果 ==")
    if failures:
        print("  ✗ 自检失败：")
        for f in failures:
            print(f"    - {f}")
        return 1
    print(f"  ✓ 全部通过（案例降分 {improved}/{len(pairs)}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
