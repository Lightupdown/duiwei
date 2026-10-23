# GitHub「去AI味 / humanizer / anti-slop」竞品调研

> 调研时间：2026-10-19。star / fork 数为当日通过 GitHub API 取的快照。所有仓库都逐个打开 README / SKILL.md / 规则文件核对；打不开或没读到的会在对应条目标注「未核实」。
> 目的只有一个：看别人**具体怎么检测、怎么改、怎么打分、怎么防止改坏**，挑出能塞进我们中文口播/文案 SKILL 的东西。

## TL;DR：五个关键发现

1. **行业标准做法是「检测 → 改写 → 校验 → 报告」四段式**，几乎所有项目都长这样。真正的差异在最后一段：给不给分数、改不改结构、要不要保留作者声音。
2. **大厂英文规则的原型是同一份清单**：Wikipedia 的 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)。blader/humanizer（58.4k★）、op7418/Humanizer-zh（20.1k★）、slopster 的 Tagore、lieflat 的研究都从它出发，所以规则高度同源，抄一份等于抄了全部。
3. **中文这边已经有人做过语料验证，而且推翻了多条流行说法**：lieflat-less-ai-tone 用 283 万字对照语料测了 26 项，只有 11 项成立；「删设问」「删比喻」「删单字虚词」在中文里是反的（人类设问是 AI 的 17 倍，比喻是 2.4 倍）。
4. **所有工具几乎都改不动结构**。awesome-humanizer-skills 在 2026-10-07 实测 26 个 skill（23 个跑通）：19/21 只改措辞不改结构，课文式总结（stated lesson）26/26 存活，圆满结尾 28/28 存活。这是整个赛道的空白，也是我们的难点。
5. **英文词表和标点规则不能直译**。中文破折号密度、弯引号、-ing 尾巴、copula 回避都没有对应物；而中文 AI 腔的大头（段首零回指评论 R=4.4、拟人化喻体 R=7.3、对举 R=3.4、提示式冒号 R=3.8~9.4）需要中文自己的清单。

---

## 一、全景表

| # | 项目 | 链接 | star | 形态 | 核心方法 | License |
|---|---|---|---|---|---|---|
| 1 | blader/humanizer | https://github.com/blader/humanizer | 58,355 | Agent skill | 26 patterns + 4 步流程 + voice 匹配 | MIT |
| 2 | hardikpandya/stop-slop | https://github.com/hardikpandya/stop-slop | 18,143 | Agent skill | 短语/结构禁令 + 5 维评分 | MIT |
| 3 | maxsancheez/humanizer-skill | https://github.com/maxsancheez/humanizer-skill | 0 | skill + Python 检测器 | 三遍法 + stdlib regex | **无** |
| 4 | HafidIdrissi/humanizer | https://github.com/HafidIdrissi/humanizer | 1 | Agent skill | 30+ 英/9 法 patterns + 三遍 + 0–10 分 | MIT |
| 5 | eric-sabe/slop-lint（npm `slop-lint`） | https://github.com/eric-sabe/slop-lint | 2 | CLI | em-dash 硬失败 + ~100 词/~60 句式 + 语料发现 | MIT |
| 6 | t0ddharris/slopster | https://github.com/t0ddharris/slopster | 2 | Vale 规则 + skill + CI | 6 条 Vale YAML + Tagore + slop-diff | MIT |
| 7 | apurvrdx1/tagore（slopster 内置） | https://github.com/apurvrdx1/tagore | 54 | Agent skill | 29 patterns + Orwell 六条 + 8 维 56/80 | MIT |
| 8 | op7418/Humanizer-zh | https://github.com/op7418/Humanizer-zh | 20,071 | 中文 skill | 31 检查点 A–F（含 6 条中文特有） | MIT |
| 9 | taxueseek/say-it-human | https://github.com/taxueseek/say-it-human | 68 | 中文 skill 家族 | 19 维 + 决策树 + 保护区 + 体裁分档 | MIT |
| 10 | masonweb3/de-ai-flavor | https://github.com/masonweb3/de-ai-flavor | 4 | 中文单文件 skill | 8 项加权 100 分体检 + 改写 | MIT |
| 11 | larashero3-dotcom/lieflat-less-ai-tone | https://github.com/larashero3-dotcom/lieflat-less-ai-tone | 3,181 | 研究 + 中文 skill | 283 万字对照语料，11 项验证特征 | MIT |
| 12 | DW-Studio/sloplint | https://github.com/DW-Studio/sloplint | 4 | 中文检测器（网页 + skill） | 16 条带权重/R 值的正则规则 | MIT |
| 13 | Takamatsu-Hikaru/humanize-skill | https://github.com/Takamatsu-Hikaru/humanize-skill | 4 | 中文 skill | 内容/结构两遍检查，不做评分 | MIT |
| 14 | RobinZorro86/humanizer-zh-plus | https://github.com/RobinZorro86/humanizer-zh-plus | 7 | 中文 skill | 33 上游 + 5 中文特有 pattern | MIT |
| 15 | OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL | https://github.com/OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL | 889 | 中文提示词包 | 24 项检测 + 七大铁律 + 量化风格约束 | **未注明** |
| 16 | zhuyansen/awesome-humanizer-skills | https://github.com/zhuyansen/awesome-humanizer-skills | 5 | 索引 + 实测 | 242 个仓库索引，26 个端到端测试 | NOASSERTION |
| 17 | Wikipedia:Signs of AI writing | https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing | — | 资源 | 上游总源头，线索清单 | CC BY-SA |

---

## 二、逐个拆解

### A. 英文 humanizer skill 系

#### A1. blader/humanizer —— 58.4k★，整个赛道的上游

- 链接：https://github.com/blader/humanizer ｜ star 58,355 / fork 4,626 ｜ MIT ｜ SKILL.md v3.1.0，26 个 pattern
- 核心方法：把 Wikipedia 的「AI 写作迹象」整理成**按信号强度排序**的 26 条 pattern，分成 A–F 六组：
  - §1–5 Staging（铺垫代替陈述）：not X but Y、单句收尾/戏剧碎片、伪深度格言、起跑式铺垫、与假想敌辩论
  - §6–11 Rhythm by rule：强凑三段式、重复句首、破折号当万能连接、限定词堆叠、连字符复合词泛滥、被动/缺主语
  - §12–18 Inflation：AI 高频词、意义拔高、模糊关联、-ing 尾巴、销售话术、借权威、回避 is/are
  - §19–21 Formatting：装饰性粗体、装饰性标题、弯引号
  - §22–25 Leftovers：客服腔残留、知识边界免责、标题首句复读、谈论文稿而不是主题
  - §26 Wrong reader：向已经知道背景的人重新解释
