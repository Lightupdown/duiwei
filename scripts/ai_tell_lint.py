#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai_tell_lint.py — 中文文本「AI 味」体检脚本（v0.8，零依赖）

只查表面特征：词表命中、防御性句式、句长/段长分布、口语标记密度、标点规整度。
第二层提示（作文腔意象 / 人物格言句 / 无阻力 / 过度洁净）只进人工复核、不扣分；完整审稿见 references/review-layers.md。
分数仅供参考；脚本 0 分不代表过关。

用法：
    python3 ai_tell_lint.py 文本.md
    python3 ai_tell_lint.py a.md b.md          # 多文件对比（改写前后）
    python3 ai_tell_lint.py --json 文本.md
    python3 ai_tell_lint.py --genre spoken 口播稿.md
    python3 ai_tell_lint.py --fail-over 60 文本.md     # 分数 >= 60 时返回退出码 1

文体：auto / spoken / written / chat / essay / article / notice / report / copy / gov
    其中 essay=作文、article=文章、notice=通知公告、report=报告总结、copy=产品文案、gov=政务官方。
词表来源：references/ai-tells-cn.md，改词表请同步改那边。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 词表与正则
# ---------------------------------------------------------------------------

VOCAB_CATEGORIES = {
    "收条式应答": {
        "weight": 8.0,
        "cap": 24.0,
        "items": [
            "这点我认", "这点我同意", "你说得对", "你说得有道理", "这句我先收下",
            "我看到了", "我明白了", "懂了", "收到", "有道理", "我同意",
        ],
    },
    "人设/网感标签词": {
        "weight": 3.0,
        "cap": 12.0,
        "items": [
            "我熟", "先欠着", "都归我管", "这招挺", "这波不亏", "绷不住了",
            "笑死", "绝了", "拿捏", "省流", "有一说一", "不是哥们",
            "给本小姐", "记我账上",
        ],
    },
    "通用连接/评价词": {
        "weight": 2.0,
        "cap": 12.0,
        "items": [
            "其实", "说实话", "说白了", "讲真", "老实说", "不可否认",
            "某种程度上", "从某种意义上说", "值得注意的是", "需要指出的是",
            "归根结底", "总而言之", "与此同时", "然而", "此外", "综上",
            "需要提到的是", "客观来讲", "因此", "从而", "进而",
        ],
    },
    "职场黑话/万能升华": {
        "weight": 2.5,
        "cap": 10.0,
        "items": [
            "赋能", "抓手", "闭环", "颗粒度", "底层逻辑", "顶层设计", "组合拳",
            "护城河", "生态位", "长期主义", "复利", "认知升级", "情绪价值",
            "松弛感", "内核稳定",
        ],
    },
    "报告/总结套话": {
        "weight": 2.5,
        "cap": 18.0,
        "items": [
            "在公司的正确领导下", "正确领导下", "大力支持下", "围绕年度工作目标",
            "扎实推进", "显著成效", "有效提升", "显著增强", "再上新台阶",
            "持续发力", "久久为功", "再创佳绩", "有待加强", "仍需提升",
            "精细化管理", "创新意识", "全面提升", "持续优化", "紧紧围绕",
        ],
    },
    "拟人喻体/意义拔高": {
        "weight": 3.0,
        "cap": 10.0,
        "items": [
            "像一位", "宛如", "仿佛", "不知疲倦", "无声地", "默默地", "诉说着",
            "教会我们", "告诉我们", "守护着", "陪伴着", "轻声说", "像在诉",
        ],
    },
    "客服礼仪腔": {
        "weight": 6.0,
        "cap": 20.0,
        "items": [
            "希望对你有帮助", "希望对大家有帮助", "希望今天的分享",
            "对你有所启发", "如有问题随时", "有问题随时找我", "感谢你的分享",
            "很高兴为你解答", "你的反馈很重要", "祝你生活愉快",
            "欢迎在评论区留言", "点赞关注",
            "感谢您的", "感谢您对", "非常感谢", "欢迎随时", "如有其他",
            "如有疑问", "欢迎咨询", "您的反馈", "我们会认真", "尽快改进",
            "期待您的", "期待你的回复", "祝你们玩得开心", "祝您生活愉快",
            "请家长提醒", "配合学校工作", "理解与支持", "关于你提到的问题",
        ],
    },
    "营销/时代套话": {
        "weight": 2.5,
        "cap": 12.0,
        "items": [
            "在当今", "快速变化", "随着时代", "在正式开始之前", "接下来我会",
            "从三个方面", "全新的认识", "尤为重要", "至关重要",
            "不可或缺", "理想之选", "值得拥有", "品质之选", "多种场景", "任何场合",
            "有效锁住", "有效提升", "显著提升", "大幅提升", "深受", "好评",
            "名额有限", "立即报名", "资深讲师", "完整知识体系", "系统提升",
            "职业突破", "打造", "助力", "之旅", "旨在", "增进", "丰富多彩",
            "简约", "满足您的", "满足你的", "欢迎各位", "踊跃参加", "活动内容丰富",
        ],
    },
    "研究腔/借权威": {
        "weight": 4.0,
        "cap": 12.0,
        "items": [
            "研究表明", "数据显示", "专家指出", "众所周知", "据统计",
            "事实证明", "研究发现", "调查显示", "业内人士",
        ],
    },
    "空泛评价/鸡汤": {
        "weight": 3.0,
        "cap": 10.0,
        "items": [
            "感触颇深", "内心充满", "温柔以待", "心灵的陪伴", "知识的传递",
            "愿每一个", "充满感恩", "点点滴滴",
        ],
    },
}

