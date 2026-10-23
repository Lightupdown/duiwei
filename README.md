# 去 AI 味 · de-ai-flavor

> 中文写作与改写的「去 AI 味」规范：六类文体、分层审稿、体检脚本、正负样本库。
>
> A Chinese writing/rewriting skill for removing "AI flavor" — genre-aware rules, layered human review, a surface-level linter, and annotated positive/negative samples. It is **not** an AI detector and does **not** help evade detection.

[![selftest](https://github.com/Lightupdown/de-ai-flavor/actions/workflows/ci.yml/badge.svg)](https://github.com/Lightupdown/de-ai-flavor/actions/workflows/ci.yml)

## 这是什么

一套让中文写得更像「具体的人在这个场合说话」的写作规范，也是一个可直接装进 AI Agent 的技能：

- **六类文体分开处理**：作文 / 公众号文章 / 通知公告 / 视频口播 / 朋友圈聊天 / 产品课程文案；另加「只说了润色一下」的改稿流程。
- **两层审稿**：脚本查词、句式、节奏等表面特征；第二层人工查逻辑、工序可信度、人物台词、细节负载、结构闭环。
- **两张评分卡**：A 真实感（防 AI 腔与设计感）、B 文笔（防越改越干瘪）。两张都过才交付。
- **可验证**：体检脚本、13 组改写案例回归、坏样本 / 正样本对照、自动自检脚本。

## 这不是什么

- **不是 AI 检测器**，不承诺通过任何检测工具，也不判断作者身份。
- **不是代写工具**：考试、竞赛、毕业论文、评奖场景只做错别字 / 病句级提示；不接「帮我把 AI 稿改到看不出来 / 过检测」。
- 不追求「像人」的表演式口语（堆语气词、硬造错别字、写成聊天记录），那只是另一种 AI 味。

## 起因

一套规范来自一条视频评论的观察：AI 输出的中文有几类很明显的习惯——

- 高频口癖：「这点我认」「这句我先收下」「我熟」「先欠着」「都归我管」
- 防御性句式：「是 X，不是 Y」
- 生硬缩略短句：「哪句还像 AI，直接指出来」
- 太有效率、太有功能性：缺少人说话时的停顿、转折、语气词、重复、改口，甚至错别字。

顺着这些观察做成了规则、脚本和样题库。后来发现更深的一层：词句都干净、细节也不少，但**每个细节都在服务主题、人物一开口就是格言、结尾全是设计**，人一读还是觉得假。第二层审稿就是为这类「lint 0 分但不像人」的文本加的。

## 快速开始

直接用：

- 把 [`SKILL.md`](SKILL.md) 当 system prompt / 技能文件给任意模型，按需加载 `references/` 里的档案。
- 体检一段文字：

```bash
python3 scripts/ai_tell_lint.py 你的稿子.md
python3 scripts/ai_tell_lint.py --genre essay 作文.md          # 作文
python3 scripts/ai_tell_lint.py --genre notice 通知.md         # 通知 / 公告
python3 scripts/ai_tell_lint.py --genre gov 评论.md            # 官方评论 / 政务
```

- 审稿素材（剧本式提取段落骨架、台词、数字、意象、结尾）：

```bash
python3 scripts/review_extract.py 你的稿子.md
```

- 项目自检：

```bash
python3 scripts/selftest.py        # 样本区分度 + 案例回归 + 分文体档案完整性
node scripts/verify_plugin.mjs     # DSH 桥接插件自检（不安装、不重启）
```

`SKILL.md` 的工作流是：**先判文体 → 读对应档案 → 机器层体检 → 第二层审稿（L2 逻辑 / L3 人物细节 / L4 结构）→ 打 A/B 两张卡 → 报告**。

## 目录

```
.
├── SKILL.md                      # 技能本体：工作流、硬门禁、自检
├── references/
│   ├── ai-tells-cn.md            # 中文 AI 味特征清单 + 配额 + 语料验证 R 值
│   ├── review-layers.md          # 第二层审稿 + A/B 两张评分卡 + 停止规则
│   ├── human-voice/              # 人话特征库 + AI→人 改写案例
│   └── genres/                   # 文体矩阵 + 7 个文体档案
├── research/
│   ├── github-survey.md          # 17 个同类项目调研
│   ├── genre-notes.md            # 分文体外部资料
│   └── deep/                     # 作文评分 / 公文规范 / 政务文风 / AI 使用政策
├── samples/
│   ├── 01–09-*.md                # 正负对照样本
│   ├── hard-cases/               # 坏样本：lint 0 分但人工不过关
│   └── README.md
├── scripts/
│   ├── ai_tell_lint.py           # 文本体检（零依赖）
│   ├── review_extract.py         # 第二层审稿素材提取
│   ├── selftest.py               # 项目自检
│   └── verify_plugin.mjs         # DSH 插件自检
├── dsh-plugin/                   # 可选：把技能注册进 DSH 的桥接插件
└── .github/workflows/ci.yml      # GitHub Actions：跑自检
```

## 六类文体，各用各的标准

| 文体 | 口语容忍 | 一句话标准 |
| --- | --- | --- |
| 作文 / 文学 | 0（引用人物对话除外） | 书面、优美、有个人声音；口语词 0 |
| 公众号 / 文章 | 低（3–5 / 千字） | 让人读完；故事和细节大于结构和总结 |
| 通知 / 公告 | 0 | 准确、完整、可执行；去官话，不加人味 |
| 视频口播 | 高（1–3 / 百字） | 像真人在说话；气口、具体、不念稿 |
| 朋友圈 / 聊天 | 最高 | 短、随意、像本人；不演、不客服 |
| 产品 / 课程文案 | 低 | 具体、可验证、承认局限；不吹、不假 |

详细规则见 [`references/genres/00-文体矩阵.md`](references/genres/00-文体矩阵.md) 和它索引的档案。

## 为什么 lint 0 分也可能不过关

`ai_tell_lint.py` 查的是表面：词表、防御性句式、句长 / 段长、标点、口语标记。它能抓「贴脸」的 AI 腔，但抓不到另一类更高级的假：

- 人物做的事前后矛盾；
- 人物说出一句格言（「哪有不坏的东西」「别用蛮力，找那个劲」）；
- 每个细节都在服务主题，没有一个废的；
- 结构是个闭环，结局完全可预测；
- 结尾用阳光 / 意象收束。

所以加了第二层审稿（[`references/review-layers.md`](references/review-layers.md)）：

- **L2 逻辑**：行动线、视角、时间线、物件连续性、工序可不可信、事件有没有阻力、有没有记忆误差。
- **L3 人物与细节**：台词三问（禁止长辈说格言）、细节负载审计（至少 2 处无用闲笔、象征细节 ≤1、回收率不能过半）、表演式人味、叙述者主体性。
- **L4 结构**：可预测性、二元对立闭环、顿悟结尾、结尾三合一要删一个。
- **两张卡**：A 真实感（10 项 / 20 分，<14 不交付）；B 文笔（5 项 / 10 分，<7 要打磨）。只盯 A 会写成干瘪流水账，只盯 B 会写成漂亮假文。

## 验证与样本

- 机器层：13 组「AI 原稿 → 改后」案例全部降分，平均 18.6 → 0.0；样本区分度见 [`samples/`](samples/README.md)。
- 第二层：标准失败案例 [`hard-cases/01-ai-but-clean.md`](samples/hard-cases/01-ai-but-clean.md)（lint 0 分，卡 A 3/20、B 4/10）与正样本 [`09-essay-zhineng.notes.md`](samples/09-essay-zhineng.notes.md)（lint 0 分、零第二层提示；两轮独立盲评 A 17/20 · B 9/10、A 15/20 · B 9/10，均判「能交付」）。
- `selftest.py` 覆盖上述全部回归项；`verify_plugin.mjs` 覆盖 DSH 集成文件。

## 安装为 DSH skill（可选）

DSH 的技能通过一个桥接插件注册，桥接插件在 [`dsh-plugin/`](dsh-plugin/)。

1. 把仓库克隆到固定位置，例如 `~/skills/de-ai-flavor`。
2. 在 DSH desktop profile 的 `package.json` `dependencies` 里加一条 link 依赖：
   `"de-ai-flavor-dsh": "link:<你的路径>/de-ai-flavor/dsh-plugin"`
3. 在同目录 `cordis.patch.yml` 的 `insert` 列表里加：
   `- id: de-ai-flavor-dsh` / `name: 'de-ai-flavor-dsh'`
4. 在 profile 目录跑 `pnpm install`（或用等价的符号链接把包放进 `node_modules`）。
5. 重启 DSH，技能列表里会出现 `de-ai-flavor`。

> 不同版本的 DSH / 其他 Agent 框架的加载方式可能不同；不装 DSH 也能把 `SKILL.md` 直接当提示词使用。

## 已知局限

- 体检脚本只查表面特征；具体性、事实、幽默、语用好坏靠人判断。
- 短文案（<150 字）分数容易被低估，以命中项为主。
- 分数是「AI 腔浓度」不是判决；不承诺通过任何检测器。
- 词表有时效性，模型风格在漂移，建议每半年用「同题生成 vs 人类文案」重测一次。
- 第二层审稿靠人（或独立 critic 代理）判断，没有自动化评分；脚本 0 分不代表过关。
- 高考 / 中考评分细则各省不完全公开，深研里的分项数据部分是教研整理（B 级），引用时注意。
- 政策与官方文风会更新，建议每学期复核 `research/deep/`。

## 贡献

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。核心要求：

- 加样本要附来源与体检分；不要为了凑特征写漫画式 AI 腔。
- 只借鉴方法，不复制没有 LICENSE 的项目文本；引文注明出处。
- 改完跑 `python3 scripts/selftest.py` 和 `node scripts/verify_plugin.mjs`。

## 方法来源与致谢

调研了 17 个同类项目和一批中文外部资料（作文评分、公文规范、政务文风、AI 使用政策），完整清单见 [`research/github-survey.md`](research/github-survey.md)、[`research/deep/`](research/deep/)。

主要参考：[blader/humanizer](https://github.com/blader/humanizer)、[op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)、[taxueseek/say-it-human](https://github.com/taxueseek/say-it-human)、[lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone)、[masonweb3/de-ai-flavor](https://github.com/masonweb3/de-ai-flavor)、[DW-Studio/sloplint](https://github.com/DW-Studio/sloplint)。只借鉴方法与流程，未复制无 LICENSE 项目的文本。

## License

[MIT](LICENSE)。第三方引文与政策原文已在各研究文件中标注来源，按其原始许可使用。