- 关键设计（这段值得抄）：**前 5 条「见一次就改」，标了 weak alone 的 pattern 必须「同段凑够多个 tell」才动手**。原文：`The patterns are numbered by strength and frequency... a pattern marked weak alone needs company from other tells in the same passage before you act.`
- 流程（4 步）：① 通读并标记所有 tell（从强到弱，段落尺度也看：跨句的对比、三个并行例子、每节同一句收尾）；② 起草改写（可以合并/拆分段、改结构，但不加事实，缺细节要问不能编）；③ 检查（读出声、追问「哪里还像 AI」、重点复查 §1/§2/§6/§8/§19 这些改写后最易残留的）；④ 出终稿，并返回「草稿 → 残留清单 → 终稿」。
- 摘录几条最硬的规则：
  - §1 not X but Y：「negative half names something no one claimed」——否定一半在说不存在的主张。
  - §8 破折号：终稿不得含 em/en dash（除非作者样本里就用），`-- ` 也算。
  - §12 词表：delve, tapestry, testament, underscore, showcase, meticulous, pivotal, interplay, intricate, vibrant, robust（比喻义）, landscape（抽象义）, key（形容词）…
  - 「When not to act」：引号里、标题里、专有名词里、讨论这个词本身的段落里都不改；2022-11-30 前的文本不可能是 AI 写的；判断靠「多个 tell 一起出现」，不靠单个。
  - 「Keep the details that carry the writer's voice」：具体古怪的细节、混杂情绪、带年代感的梗、第一人称的偏爱、真实的旁白/自我更正 —— 明确列为**要保留**。
- 可借鉴：强度分级 + weak alone 机制（避免单词命中就删）；「保留清单」和「删除清单」同等重要；文件模式/嵌入模式（只改散文，代码、URL、YAML、链接目标不动）；报告格式「草稿 → 残留 → 终稿」。
- 局限（英→中）：大量规则绑定英文语法（curly quotes、Wh- 开头、hyphenated pairs、copula avoidance、-ing riders 的形态）；「delve/tapestry」词表直译成中文没有意义；口播稿里的重复、停顿、口头禅很容易被 §2「单句收尾」和 §4「起跑式铺垫」误伤，需要中文重新标定。
- License：MIT。

#### A2. hardikpandya/stop-slop —— 18.1k★，最像「编辑手册」的一份

- 链接：https://github.com/hardikpandya/stop-slop ｜ star 18,143 / fork 1,339 ｜ MIT
- 结构：`SKILL.md` + `references/phrases.md` + `references/structures.md` + `references/examples.md`
- 核心方法：8 条 core rules（砍填充、破公式结构、主动语态、要具体、把读者放进现场、变节奏、信任读者、砍金句）+ 12 项 quick checks + 5 维 1–10 打分（Directness / Rhythm / Trust / Authenticity / Density，低于 35/50 重改）。
- 规则具体到可以直接抄：
  - phrases.md 分 6 类：throat-clearing openers（"Here's the thing", "The uncomfortable truth is", "Let me be clear"…15 条）、emphasis crutches（"Full stop." "Let that sink in."）、business jargon 替换表（navigate→handle、unpack→explain、lean into→accept、deep dive→analysis…11 组）、**adverbs 全杀**（really/just/literally/genuinely/honestly/simply/actually…）、meta-commentary（"Let me walk you through…"）、vague declaratives（"The implications are significant"→说出具体是什么）。
  - structures.md 列得更细：binary contrasts 10 种句式、negative listing、dramatic fragmentation、rhetorical setups、false agency（「a complaint becomes a fix」→要点名是谁修的）、narrator-from-a-distance、passive voice、Wh- 句首、三连列表、lazy extremes（every/always/never）。
- 可借鉴：**把「结构问题」写成可识别的句式表**，比只给词表有用得多；false agency 那张表全是「AI 爱让无生命的东西做人事」的具体案例，中文口播里同样有（「这个功能解决了焦虑」「数据会说话」）；jargon 替换表可以直接改造成中文对照。
- 局限：极端规则是英文编辑口味。「kill all adverbs」「no passive voice」「no Wh- 开头」直译到中文会伤口语自然度（中文的「其实/就/真的」是节奏不是废话）；整套只管风格，没有事实保真门禁，容易改出事实漂移。
- License：MIT。

#### A3. maxsancheez/humanizer-skill —— 0★，但三遍法+检测器的分工声明值得抄

- 链接：https://github.com/maxsancheez/humanizer-skill ｜ star 0（2026-10-14 新建）｜ **仓库无 LICENSE 文件**（GitHub API `license: null`）
- 核心方法：三遍法 + 一个 stdlib Python 检测器 `code/tells.py`
  - Pass 1 找 tell：把命中逐条**引用原文**，分四组：修辞癖（not just X but Y、here's the thing、turns out、X is dead）、结构癖（连续反问、三句同头、冒号带三项、participle 尾巴、悬空助动词）、词汇填充、残留物（citation markers、utm 参数）。
  - Pass 2 改写：核心规则「almost every tell is a substitute for saying the thing. Cut the framing and state the claim.」；变句长；用朴素词；**不新增事实、数字、例子**；不换一个陈词滥调为另一个；永不用 em dash。
  - Pass 3 报告：干净全文 + 改动表（tell / 原文 / 替换）+ 刻意保留的说明 + 一句诚实的「现在像人吗」，并规定 `If the draft is already clean, say so and change nothing. Do not invent problems to look useful.`