REGEX_PATTERNS = [
    {
        "name": "防御性句式（不是X而是Y）",
        "weight": 10.0,
        "cap": 25.0,
        "pattern": re.compile(r"(?:不是|并非|而不是)[^。！？!?\n]{0,25}?(?:而是|是[^。！？!?\n]{0,15})"),
    },
    {
        "name": "防御性句式（与其说/表面上/看起来）",
        "weight": 8.0,
        "cap": 16.0,
        "pattern": re.compile(r"(?:与其说|表面上是|看起来[^。！？\n]{0,10}?其实|我这么说不是)"),
    },
    {
        "name": "说明文骨架（首先/其次/第一第二）",
        "weight": 4.0,
        "cap": 12.0,
        "pattern": re.compile(r"(?:首先|其次|再次|最后)[，、,：:]|第[一二三四五](?:个原因|个方面|点|条|部分)[，、,：:]?"),
    },
    {
        "name": "总分总结（综上/总之/总的来说）",
        "weight": 5.0,
        "cap": 10.0,
        "pattern": re.compile(r"(?:综上|总之|总的来说|总结一下|一句话总结)"),
    },
    {
        "name": "引列表冒号（主要包括/具体如下）",
        "weight": 8.0,
        "cap": 16.0,
        "pattern": re.compile(r"(?:主要包括|主要有|具体如下|具体包括|主要分为)[：:]"),
    },
    {
        "name": "提示式冒号（核心是/说白了）",
        "weight": 5.0,
        "cap": 12.0,
        "pattern": re.compile(r"(?:核心是|关键是|答案是|说白了|本质是|重点是)[：:]"),
    },
    {
        "name": "译文句式（当…时/对于…来说/这意味着）",
        "weight": 4.0,
        "cap": 12.0,
        "pattern": re.compile(r"(?:当[^。！？!?\n]{0,25}时[，,]|对于[^。！？!?\n]{0,15}来说|这意味着)"),
    },
    {
        "name": "书面腔/翻译腔（进行+动词/随着…发展/被…所）",
        "weight": 3.0,
        "cap": 9.0,
        "pattern": re.compile(
            r"进行(?:了)?[^。！？!?\n]{0,6}(?:工作|研究|分析|处理|优化|管理|检查|调整|改革|建设|推广|应用)"
            r"|随着[^。！？!?\n]{0,20}(?:发展|进步|变化)"
            r"|被[^。！？!?\n]{0,10}所[^。！？!?\n]{0,10}"
        ),
    },
    {
        "name": "递进套式（不仅…更…）",
        "weight": 4.0,
        "cap": 10.0,
        "pattern": re.compile(r"不仅[^。！？!?\n]{0,15}更(?:是)?[^。！？!?\n]{0,15}"),
    },
    {
        "name": "序数词小标题（第一步/第二步）",
        "weight": 2.0,
        "cap": 6.0,
        "pattern": re.compile(r"第[一二三四五六七八九十]+步[，、,：:]?"),
    },
    {
        "name": "名言撑场（正如古人所言/俗话说）",
        "weight": 3.0,
        "cap": 9.0,
        "pattern": re.compile(r"(?:正如古人所言|古人云|俗话说|常言道|有位名人说过|正如那句话所说)"),
    },
    {
        "name": "四字格堆砌（常见套话成语）",
        "weight": 3.0,
        "cap": 8.0,
        "pattern": re.compile(
            r"与时俱进|开拓创新|砥砺前行|不负韶华|持之以恒|常抓不懈|真抓实干|"
            r"奋楫笃行|凝心聚力|守正创新|行稳致远|赓续|笃行不怠|只争朝夕|"
            r"久久为功|驰而不息|抓铁有痕|踏石留印|继往开来|携手共进"
        ),
    },
    {
        "name": "时代腔开场（在这个…的时代）",
        "weight": 4.0,
        "cap": 8.0,
        "pattern": re.compile(r"(?:在这个|在当今|身处)[^。！？!?\n]{0,14}(?:时代|社会)"),
    },
    {
        "name": "升华套式（是一种…更是一种/让我们）",
        "weight": 3.0,
        "cap": 8.0,
        "pattern": re.compile(r"是一种[^。！？!?\n]{0,12}更是一种|让我们[^。！？!?\n]{0,20}"),
    },
    {
        "name": "对举套式（看似…却…）",
        "weight": 3.0,
        "cap": 6.0,
        "pattern": re.compile(r"看似[^。！？!?\n]{0,15}却[^。！？!?\n]{0,15}"),
    },
    {
        "name": "空转目的状语堆叠（为…为…为…）",
        "weight": 6.0,
        "cap": 12.0,
        "pattern": re.compile(r"为[^。！？!?\n]{0,18}[，,]为[^。！？!?\n]{0,18}[，,]为"),
    },
    {
        "name": "空转表态（高度重视/认真落实/确保实效）",
        "weight": 4.0,
        "cap": 12.0,
        "pattern": re.compile(
            r"高度重视|认真落实|切实加强|切实抓好|确保取得实效|狠抓落实|压实责任|形成合力"
        ),
    },
    {
        "name": "程序化表态（立即响应/举一反三）",
        "weight": 3.0,
        "cap": 9.0,
        "pattern": re.compile(r"立即响应|举一反三|迅速行动|第一时间"),
    },
]