- 检测器实现细节：正则逐条对应 pattern，`structure_tells()` 用句子切分做上下文检测；输出格式是 `== file: 101 words, 18 tells (17.8 per 100 words)` + 每条 `[category] label "phrase"` + by category 统计；**发现 tell 就 exit 非零**，可直接当 pre-publish check。原文注释：`a regex can spot "here's the thing", but it can't say the thing for you`。
- 可借鉴：①「检测器只做 Pass 1、改写交给模型」的分工声明；②按每百字算命中密度（中文可用每百字）；③报告表和「原文干净就别改」；④把检测器做成 exit code 可接 CI（我们以后可以给口播稿做类似的「发布前自检」）。
- 局限：全英文词表 + 英文句子切分（按 `.!?`），中文要重写切分和结构检测；仓库太新，无社区验证；**无 license，不能复制代码/文本，只能借鉴思路**。
- License：无（不可复用）。

#### A4. HafidIdrissi/humanizer —— 1★，「personality pass」值得看

- 链接：https://github.com/HafidIdrissi/humanizer ｜ star 1 ｜ MIT ｜ 默认分支 master（main 分支的 README 404，已换 master 核实）
- 核心方法：30+ 英文 pattern + 9 条法语专属 pattern（说明「规则不能跨语言直译」这件事，作者自己就分了语言库）；三遍：pattern pass → **personality pass** → anti-AI audit；`--score` 给 0–10（越低越像人），5 个维度：Rhythm / Vocabulary / Structure / Hedging / Voice；`--light` 只修最严重的、保留结构；voice matching 收 2–3 段用户写作。
- 法语 pattern 摘录：mots bannis（approfondir/incontournable/synergie）、constructions administratives（dans le cadre de / il convient de）、substantivation excessive（procéder à une analyse→analyser）、intro en entonnoir（dans un monde de plus en plus…）、conclusion circulaire（ainsi nous avons vu que…）、enthousiasme artificiel。
- 可借鉴：**「清完痕迹不等于有人味」**，所以单独设 personality pass，主动注入 2–3 个人味标记（一句短促的话、一个具体细节、一个真实立场、一句旁白）。这跟我们「人话特征库」是一个方向；法语独立库证明「中文/口播也应该有独立规则集」。
- 局限：1 star 个人项目；README 描述的 personality pass 没有素材约束机制，模型容易靠编造细节来「有人味」——必须叠加 blader/op7418 的「不新增事实」门禁；未读其 SKILL.md，内部规则细节**未核实**。
- License：MIT。

### B. 把规则工程化、可检测的项目

#### B1. eric-sabe/slop-lint（npm `slop-lint`）—— 检测器产品化的范本

- 链接：https://github.com/eric-sabe/slop-lint ｜ npm https://www.npmjs.com/package/slop-lint ｜ star 2 ｜ MIT ｜ v0.8.0，单文件零依赖，Node 18+
- 核心方法：**分级检测**。只有 em dash（U+2014）是 hard failure（exit 1），其余 ~100 个焦点词、~60 个句式、回复机器人语体（"That's the distinction." 这类 validate-then-restate 开场、对比机、格言模具）、双连字符、弯引号、emoji 全是 warning。作者原话：`A low false-negative rate matters more than zero false positives.`
- 语料工程（这部分比规则更值钱）：
  - `--discover`：拿模型输出和人类基线比词/二元组频率，找出还没收录的 tell；支持「同题多模型 vs 模型池」的对比，排除话题干扰；
  - `generate-samples.mjs`：固定 prompt 集跑各模型，保证「差异是风格不是题材」；
  - `build-baseline.mjs`：用公共领域文本（美国总统演讲、NIH 科普、Wikinews）搭人类基线；
  - `corpus-stats.mjs`：量标点密度（em dash / 弯引号 / 分号 / 省略号 / 粗体每千字），测出 GPT/Grok 每千字约 9 个弯引号、Claude 0 个；
  - `corpus/specimens/`：人工从真实评论里收句式标本，**要求两次独立目击才上线新规则**（一次目击的进 PENDING.md）。
- 可借鉴：①「只把最可靠的那一条当硬失败，其余都是 review prompt」；②白名单 `--allow`/`.slop-lint.json`；③词表带 `since` + `source` + 版本号，fading tells 主动删；④「发现新 tell 靠测频率，不靠猜」——我们以后做中文口播词表可以照这个流程，用同题生成 vs 人类文案对照。
- 局限：全部英文。中文文本没有弯引号问题（中文用全角引号），破折号是「——」，而且口播稿几乎不用破折号；作者自己也承认 em dash 只是「plain modern typed text」的特征，文学排印文本照样大量用。词表直译无意义。
- License：MIT。补充：npmjs.com 页面本身被 Cloudflare 拦（403），以上信息来自 registry.npmjs.org 的包元数据 + GitHub README，已核实。

#### B2. t0ddharris/slopster + apurvrdx1/tagore —— 「lint + skill + CI」三层组合

- 链接：https://github.com/t0ddharris/slopster ｜ star 2 ｜ MIT ｜ TypeScript；内置 https://github.com/apurvrdx1/tagore (54★, MIT)
- 核心方法：三层
  1. **Vale 规则**（确定性、无需 AI）：6 条 YAML —— `AISlop`（跨句否定转折 regex，如 `"wasn't [^.]+\\. It was"`）、`BannedWords`（40+ 条，含 "Here's the thing"、"Let that sink in"、"In today's fast-paced world"、`'quiet\w*'`、`'sharp\w*'`）、`JargonSwaps`（utilize→use、leverage→use、facilitate→help…25 组）、`WeakWords`、`EmDash`（每篇 >3 个警告）、`Orwell`（陈腐隐喻 + 外来短语）。
  2. **Tagore skill**（深度改写）：29 个 pattern（直接来自 Wikipedia 清单，按 Content 1–6 / Language 7–13 / Style 14–19 / Communication 20–22 / Filler 23–29 分组）+ **Orwell 六条规则作为强制门** + 8 维评分（机制 5 维：Directness/Rhythm/Trust/Authenticity/Density；实质 3 维：Specificity/Restraint/Voice），低于 **56/80** 重改。Stage 4 会自问 `"What makes the below so obviously AI generated?"` 再改一遍。
  3. **slop-diff**：拿分支和 main 比，只报**新增**的 slop，忽略行号漂移。