# 金句近似：短句 + 强升华词（不用「不是/就是/其实」这类泛词，避免误伤口语）
JINJU_CUES = ["说到底", "这大概就是", "成年人的", "你会发现", "本质", "无非", "真正的", "重要的是", "关键是"]

# 段首零回指的人工提示词（lieflat 语料 R=4.4；正则不可靠，只提示不扣分）
ZERO_ANAPHORA_OPENERS = [
    "说实话", "说白了", "其实", "确实", "真的", "很难", "挺好", "值得",
    "关键是", "重要的是", "本质上", "不得不说", "最需要", "最容易",
]

# 第二层审稿提示（只进人工复核，不扣分；见 references/review-layers.md）
IMAGERY_WORDS = ["阳光", "月光", "微风", "时光", "岁月", "背影", "灯火", "亮痕", "余晖", "晚风", "炊烟", "雨丝"]
APHORISM_PATTERNS = [
    "哪有不", "一辈子", "总会", "总要", "说到底", "才算", "才叫",
    "没有不", "别用蛮力", "找那个", "那个劲",
]
RESISTANCE_WORDS = [
    "没成", "不行", "白跑", "返工", "贵了", "没谈成", "失败", "不肯", "犹豫",
    "拒绝", "打不开", "没修好", "吵", "争执", "还价", "退钱", "算了",
    "听岔", "听不懂", "没反应", "不碰", "费那个钱", "没再说话",
    "延期", "超支", "变更", "离职", "缺口", "投诉", "事故", "故障",
]

# 文体别名：作文 / 通知 / 文章 / 文案都按「书面」计分，只是标签不同
GENRE_ALIASES = {"essay": "written", "notice": "written", "article": "written", "copy": "written", "gov": "written", "report": "written"}
GENRE_LABELS = {
    "auto": "自动", "spoken": "口播", "written": "书面", "chat": "聊天",
    "essay": "作文", "notice": "通知", "article": "文章", "copy": "文案", "gov": "政务/官方", "report": "报告",
}

# 文体豁免：这些词在该文体里是正常用法，不按 AI 腔扣分
GENRE_EXEMPTIONS = {
    "essay": {"拟人喻体/意义拔高": {"仿佛", "宛如"},
              "通用连接/评价词": {"因此", "然而", "此外", "从而", "进而"}},
    "chat": {"收条式应答": {"收到", "懂了", "我明白了"}},
    "article": {"通用连接/评价词": {"因此", "然而", "此外", "从而", "进而"}},
    "notice": {"通用连接/评价词": {"因此", "然而", "此外", "从而", "进而"}},
    "report": {"通用连接/评价词": {"因此", "然而", "此外", "从而", "进而"}},
    "gov": {"通用连接/评价词": {"因此", "然而", "此外", "从而", "进而"}},
}

# 公文/官方格式要素（识别到只提示、不计分；见 research/deep/official-docs.md、gov-tone.md）
OFFICIAL_FORMAT_PATTERNS = {
    "标题文种": re.compile(r"^关于[^。\n]{0,40}的(?:通知|公告|通告|通报|请示|报告|函)\s*$", re.M),
    "发文字号": re.compile(r"[〔\[][12]\d{3}[〕\]]\d+号"),
    "主送机关": re.compile(r"^[^\n。，]{2,20}[：:]\s*$", re.M),
    "成文日期": re.compile(r"20\d{2}年\d{1,2}月\d{1,2}日"),
    "文种结语": re.compile(r"特此通知|特此公告|特此报告|此复|妥否，请批示|以上通知，请|现将有关事项通知如下"),
}
# 官方文体下不计分、只提示的规则（句法无法区分合法对举与 AI 防御句式）
OFFICIAL_MANUAL_RULES = {
    "gov": ("防御性句式", "四字格"),
    "notice": ("说明文骨架", "书面腔"),
}