- 最值得抄的概念（Tagore 的原创）：
  - **clean but soulless**：机制分高、实质分低 → 回 Stage 1b 补人味；**interesting but slop-shaped**：实质分高、机制分低 → 回 Stage 1a 洗句式。
  - **amplifier paragraph**：只把已经说过的意思再换一种对仗/三段式说一遍的段落，用「删掉这段，论证有没有损失」测试；`You cannot cadence-fix filler; polishing it only makes the slop more convincing.`
  - **mic-drop metronome**：连续三段都以短促结论句收尾，就是新的模板（这个能躲过句长变化检测）——测法是把每段最后一句连起来读，三句以上短判断句就是中招。
  - **confiding-insight openers**：「here's the hidden truth / what nobody tells you」是一种**形状**不是固定短语，换词也活着。
- 可借鉴：Tagore 的「机制 vs 实质」二维诊断非常适合口播稿：「一句句都干净但没人味」和「有观点但句式是 AI 模板」是两种病，得吃两种药；amplifier paragraph 删除测试、mic-drop 测试都能直接改成口播版（连续三条视频结尾都是「这才是……的本质」就是 mic-drop 中招）。
- 局限：Vale 和 Orwell 六条都是英文写作规范；29 patterns 里一半是英文语法形态（-ing riders、copula avoidance、hyphenated pairs、curly quotes），中文没有对应；56/80 是拍的经验门槛，没有数据支撑。
- License：MIT。

### C. 中文去AI味 skill 系（重点）

#### C1. op7418/Humanizer-zh —— 20.1k★，中文引用最多的一份

- 链接：https://github.com/op7418/Humanizer-zh ｜ star 20,071 / fork 1,278 ｜ MIT ｜ 基于 blader/humanizer v3.0.0 + PR #39，2026-09-23 重写
- 核心方法：31 个检查点，A–F 分类，每条给「改写前 / 改写后 / **保留**」三件套：
  - A 铺垫代替陈述（1–5）：不是X而是Y、单句收尾与戏剧碎片、格言与伪深度、起跑式铺垫、与假想敌辩论
  - B 公式化节奏（6–11）：强凑三段式、句式开头复读、破折号当万能连接、限定词堆叠、生造复合词、被动与缺主语
  - C 拔高与借权威（12–18）：AI 高频词、意义拔高、模糊关联、句尾补充式拔高、宣传语、借权威、回避「是/有」
  - D 公式化排版（19–21）：粗体当装饰、装饰性标题、引号与中文标点
  - E 聊天与草稿残留（22–25）：客服腔、知识边界免责与猜测填充、首句复读标题、谈论上一稿
  - F 中文补充（26–31）：层叠的「的」、「进行＋动词」、被字句堆叠、四字词排比、「随着……的发展」式开头、套话收尾
- 流程：编辑约束**优先级**（保留信息与确定程度 > 用户范围与文体 > 作者声音 > 具体表达问题）→ 通读定文体 → 只改确实存在的问题 → 对照原文查新增/遗漏/主张强度变化 → 通读语气。默认只交终稿，不附命中清单、不附自评分。
- 摘录它的「保留」示例（这是中文项目里做得最细的）：
  - 「问题被社区多次报告，被认为可能与内存泄漏有关，但原因尚未确认」→ 保留「可能」「尚未确认」，不把推测改成因果；
  - 「这次更新新增导出、搜索和批量重命名」→ 三项都真，就保留三项，不为避开三段式删项；
  - 「先保存文件，再关闭窗口。未保存的修改会丢失。」→ 本来就清楚，不改。
- 可借鉴：①「保留」示例比改写示例更能校准尺度——我们的口播 skill 必须有「这句别动」的例子（结巴、重复、口头禅、方言）；②事实/情态优先级列表可以直接做成硬约束；③F 组 6 条中文特有项可作我们词表的底子；④「不要为了展示工作量强行修改通顺的文字」；⑤中文标点规范（「」/“”）。
- 局限：偏书面编辑（文章、评论、文档），没有口播的气口、停顿、称呼、互动感；F 组 6 条也偏书面（层叠的、进行+动词），口语层缺位；只是检查点不是可执行检测器；不提供分数（和 de-ai-flavor 是两种产品选择）。
- License：MIT。

#### C2. taxueseek/say-it-human —— 68★，跟我们最像的中文竞品

- 链接：https://github.com/taxueseek/say-it-human ｜ star 68 / fork 3 ｜ MIT ｜ 是一套 skill 家族（humanize-ai v1.8.0 + chinese-write-checker + editor-revisor + voice-dissolver + packaging-workshop + punct-master），另有 `references/extended-patterns.md`（19 维详解）、`title-and-opening-patterns.md`（8 种标题公式 + 7 种开头）
- 核心方法（分四层，层级感很强）：
  1. **快速扫描**：数关键词命中（结构胶水、空洞词、模板句、口水话、交流腔）。<5 处只改标记处；≥5 处进全量诊断。
  2. **19 维 AI 味模式 + 3 个根因**：根因是「语气过于中性/权威」「套话与空洞修饰」「翻译腔」——先解根因，能一次消掉多种表现。
  3. **保护区**：先识别人声（口头禅≥3次且非模板、动情处拔高、不完美痕迹），标为不动，**再**逐段改。原话：`不先做这步就逐段改，会把人味当AI味删掉。`
  4. **决策树（留还是删）**：①在保护区？②200 字内出现≥3 次？③换话题还成立？④是两段之间的喘息句？⑤删了会失去温度/锋利/犹豫吗？——五问通过才删。核心原则：**看密度，不看单次出现**。