# 口语标记（语气词 + 口头禅）
ORAL_TOKENS = ["啊", "呢", "吧", "嘛", "哈", "呀", "哦", "诶", "哎", "唉", "嗯", "呃", "啦", "呗", "咯"]
ORAL_PHRASES = ["就是说", "反正", "你看", "你想", "你说", "我跟你讲", "咋", "啥"]

# 具体性信号（数字、引号、时间词）
NUMBER_RE = re.compile(r"\d+")
CN_NUM_RE = re.compile(
    r"[一二三四五六七八九十百千万两几]+(?:分钟|小时|天|周|个月|年|岁|个|节|道|页|块|米|次|遍|版|点|步|句|篇)"
)
QUOTE_RE = re.compile(r"[「『“\"][^」』”\"]{1,40}[」』”\"]")
TIME_WORDS = ["周", "月", "点", "分钟", "小时", "昨天", "今天", "上周", "下周", "年底", "早上", "晚上", "当时", "以前", "后来"]


# ---------------------------------------------------------------------------
# 文本处理
# ---------------------------------------------------------------------------

def read_text(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def clean_text(raw: str) -> str:
    """去掉 frontmatter、代码块、markdown 标记，保留正文。"""
    text = raw
    # frontmatter
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
    # code fences
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    # 标题行整体丢弃（含「标题：」这种手写标题）
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if re.match(r"^标题[：:]", stripped):
            continue
        lines.append(line)
    text = "\n".join(lines)
    # markdown 强调、链接、图片
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_>`|]", "", text)
    return text.replace("\r\n", "\n")


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def split_sentences(text: str) -> list[str]:
    chunks = re.findall(r"[^。！？!?…\n]+[。！？!?…]*", text)
    result = []
    for chunk in chunks:
        s = chunk.strip()
        if cjk_count(s) >= 2:
            result.append(s)
    return result


def split_paragraphs(text: str) -> list[str]:
    paras = re.split(r"\n\s*\n", text)
    result = []
    for para in paras:
        p = para.strip()
        if cjk_count(p) >= 8:
            result.append(p)
    return result


def count_phrase(text: str, phrase: str) -> int:
    return text.count(phrase)


def context_of(text: str, phrase: str, width: int = 12) -> str:
    idx = text.find(phrase)
    if idx < 0:
        return phrase
    start = max(0, idx - width)
    end = min(len(text), idx + len(phrase) + width)
    snippet = text[start:end].replace("\n", " ")
    return ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")


# ---------------------------------------------------------------------------
# 统计
# ---------------------------------------------------------------------------

def cv(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = statistics.mean(values)
    if mean == 0:
        return None
    return statistics.pstdev(values) / mean


def collect_metrics(text: str, genre: str = "auto") -> dict:
    requested_genre = genre
    genre = GENRE_ALIASES.get(genre, genre)
    is_notice = requested_genre == "notice"
    is_gov = requested_genre == "gov"
    protected_mode = is_notice or is_gov
    chars = cjk_count(text)
    kchars = max(chars / 1000.0, 0.001)
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)

    sent_lens = [cjk_count(s) for s in sentences]
    para_lens = [cjk_count(p) for p in paragraphs]

    metrics: dict = {
        "字数": chars,
        "句数": len(sentences),
        "段数": len(paragraphs),
        "平均句长": round(statistics.mean(sent_lens), 1) if sent_lens else 0,
        "句长CV": round(cv(sent_lens) or 0, 3) if len(sent_lens) >= 2 else None,
        "段长CV": round(cv(para_lens) or 0, 3) if len(para_lens) >= 2 else None,
        "命中": [],
        "扣分": {},
    }

    # 词表
    vocab_hits: list[dict] = []
    exempt_map = GENRE_EXEMPTIONS.get(requested_genre, {})
    for category, spec in VOCAB_CATEGORIES.items():
        exempt = exempt_map.get(category, set())
        counted = []
        for item in spec["items"]:
            if item in exempt:
                continue
            n = count_phrase(text, item)
            if n:
                counted.append({"词": item, "次数": n, "例句": context_of(text, item)})
        if counted:
            total = sum(c["次数"] for c in counted)
            density = total / kchars
            penalty = min(spec["cap"], density * spec["weight"])
            if is_gov and category == "营销/时代套话":
                penalty *= 0.5
            if is_gov and category == "职场黑话/万能升华":
                # 官方语境里「赋能/组合拳/抓手」常有具体政策所指，改为人工判断
                penalty = 0.0
            vocab_hits.append({
                "类别": category,
                "总次数": total,
                "每千字": round(density, 2),
                "扣分": round(penalty, 1),
                "明细": counted,
            })
            if penalty:
                metrics["扣分"][category] = round(penalty, 1)

    # 正则句式
    pattern_hits: list[dict] = []
    official_manual: list[str] = []
    manual_rules = OFFICIAL_MANUAL_RULES.get(requested_genre, ())
    for spec in REGEX_PATTERNS:
        matches = [m.group(0) for m in spec["pattern"].finditer(text)]
        if not matches:
            continue
        density = len(matches) / kchars
        penalty = min(spec["cap"], density * spec["weight"])
        if any(rule in spec["name"] for rule in manual_rules):
            # 官方文体：合法对举 / 格式性序数等不自动扣分，转人工复核
            official_manual.append(spec["name"])
            penalty = 0.0
        pattern_hits.append({
            "类别": spec["name"],
            "总次数": len(matches),
            "每千字": round(density, 2),
            "扣分": round(penalty, 1),
            "明细": matches[:5],
        })
        if penalty:
            metrics["扣分"][spec["name"]] = round(penalty, 1)

    # 公文 / 官方格式要素：识别出来只提示，不进扣分
    official_hits = [name for name, pat in OFFICIAL_FORMAT_PATTERNS.items() if pat.search(text)]
    if official_hits:
        metrics["公文格式要素"] = official_hits
    if official_manual:
        metrics["人工复核（官方文体）"] = sorted(set(official_manual))
    metrics["官方文体模式"] = requested_genre if protected_mode else None

    # 金句近似
    jinju = []
    for s in sentences:
        n = cjk_count(s)
        if 8 <= n <= 28 and s.count("，") <= 1 and any(cue in s for cue in JINJU_CUES):
            jinju.append(s)
    if jinju:
        jdensity = len(jinju) / kchars
        penalty = min(8.0, jdensity * 2.0)
        if is_gov:
            # 政论金句密度可到 2–3 句/千字，改为人工判断（见 gov-tone.md）
            penalty = 0.0
        if penalty:
            metrics["扣分"]["金句近似"] = round(penalty, 1)
        metrics["金句近似"] = {
            "总次数": len(jinju),
            "每千字": round(jdensity, 2),
            "明细": jinju[:5],
        }

    # 人工复核项：段首零回指（只提示，不扣分）
    zero_anaphora = []
    for para in paragraphs:
        ps = split_sentences(para)
        if not ps:
            continue
        first = ps[0]
        if 3 <= cjk_count(first) <= 16 and any(first.startswith(w) for w in ZERO_ANAPHORA_OPENERS):
            if not any(p in first for p in ("这", "那", "它", "他", "她", "我", "你")):
                zero_anaphora.append(first)
    metrics["人工复核项"] = {"段首疑似零回指": zero_anaphora[:5]}

    # 第二层人工提示（只提示，不扣分；见 references/review-layers.md）

    # 1) 作文腔意象（作文 / 自动模式，出现 2 个以上才提示）
    imagery = [w for w in IMAGERY_WORDS if w in text]
    if requested_genre in ("essay", "auto") and len(imagery) >= 2:
        metrics["人工复核项"]["作文腔意象"] = imagery[:6]

    # 2) 人物格言句（引号里短而像道理的话，或「说，……」后的短句）
    aphorisms = []
    for m in re.finditer(r"[「“\"]([^」”\"]{4,30})[」”\"]", text):
        s = m.group(1).strip()
        if 6 <= cjk_count(s) <= 20 and any(p in s for p in APHORISM_PATTERNS):
            aphorisms.append(s)
    for m in re.finditer(r"(?:说|问|答|道|喊|念叨)[，,：:]\s*([^。！？!?\n]{2,24})[。！？!?]", text):
        s = m.group(1).strip()
        if 6 <= cjk_count(s) <= 22 and any(p in s for p in APHORISM_PATTERNS):
            aphorisms.append(s)
    if aphorisms:
        metrics["人工复核项"]["人物格言句"] = list(dict.fromkeys(aphorisms))[:5]

    # 3) 无阻力（足够长的文本里没有失败 / 还价 / 怀疑 / 返工）
    if chars >= 150 and not any(w in text for w in RESISTANCE_WORDS):
        metrics["人工复核项"]["无阻力"] = "全篇没有失败 / 还价 / 怀疑 / 返工，事件可能太顺"

    # 4) 过度洁净（标点过于规整，长文本才提示）
    if requested_genre in ("essay", "article", "auto") and chars >= 150:
        clean = (
            text.count("——") == 0
            and text.count("……") == 0
            and "！" not in text and "!" not in text
            and (text.count("？") + text.count("?")) <= 1
        )
        if clean:
            metrics["人工复核项"]["过度洁净"] = "无破折号 / 省略号 / 感叹号、问号≤1，可能过于均匀"

    # 口语标记密度
    oral = sum(count_phrase(text, tok) for tok in ORAL_TOKENS)
    oral += sum(count_phrase(text, ph) for ph in ORAL_PHRASES)
    oral_density = oral / chars * 100 if chars else 0
    metrics["口语标记密度（每百字）"] = round(oral_density, 2)

    # 具体性
    numbers = len(NUMBER_RE.findall(text)) + len(CN_NUM_RE.findall(text))
    quotes = len(QUOTE_RE.findall(text))
    time_marks = sum(count_phrase(text, w) for w in TIME_WORDS)
    concrete = numbers + quotes + time_marks
    metrics["具体性信号"] = {"数字": numbers, "引号": quotes}
    metrics["具体时间词"] = time_marks

    # 标点
    dashes = text.count("——") + text.count("—")
    semicolons = text.count("；")
    punctuation_density = (dashes + semicolons) / kchars
    metrics["破折号分号密度（每千字）"] = round(punctuation_density, 2)

    # 顿号并列过密（语料验证 R=1.8，弱信号；公文/官方文体按格式惯例不计分）
    dunhao = text.count("、")
    dunhao_per_sentence = dunhao / max(len(sentences), 1)
    metrics["顿号密度（每句）"] = round(dunhao_per_sentence, 2)
    if dunhao_per_sentence > 3 and chars > 150 and not protected_mode:
        metrics["扣分"]["顿号并列过密"] = 3

    # 问句比例
    asks = sum(1 for s in sentences if s.rstrip().endswith(("？", "?")))
    ask_ratio = asks / len(sentences) if sentences else 0
    metrics["问句比例"] = round(ask_ratio, 2)

    # ---- 计分 ----
    score = sum(metrics["扣分"].values())

    # 句长均匀度（弱信号：lieflat 语料里 R=0.87 未通过验证，所以只给小分）
    # 只对「像散文的文本」计分：句子数 ≥8 且平均句长 ≥14；口播/聊天里短句成排是正常现象。
    # 公文/官方文体版式本就整齐，不计分。
    sent_cv = metrics["句长CV"]
    mean_len = statistics.mean([cjk_count(s) for s in sentences]) if sentences else 0
    if not protected_mode and sent_cv is not None and len(sentences) >= 8 and mean_len >= 14:
        if sent_cv < 0.30:
            score += 5
            metrics["扣分"]["句长过于均匀"] = 5
        elif sent_cv < 0.40:
            score += 3
            metrics["扣分"]["句长偏均匀"] = 3
        elif sent_cv < 0.50:
            score += 2
            metrics["扣分"]["句长略均匀"] = 2

    # 段长均匀度（同为弱信号，且短文本不判；公文/官方文体不计分）
    para_cv = metrics["段长CV"]
    if not protected_mode and para_cv is not None and len(paragraphs) >= 4:
        if para_cv < 0.18:
            score += 3
            metrics["扣分"]["段落过于均匀"] = 3
        elif para_cv < 0.28:
            score += 2
            metrics["扣分"]["段落偏均匀"] = 2

    # 文体判定
    effective_genre = genre
    if genre == "auto":
        effective_genre = "spoken" if oral_density >= 0.5 else "written"
    metrics["判定文体"] = GENRE_LABELS.get(requested_genre) or GENRE_LABELS.get(effective_genre, effective_genre)

    # 口语标记不足（只判口语 / 聊天；书面、作文、通知本来就可以没有口语词）
    if effective_genre in ("spoken", "chat"):
        if oral_density < 0.2:
            score += 6
            metrics["扣分"]["缺少口语标记"] = 6
        elif oral_density < 0.4:
            score += 3
            metrics["扣分"]["口语标记偏少"] = 3

    # 正向抵扣（有具体细节、有问句、有引号）——上限压低，避免 0 分假象
    bonus = 0
    if concrete >= 3:
        bonus += 2
    if quotes >= 1:
        bonus += 1
    if ask_ratio >= 0.12:
        bonus += 1
    if bonus:
        score -= bonus
        metrics["加分抵扣"] = bonus

    score = max(0, min(100, round(score)))
    metrics["AI味风险分"] = score
    metrics["等级"] = grade(score)
    metrics["词表命中"] = vocab_hits
    metrics["句式命中"] = pattern_hits

    return metrics


def grade(score: float) -> str:
    if score <= 20:
        return "自然"
    if score <= 40:
        return "轻微 AI 味"
    if score <= 60:
        return "明显 AI 味"
    if score <= 80:
        return "AI 味重"
    return "AI 味很重"


def suggestions(m: dict) -> list[str]:
    tips = []
    checks = m.get("人工复核项", {})
    extra_checks = [k for k in checks if k != "段首疑似零回指"]
    if m.get("AI味风险分", 100) <= 10 and not extra_checks:
        return ["风险分很低，没有明显 AI 腔。不要为改而改；重点检查事实、具体细节和场景是否够。"]
    cats = m.get("扣分", {})
    if any("防御性" in k for k in cats):
        tips.append("有防御性句式：直接说结论；真需要澄清，先把对方的话引出来再说，不要预防性辩解。")
    if "收条式应答" in cats:
        tips.append("有收条式应答：把「我认/我看到了」换成具体回应、例子或追问。")
    if "客服礼仪腔" in cats:
        tips.append("有客服腔：结尾换成具体动作、问题或画面，别用「希望对你有所帮助」。")
    if "说明文骨架" in cats or "总分总结" in cats:
        tips.append("说明文骨架太明显：删掉「首先/其次/最后」「综上」，改成自然说话顺序。")
    if any(k.startswith("句长") for k in cats):
        tips.append("句长太均匀：刻意制造一长一短，允许 5 字短句和 40 字长句并存。")
    if any(k.startswith("段落") for k in cats):
        tips.append("段落太整齐：让有的段只有一句，有的段四五句，不要每段同构。")
    if "缺少口语标记" in cats or "口语标记偏少" in cats:
        tips.append("口播稿缺气口：加少量语气词（啊/呢/吧/嘛）、停顿和口语词。")
    if "金句近似" in cats:
        tips.append("金句偏多：一部分段落停在事实上，不升华。")
    if any("冒号" in k for k in cats):
        tips.append("冒号列表 / 提示式冒号：冒号前面那句往往只是引出列表，删掉直接说。")
    if any("译文" in k for k in cats):
        tips.append("有翻译腔：当……时 / 对于……来说 / 这意味着，改成口语顺序或直接删。")
    if any("拟人" in k for k in cats):
        tips.append("有拟人喻体或意义拔高：换成具体动作、数字、场景。")
    if any("序数" in k for k in cats):
        tips.append("有一二三式小标题：口播里换成自然说话顺序。")
    if any("名言" in k for k in cats):
        tips.append("有名言撑场：删掉「正如古人所言」，换成你亲眼看到的一个场景。")
    if any("四字格" in k for k in cats):
        tips.append("四字格堆砌：一次最多留一个，其余改成具体动作或大白话。")
    if any("时代腔" in k for k in cats):
        tips.append("有时代腔开场：删掉「在这个……的时代」，直接说具体的人或事。")
    if any("升华套式" in k for k in cats):
        tips.append("有升华套式：别急着「让我们」，停在具体场景或动作上。")
    if any("对举套式" in k for k in cats):
        tips.append("有「看似……却……」套式：直接说反差，不做铺垫。")
    if "顿号并列过密" in cats:
        tips.append("顿号并列过密：拆成短句，别一句话塞五个并列。")
    if any("空转目的" in k for k in cats):
        tips.append("目的状语堆叠：删掉「为…为…为…」，正式公文只留一句依据+目的+过渡语，群消息直接说事。")
    if any("空转表态" in k for k in cats):
        tips.append("空转表态：「高度重视/认真落实/确保实效」换成可检查的动作、时间、责任人。")
    if any("程序化表态" in k for k in cats):
        tips.append("程序化表态：「立即响应/举一反三」要换成已采取的具体措施和进展。")
    if m.get("公文格式要素"):
        tips.append(
            "识别为公文格式：格式要素与文种结语不计入 AI 味。请人工核对文种—结语对应、"
            "发文字号/成文日期/层次序数（见 research/deep/official-docs.md）。"
        )
    if m.get("人工复核（官方文体）"):
        tips.append(
            "官方文体人工复核："
            + "、".join(m["人工复核（官方文体）"])
            + " 不自动扣分，按 research/deep/gov-tone.md 的四测试判断是否保留。"
        )
    if any("书面腔" in k for k in cats):
        tips.append("有书面腔：进行+动词 / 随着…发展 / 被…所，改成动词直接说（做、改、看）。")
    if checks.get("段首疑似零回指"):
        tips.append("有疑似段首零回指：段落开头直接抛评价，补个「这 / 这个 / 他」说清在评价什么。")
    if checks.get("作文腔意象"):
        tips.append(
            "作文腔意象偏多："
            + "、".join(checks["作文腔意象"])
            + "。删到 1 个，换一个有个人印记的细节。"
        )
    if checks.get("人物格言句"):
        tips.append(
            "人物台词格言化："
            + "、".join(checks["人物格言句"])
            + "。改成技术性 / 日常的话，或换成动作。"
        )
    if checks.get("无阻力"):
        tips.append("全篇无阻力：加一次失败、还价、怀疑或返工，事件才像真发生过。")
    if checks.get("过度洁净"):
        tips.append("过度洁净：标点过于规整，可能显得均匀；允许一处破折号、省略号或感叹。")
    if extra_checks:
        tips.append(
            "第二层审稿（脚本查不到）：按 references/review-layers.md 过逻辑 / 工序 / 人物台词 / "
            "细节负载 / 结构，并打 A 卡（真实感）与 B 卡（文笔）。"
        )
    concrete_total = (
        m.get("具体性信号", {}).get("数字", 0)
        + m.get("具体性信号", {}).get("引号", 0)
        + m.get("具体时间词", 0)
    )
    if concrete_total < 3:
        tips.append("缺具体细节：加时间、数字、地点、动作或原话，每 2–3 句至少一个。")
    if not tips:
        tips.append("表面指标没什么问题。再检查：是否每句都太有用、是否从不困惑、是否每段都有结论。")
    return tips


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def fmt_hits(m: dict) -> list[str]:
    lines = []
    for hit in m.get("词表命中", []):
        examples = "、".join(f"{d['词']}×{d['次数']}" for d in hit["明细"][:4])
        ded = f"-{hit['扣分']}" if hit["扣分"] else "（提示，不计分）"
        lines.append(f"  · {hit['类别']}：{hit['总次数']} 次（{examples}）  {ded}")
    for hit in m.get("句式命中", []):
        examples = "；".join(hit["明细"][:3]).replace("\n", " ")
        ded = f"-{hit['扣分']}" if hit["扣分"] else "（提示，不计分）"
        lines.append(f"  · {hit['类别']}：{hit['总次数']} 次（{examples}）  {ded}")
    if "金句近似" in m:
        lines.append(f"  · 金句近似：{m['金句近似']['总次数']} 次  -{m['扣分']['金句近似']}")
    for key, val in m.get("扣分", {}).items():
        if key in ("句长过于均匀", "句长偏均匀", "句长略均匀", "段落过于均匀", "段落偏均匀",
                   "缺少口语标记", "口语标记偏少", "没有任何口语痕迹"):
            lines.append(f"  · {key}  -{val}")
    return lines


def print_report(path: str, m: dict) -> None:
    print(f"\n== 体检：{path} ==")
    print(f"字数 {m['字数']} 字 | 句数 {m['句数']} | 平均句长 {m['平均句长']} | 句长CV {m['句长CV']}")
    print(f"段落 {m['段数']} | 段长CV {m['段长CV']} | 口语标记 {m['口语标记密度（每百字）']}/百字 | 判定文体 {m['判定文体']}")
    print(f"AI 味风险分：{m['AI味风险分']} / 100 —— {m['等级']}")
    if m.get("公文格式要素"):
        print(f"识别为公文格式：{'、'.join(m['公文格式要素'])}（格式要素与文种结语不计入 AI 味）")
        print("  请人工核对：文种—结语对应、发文字号/成文日期/层次序数；惯例见 research/deep/official-docs.md")
    if m.get("人工复核（官方文体）"):
        print(f"官方文体人工复核：{'、'.join(m['人工复核（官方文体）'])}（不自动扣分）")
        print("  按 research/deep/gov-tone.md 第三节「四测试」判断：能对账、挪不动、在结构位、删了会疼才保留")
    if m["字数"] < 150:
        print("  注：字数不足 150，风险分容易被低估，请以命中项为主。")
    hits = fmt_hits(m)
    if hits:
        print("主要命中：")
        print("\n".join(hits))
    checks = m.get("人工复核项", {}).get("段首疑似零回指") or []
    if checks:
        print("人工复核（不扣分，需人判断）：")
        print("  · 段首疑似零回指：补个「这 / 这个 / 他」，说清在评价什么")
        for s in checks:
            print(f"    - {s}")
    manual = m.get("人工复核项", {})
    other_checks = {k: v for k, v in manual.items() if k != "段首疑似零回指"}
    if other_checks:
        print("第二层审稿提示（不扣分，脚本只提示）：")
        labels = {
            "作文腔意象": "作文腔意象",
            "人物格言句": "人物格言句",
            "无阻力": "无阻力",
            "过度洁净": "过度洁净",
        }
        for key, value in other_checks.items():
            print(f"  · {labels.get(key, key)}：{value}")
    print("建议：")
    for tip in suggestions(m):
        print(f"  - {tip}")
    print("提示：脚本只查表面。请按 references/review-layers.md 过第二层（逻辑 / 工序 / 人物 / 细节 / 结构 / 文笔两张卡）。")


def print_compare(rows: list[tuple[str, dict]]) -> None:
    print(f"\n{'文件':<32}{'字数':>6}{'风险分':>8}{'等级':>14}")
    print("-" * 60)
    for path, m in rows:
        print(f"{path:<32}{m['字数']:>6}{m['AI味风险分']:>8}{m['等级']:>14}")


def main() -> int:
    parser = argparse.ArgumentParser(description="中文文本「AI 味」体检")
    parser.add_argument("files", nargs="*", help="待检查文件；留空则读 stdin")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--genre", default="auto",
                        choices=["auto", "spoken", "written", "chat", "essay", "notice", "article", "copy", "gov", "report"],
                        help="文体：auto / spoken / written / chat / essay（作文）/ article（文章）/ notice（通知公告）/ report（报告总结）/ copy（产品文案）/ gov（政务官方）。按对应文体给权重与豁免；gov 下对举与版式均匀只提示不扣分。")
    parser.add_argument("--fail-over", type=float, default=None, help="风险分 >= 该值时返回退出码 1")
    args = parser.parse_args()

    files = args.files or [None]
    results = []
    for path in files:
        raw = read_text(path)
        text = clean_text(raw)
        m = collect_metrics(text, genre=args.genre)
        label = path if path else "<stdin>"
        results.append((label, m))

    if args.json:
        payload = {label: m for label, m in results}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif len(results) > 1:
        print_compare(results)
        for label, m in results:
            print_report(label, m)
    else:
        label, m = results[0]
        print_report(label, m)

    if args.fail_over is not None and any(m["AI味风险分"] >= args.fail_over for _, m in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