- 改写目标：「人话三要素」——至少一处真实偏见、一处真实情绪（要具体到瞬间：「我看到这条消息的时候，手停在半空」）、一处真实立场（「我一开始也觉得……后来撞见这事才发现……」）。
- 质量控制：硬指标一票否决（有没有编造原文没有的人物/故事/样本量、对齐度、信息保真、新引入套话）+ 软指标（人称一致、因果真实、节奏、结尾），A/B/C/D 分级，最多 3 轮；输出有完整「诊断报告模板」。
- 体裁表（对我们直接有用）：
  | 体裁 | AI 味敏感度 | 处理原则 |
  |---|---|---|
  | 个人随笔/推文/**短视频文案** | 高 | 允许不完美、允许跑题、允许情绪化 |
  | 公众号/专栏 | 中 | 保留结构感，打破模板化 |
  | 商业报告/学术 | 低 | 规范表达不是 AI 味，别误伤 |
- 误伤警告表（很诚实）：不是X是Y → 800 字内 3 次以上才判；收束金句 → 仅公众号长文判；**短视频文稿金句收束不判定**；推文 → 句子节奏不适用；学术文体 → 堵反驳不判定。
- 可借鉴：决策树直接解决「密度 vs 单次」；保护区机制先于改写；体裁表已经有「短视频文案」档位；「去 AI 味 ≠ 好内容，检测干净就直接说，不要硬找问题」。
- 局限：诊断报告对 30 秒口播稿太重；人话三要素（偏见/情绪/立场）适合观点文，产品口播、通知、活动文案会被逼着「加戏」；19 维仍是经验清单，没做 lieflat 那种对照验证；仓库 topics 标 Python 但主体是 prompt skill，树里只有 archived 的旧脚本，**没有现役检测器**（已核实文件树）。
- License：MIT。

#### C3. masonweb3/de-ai-flavor —— 4★，中文里评分体系最完整

- 链接：https://github.com/masonweb3/de-ai-flavor ｜ star 4 ｜ MIT ｜ 单文件零依赖，无脚本
- 核心方法：**8 项加权 100 分体检**：

  | # | 检查项 | 权重 | 判定标准（摘录） |
  |---|---|---|---|
  | 1 | 框架词 | 15 | 首先/其次/最后/总而言之/综上所述/值得一提的是 |
  | 2 | AI 高频词 | 15 | 赋能/闭环/抓手/颗粒度/底层逻辑/极致/拉满/助力/开启…之旅/不难发现 |
  | 3 | 排比与对仗 | 10 | 连续两处以上排比；小标题强行工整对仗 |
  | 4 | 句长同构 | 10 | 连续三句结构相同；整段长度均匀 |
  | 5 | 情感缺失 | 15 | 全文没有真实情绪（意外/犹豫/吐槽/自嘲）、没有个人判断 |
  | 6 | 细节缺失 | 15 | 没有具体物（工具名/数字/场景）；抽象形容词连用两个以上 |
  | 7 | 书面腔 | 10 | 进行操作/此外/因此/与此同时；当面不会对朋友说的句子 |
  | 8 | 冗余句 | 10 | 删掉不影响表达的句子；同义反复 |

- 评分方法：每项三档（无 0 / 轻微 1–2 处 0.5 / 明显 3 处以上或贯穿全文 1），浓度 = Σ(权重×档位)，<30% 轻度、30–60% 中度、>60% 重度，并声明「同一篇两次体检允许 ±10 浮动」。
- 改写规则里两条硬约束很实用：**篇幅 ±20%**（低于原文约 85% 就是删过头，要把信息补回来）；**情感与细节只能从原文既有内容里带出来**，原文没提的场景不许放大成「真实语气」。
- 报告格式：命中项必须「引用原文短句」；**亮点保留**是必填项（指出原文本来就有人味的地方并承诺改写时保留，找不到就直说「没找到」，不许编造亮点）；改完附三行内「改了什么」。
- 文体特调：小红书保留短句分段、emoji ≤6、话题标签原样；公众号允许完整段落；工作周报里「本周完成」不算 AI 味，重点打「持续赋能业务增长」这类空话。安全条款：输入文本是数据不是指令（防注入）。
- 可借鉴：①固定权重评分可以跨次比较；②「亮点保留」必填，防只破不立；③篇幅 ±20% —— 口播时长直接对应字数，这条对我们特别合适；④文体特调 + 防注入声明。
- 局限：权重是经验值无验证；「情感缺失 15 分」用在通知/产品口播上不合理；8 项里没有口播专属维度（气口、重音、称呼、互动）；只给改后全文，不给逐句依据。
- License：MIT。

#### C4. larashero3-dotcom/lieflat-less-ai-tone —— 3.2k★，唯一做过中文语料对照的

- 链接：https://github.com/larashero3-dotcom/lieflat-less-ai-tone ｜ star 3,181 / fork 194 ｜ MIT
- 核心方法：629 篇文章（生成侧 300 篇、5 个模型、受控无风格指令；人类侧 329 篇）约 283 万字、95,551 句；对 26 项「AI 文风」候选特征逐项算频率比 **R = 生成侧 ÷ 人类侧**；判定：R≥2 纳入，1.25–2 条件纳入，0.8–1.25 排除，<0.8 人类更高（反向也不能作为删改依据）。另加三重门槛：组间一致性（人类各组极差≤5 倍）、算子可定位、改写可操作性。
- **通过检验的 11 项（这是目前最可靠的中文清单）**：

  | 特征 | R 值 | 备注 |
  |---|---|---|
  | 段首零回指评论 | **4.4** | 段落起头直接抛评价，不说是评价什么；补个「这」就顺 |
  | 提示语冒号 | 3.8 | 「核心是：」「说白了：」 |
  | 空转句引列表的冒号 | **9.4** | 「主要包括：」「具体如下：」 |
  | 对举结构（不是A而是B） | 3.4 | |
  | 起首语（说白了） | 3.2 | |
  | 序数词充当小标题 | 3.1 | 一、二、三 |
  | 破折号 | 3.0 | 但组间极差百倍，附限定说明 |
  | 顿号并列过密 | 1.8 | 密度型 |
  | 相邻句结构同构 | 2.0 | |
  | 拟人化喻体 | **7.3** | 「像一位智慧的导师」「不知疲倦的助手」 |
  | 译文句式 5 种 | 2.6–5.3 | 过长前置定语、「当…时」、前置话题壳「对于…来说」、句首「然而，」、「这意味着」复述句 |

- **被推翻的流行说法（同样重要）**：句长均匀度 R=0.87（作者最初报过 51 倍，后查出是切分 bug）；正文设问 R=0.05（**人类是 AI 的 17 倍**）；比喻标记 R=0.42（人类 2.4 倍）；口语连接词 R=0.26；单字虚词「就」R=0.45（人类 2 倍多）。作者结论：通过检验的特征集中在**篇章与结构**，不在词汇或标点。
- 模型差异：破折号 DeepSeek 5.16 / Claude 4.25 / Gemini 0.51 / GPT 0.11 / Kimi 2.32（极差 40 倍）；对举 Gemini 最低、GPT 最高；问句小标题 Gemini 最高。说明「AI 文风」不是单一形态。
- 还公开了 6 次测量失误（算子覆盖范围、分母选择等），并给出复算脚本（`compare-human-ai.py` / `check-structure.py` / `check-translationese.py`）。
- 可借鉴：①段首零回指是目前最强的中文特征，口播稿里同款问题很常见（段落起头就抛一句「说实话」，却不说在评价什么）；②拟人化喻体要进词表；③反向数据告诉我们**别删设问、别删比喻、别删虚词**；④「白名单 + 信息守恒 + 语义判断排除」；⑤规则标 [corpus]/[经验]，比装权威可信。
- 局限：语料不公开（作者自承不可核验）；话题/文体没严格配对；正则只能测形态，语义层测不到；11 项规则偏书面（破折号、冒号、小标题），口播稿要重新取样；结论有时效性（模型在收敛）。
- License：MIT。

#### C5. DW-Studio/sloplint —— 4★，中文检测规则库的工程格式可以直接借

- 链接：https://github.com/DW-Studio/sloplint ｜ star 4 ｜ MIT ｜ 网页版 https://dw-studio.github.io/sloplint/ + skill 版，共用 `rules/patterns.json`（v2.1.0）
- 核心方法：16 条规则，每条带 `id / name / weight / evidence / R / type / regex / keywords / comment`；`type` 分 regex、density、density-below、line-start。评分公式：**加权命中 ÷（加权命中 + 6）** 映射到 0–100（calibration 6.0），是「浓度分」不是判决。Skill 版另加 3 条要 LLM 判断的语义规则（段首零回指、拟人化比喻、相邻句同构）。
- 规则摘录（可直接当词表）：引列表的冒号（主要包括/主要分为/具体如下，w3，R 9.4）、提示式冒号（核心是/说白了/答案是，w3）、不是…而是…（w3，R 3.4）、说白了式开场（w3）、一二三式小标题（w3）、破折号太多（density 阈值 1.5，w3）、翻译腔（当…时/对于…来说/这意味着/句首「然而，」，w3）、顿号成串（density 2.5，w2）、**通篇没数字**（density-below 8.0，w2）、万能开头（随着…的发展/众所周知，w1）、每段都综上（w1）、没有立场（各有优缺点/因人而异，w1）、凑数成语（与时俱进/开拓创新，w1）、空形容词（显著提升/大幅改善，w1）。
- 每条规则都写了一行「为什么」的 comment，例如冒号规则：`冒号前面那句是废话，只负责引出后面的列表。真人说话不会先绕这么一圈。`
- 可借鉴：①规则 JSON 结构可直接当我们参考库的数据格式；②「加权命中/(命中+6)」比直接扣分平滑，长文不会被线性惩罚；③threshold/density 型规则而不是「命中即改」；④R 值和「未验证」标在规则上；⑤给规则写「人话理由」。
- 局限：规则直接复用 lieflat 的结论，而 lieflat 语料偏书面；破折号密度、冒号、小标题这些口播稿几乎不出现；只有 16 条覆盖有限；网页版不接 LLM，误报要人自己看。
- License：MIT。

#### C6. Takamatsu-Hikaru/humanize-skill —— 4★，把「过度解释」当核心问题

- 链接：https://github.com/Takamatsu-Hikaru/humanize-skill ｜ star 4 ｜ MIT ｜ 中英双语
- 核心方法：不做 AI 味评分，不判断作者身份；**两遍检查**——第一遍看内容（主线、每段作用、信息量、比例），第二遍看表达（过度教学、正确但无用的话、防御性声明、自我弱化）；标题标明内容（「官网承担什么」→「官网功能」）；方案以陈述为主；删除导览式/陪伴式语气；「事实不足时标明缺少，不能靠润色补出一套安排」。
- 摘录几个真实案例：「这不仅是一场比赛，更是一次探索未来、实现成长的旅程」→「比赛设置计算机视觉、Agent 和具身智能三个方向，提供学习资料、算力支持与交流答疑」；「先让同学进得来、看得懂、能报名」→「AI 社将于 10 月 13 日发布赛事公告、三份赛题说明和队伍登记表」。作者原话：`单列一张「AI 高频词表」，很容易把好句子一起删掉。`
- 可借鉴：①「标题/小标题写内容名，不写成提问或行动指令」——口播选题标题同理；②「过度解释/防御性写作」是比词表更结构性的中文 AI 特征；③产品边界说法（不做 AI 检测、不承诺过检测器）；④「不输出 AI 味评分」是另一种选择（和 de-ai-flavor 相反，说明评分是产品选择不是必须）。
- 局限：面向方案/文档，不碰口播、语气词、节奏；无词表无检测器；仓库很新。
- License：MIT。

### D. 其他相关项目/资源（速览）

| 项目 | star | 方法要点 | 可借鉴 | 局限 | License |
|---|---|---|---|---|---|
| [RobinZorro86/humanizer-zh-plus](https://github.com/RobinZorro86/humanizer-zh-plus) | 7 | 上游 33 pattern + **5 个中文特有**：四字格堆砌、文言虚词滥用、中文排比（是…是…是/有…有…有）、套路结尾词、段落节奏均匀 | 5 条中文特有项的触发词清单可直接进我们的中文词表 | 中文项偏书面；仍以「扫 pattern」为主 | MIT |
| [OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL](https://github.com/OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL) | 889 | 从 7 篇真实作者文章提炼写作特征；24 项 AI 痕迹检测；七大铁律 + 段落谱系/句式节奏/标点预算的量化约束；`style_audit.js` + `style-lint.ps1` | 量化规则（句长方差、标点预算）的做法；说明「风格复现」和「去 AI 味」是两层 | **仓库无 LICENSE**，不能搬文本；规则服务于特定作者风格，通用性存疑；未逐个核实其 SKILL 内部 | 未注明 |
| [zhuyansen/awesome-humanizer-skills](https://github.com/zhuyansen/awesome-humanizer-skills) | 5 | 242 个仓库索引 + 2026-10-07 实测 26 个（23 个跑通），三维打分（读起来像人 / 有没有动结构 / 事实是否保留） | 唯一有横向实测数据的索引；结论「19/21 只改措辞不改结构」是重要的行业判断 | 索引本身非工具；评分来自模型评审，非人工双盲 | NOASSERTION |
| [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | — | 上游总源头；原则是「线索，不是证据」；分 Content / Language / Style / Communication / Markup / Citations / Signs of human writing / Ineffective indicators / Historical indicators 等节 | 免费、更新最快、多语言版本（中文版「AI生成文的特徵」）；适合当定期回扫的基准 | 面向维基编辑场景，很多项（wikitext、引用格式）与文案无关；正文较长，抓取时被截断，细节**部分未核实** | CC BY-SA |

---

## 三、横向对比：他们到底差在哪

1. **形态三派**：prompt-only skill（大多数：blader、stop-slop、Humanizer-zh、say-it-human、de-ai-flavor…）、规则库 + CLI/网页（slop-lint、sloplint、Vale）、研究驱动（lieflat）。其中「skill + 独立检测器」的组合最少（maxsancheez 和 slopster 算半个），而口播审稿其实很需要「确定性命中 + 模型判断」两层。
2. **流程高度同构**：检测清单 → 改写 → **保真校验** → 报告/评分。真正的分歧在：
   - 给不给分数：de-ai-flavor 给 0–100，stop-slop 给 5 维，tagore 给 8 维 56/80，Humanizer-zh 明确不给；
   - 改不改结构：blader/tagore 允许改段落结构，多数中文 skill 只改句子；
   - 要不要作者样本：blader/HafidIdrissi 有 voice matching，Humanizer-zh 只「借鉴表达习惯」；
   - 有没有「保留清单」：blader、op7418 有，多数项目只有删除清单。
3. **结构层是空白**。awesome-humanizer-skills 的实测（23 个 skill、40 次改写）显示：课文式总结 26/26 存活、圆满结尾 28/28 存活、单一叙事线 40/40 存活；连「结构层」评分最高的 humanizer-stack 也只算部分改到。换句话说，现有工具都在「换词、删句、拆节奏」，没人真正重排信息顺序、删掉那个「升华段」。
4. **规则在漂移**。slop-lint 用 `--discover` 每月重测模型输出 vs 人类基线；Wikipedia 页面还在更新（破折号一节标了 2022–2026）；lieflat 作者自己说 GPT 的破折号频率一年内从「近乎每句一次」降到 0.11。任何静态词表半年就过时。
5. **中文有真正的经验证据，但只覆盖书面**。lieflat 的 11 项是唯一经过对照语料验证的中文清单，但它的语料是文章不是口播；口播的停顿、重复、称呼、互动、语速这些维度，目前没有任何公开项目做过量化。

---

## 四、对中文口播/文案场景的启示

### 4.1 可以直接吸收进 SKILL.md 的做法（8 条核心 + 2 条补充）

1. **检测与改写分两遍，检测必须引用原文**（blader / maxsancheez / tagore / Humanizer-zh 都这么做）。落到我们：口播稿先出一张「命中清单」，每行是「原句 + 类型 + 依据（哪条规则/哪个频率比）」，再动手改。理由：口播是一次性的，改错了听众没法回看；引用原文也让用户能审。
2. **密度阈值 + 决策树，不做「命中即改」**（say-it-human 的 5 问决策树 + lieflat 的 R 值）。落到我们：口播稿按「每 100 字」或「每条视频」算密度；保留「换话题测试」「是不是喘息句」「删了会不会失去温度」三问——这三问对处理口播里的金句、口头禅、重复句特别有效。
3. **先画保护区，再改**（say-it-human）。落到我们：把「这个人平时会这么说」的句子先标出来——口头禅、自我更正（「不对，我想想」）、突然停顿、方言词、跑题。可操作标准照抄：同一表达全文 ≥3 次且不在模板语境里。
4. **硬保真门禁，一票否决**（op7418 / blader / de-ai-flavor 都强调）。落到我们的 SKILL 约束：不新增数字、案例、来源、第一人称经历；不把「可能」改成「确定」、不把「计划」写成「已经」；篇幅 ±20%（口播直接对应时长，低于 85% 就是删过头）。口播改写最容易在「补人味」时编出「我有个朋友」——这条必须写死。
5. **按渠道/体裁分档，一套规则不能打天下**（say-it-human 的体裁表 + de-ai-flavor 的文体特调 + Takamatsu 的「读者与用途」）。落到我们：至少分四档——短视频口播（15–60 秒）、长视频/口播长文（1–3 分钟）、公众号/文案长文、朋友圈/聊天/通知。口播档允许设问、金句、重复、不完美；书面档要克制；通知/周报里「本周完成」不算 AI 味。
6. **打分用「加权浓度」而不是「AI 率」**（de-ai-flavor 的 8 项加权 + sloplint 的 `命中/(命中+6)` + ±10 浮动声明）。落到我们：给 0–100 的「AI 腔浓度」+ 分项明细，明确不承诺过任何检测器、不判断作者身份（Wikipedia 和 OpenAI 自己的数据都说明检测不可靠）；口播档可以单独加「气口密度 / 句长方差 / 具体细节数 / 称呼与互动」四个维度，而不是照搬英文的 directness/rhythm/trust。
7. **报告必须有「亮点保留」和「改了什么」**（de-ai-flavor 的必填亮点 + humanizer 的变更表）。落到我们：每一版改写附「这句为什么留」（例如「这里的重复是口播强调，保留」）和「三行内改了什么」。用户知道哪些是故意留的，下次才敢继续用。
8. **每条规则标来源与验证状态，预留更新入口**（slop-lint 的 since/source/版本号 + lieflat 的 [corpus]/[经验] 标注）。落到我们：中文 AI 词表半年漂移一次；SKILL 里每条词表规则标「语料验证 / 经验 / 待验证」，并写清如何替换（附一段「如何用同题生成 vs 人类文案重测词表」的流程）。

补充两条也值得进 SKILL：

9. **「加人味」要有结构化动作，不是口号**（HafidIdrissi 的 personality pass + say-it-human 的人话三要素 + tagore 的 personality）。清完痕迹后至少做三件事：补一个具体细节、给一个真实态度或犹豫、放一个短句气口。但只能从原文/用户素材里取，不许编。
10. **段落级/结尾级检查**（tagore 的 amplifier paragraph 删除测试 + mic-drop metronome）。口播版：每条视频的结尾是不是又是「这才是……的本质」三连；中间有没有一段只是把前面的话换种说法再说一遍（删掉它，信息有没有少）。

### 4.2 不打算照搬的做法（5 条，附原因）

1. **不照搬「禁副词 / 禁被动 / 禁破折号 / 禁设问 / 禁金句」的全禁式规则**（stop-slop、blader 的绝对项）。
   原因：中文语料实测是反的——设问人类是 AI 的 17 倍（R=0.05）、比喻 2.4 倍（R=0.42）、单字虚词「就」人类 2 倍多（R=0.45）；口播里的「其实/真的/就/你看」是节奏和互动，不是废话；中文被字句和英文被动不是一回事。照搬「kill all adverbs」会把口播改干。
2. **不照搬 19/29/38 项大清单的全量扫描**。
   原因：30 秒口播稿全量扫 30 项，等于逼模型「为改而改」；op7418 自己说「模式清单是检查线索，不是词语黑名单」；Takamatsu 也提醒「单列高频词表很容易把好句子一起删掉」。我们的口播档应该只查 8–12 项高频问题，长文档才上全量。
3. **不把「删掉升华 / 删掉总结」当卖点**。
   原因：awesome 实测证明，现有工具几乎删不掉课文式总结（26/26 存活）和圆满结尾（28/28 存活）；而口播体裁本来就需要收口金句（say-it-human 明确「短视频文稿金句收束不判定」）。我们能做的是「金句密度/原创度」而不是「删除」——比如一条视频不超过一个金句、金句必须来自正文提炼而不是空降。
4. **不直译英文词表**（delve→深入探讨、tapestry→织锦、em dash→破折号）。
   原因：翻译后命中率极低或误伤；中文 AI 腔有自己的高频（不仅…而且、值得注意的是、赋能/闭环/抓手、说到底、从这个角度看、不是…而是…）；lieflat 的 11 项才是中文语料验证过的。英文清单只能当**结构灵感**（如 false agency、staged run-up、段首零回指），不能当词表搬。
5. **不用书面样本做「声音匹配」后直接生成口播**（HafidIdrissi / blader 的 voice matching 用法）。
   原因：书面样本的句长、连接词、标点习惯会产出「像文章的说话」；口播需要更短的句、更多停顿、称呼和互动。我们应该收「口播转写/自己说话的文字记录」作样本，并且样本的优先级低于事实与体裁（op7418 的优先级表就是这个思路）。

---

## 五、访问情况与未核实项

- **star/fork** 全部取自 2026-10-19 的 `api.github.com` 快照，会继续变。
- **npm `slop-lint`**：npmjs.com 页面被 Cloudflare 拦（HTTP 403），信息来自 `registry.npmjs.org/slop-lint/latest` 元数据 + GitHub README，已核实。
- **HafidIdrissi/humanizer**：`main` 分支 README 404，默认分支实为 `master`，已用 master 核实 README；其 `SKILL.md` 与 `references/` 内部规则**未逐条核实**。
- **Wikipedia:Signs of AI writing**：抓取时正文被截断，只核实了目录结构与项目来源说明；具体条目的细节来自 blader/humanizer、Tagore、op7418 的转述，**部分未逐条对照原文**。
- **OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL**：我只读了 `gitliuyun` fork 的 README（其上游即 OUBIGFA，star 889 来自 API），作者 README 中提到的 24 项检测内部清单未逐条核实；且**仓库没有 LICENSE**，不建议复制其文本。
- **maxsancheez/humanizer-skill**：`license` 字段为 null，仓库内没有 LICENSE 文件，代码/文本不可直接复用。
- **apurvrdx1/tagore**：通过 slopster 的 `skills/tagore/SKILL.md` 完整读取；独立仓库本身只核实了 API 元数据（54★、MIT）。
- 未展开核实（仅索引里看到）：FeedHive/ai-slop-detector（120 patterns）、Nanako0129/sepia（3.2k★）、lynote-ai/humanize-text（3.4k★）、sgaofen/humanizer-local-model 等，**未读原文，不写结论**。

## 六、值得直接再读的原始文件（raw 地址）

- blader/humanizer 规则：https://raw.githubusercontent.com/blader/humanizer/main/SKILL.md
- stop-slop 词表：https://raw.githubusercontent.com/hardikpandya/stop-slop/main/references/phrases.md ｜ 结构表：https://raw.githubusercontent.com/hardikpandya/stop-slop/main/references/structures.md
- maxsancheez 检测器：https://raw.githubusercontent.com/maxsancheez/humanizer-skill/main/code/tells.py ｜ skill：https://raw.githubusercontent.com/maxsancheez/humanizer-skill/main/skill/SKILL.md
- Tagore（29 patterns + 8 维评分）：https://raw.githubusercontent.com/t0ddharris/slopster/main/skills/tagore/SKILL.md
- slopster Vale 规则：https://raw.githubusercontent.com/t0ddharris/slopster/main/styles/Slopster/BannedWords.yml ｜ https://raw.githubusercontent.com/t0ddharris/slopster/main/styles/Slopster/JargonSwaps.yml
- slop-lint 说明：https://raw.githubusercontent.com/eric-sabe/slop-lint/main/README.md
- Humanizer-zh 规则：https://raw.githubusercontent.com/op7418/Humanizer-zh/main/SKILL.md
- say-it-human 19 维详解：https://raw.githubusercontent.com/taxueseek/say-it-human/main/references/extended-patterns.md
- de-ai-flavor：https://raw.githubusercontent.com/masonweb3/de-ai-flavor/main/SKILL.md
- lieflat 研究：https://raw.githubusercontent.com/larashero3-dotcom/lieflat-less-ai-tone/main/README.md
- sloplint 规则库：https://raw.githubusercontent.com/DW-Studio/sloplint/main/rules/patterns.json
- humanizer-zh-plus 中文 5 pattern：https://raw.githubusercontent.com/RobinZorro86/humanizer-zh-plus/main/references/chinese-patterns.md
- Wikipedia 原页：https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
