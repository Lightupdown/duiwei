# 对味 · duiwei

> 中文写作与改写的「去 AI 味」规范：八类文体、分层审稿、体检脚本、正负样本库。
>
> A Chinese writing/rewriting skill for removing "AI flavor" — genre-aware rules, layered human review, a surface-level linter, and annotated positive/negative samples. It is **not** an AI detector and does **not** help evade detection.

[![selftest](https://github.com/Lightupdown/duiwei/actions/workflows/ci.yml/badge.svg)](https://github.com/Lightupdown/duiwei/actions/workflows/ci.yml)

## 这是什么

一套让中文写得更像「具体的人在这个场合说话」的写作规范，也是一个可直接装进 AI Agent 的技能：

- **八类文体分开处理**：作文 / 公众号文章 / 通知公告 / 视频口播 / 朋友圈聊天 / 产品课程文案 / 报告总结 / 演讲稿；另加「只说了润色一下」的改稿流程。
- **三档审稿**：叙事类查逻辑 / 工序 / 人物台词 / 细节负载 / 结构闭环；议论类查扣题与论证；功能类（通知 / 报告 / 聊天 / 文案）只走保真门禁 + 文体自检。脚本查词、句式、节奏等表面特征，0 分不代表过关。
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

顺着这些观察做成了规则、脚本和样题库。后来发现更深的一层：词句都干净、细节也不少，但**每个细节都在服务主题、人物一开口就是格言、结尾全是设计**，人一读还是觉得假。这套分层审稿就是为这类「lint 0 分但不像人」的文本加的。

## 示例不是素材

档案里的「改后」示例（报告里的 37 个项目、146 万元，作文里的柿子树、腌菜缸）都是**演示数字 / 细节，不是原稿事实**。真实改写只能用原文或用户提供的素材；缺数据写 `【待补：项目数 / 同比 / 原因…】`，不许补成具体数字。报告档案同时给了「无素材占位版」和「有素材演示版」，`rewrite-examples.md` 也逐组标了演示素材。

这条比风格规则更硬：照着示例的数字改，就是在编造。

## 快速开始

直接用：

- 把 [`SKILL.md`](SKILL.md) 当 system prompt / 技能文件给任意模型，按需加载 `references/` 里的档案。
- 体检一段文字：

```bash
python3 scripts/ai_tell_lint.py 你的稿子.md
python3 scripts/ai_tell_lint.py --genre essay 作文.md          # 作文
python3 scripts/ai_tell_lint.py --genre notice 通知.md         # 通知 / 公告
python3 scripts/ai_tell_lint.py --genre gov 评论.md            # 官方评论 / 政务
python3 scripts/ai_tell_lint.py --genre report 总结.md        # 报告 / 总结
python3 scripts/ai_tell_lint.py --genre speech 演讲稿.md      # 演讲稿
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

`SKILL.md` 的工作流是：**先判文体 → 读对应档案 → 机器层体检 → 按档位审稿（叙事 L2–L4 + 卡 A/B；议论卡 C/B；功能类档案自检）→ 报告**。

## 目录

```
.
├── SKILL.md                      # 技能本体：工作流、硬门禁、自检
├── references/
│   ├── ai-tells-cn.md            # 中文 AI 味特征清单 + 配额 + 语料验证 R 值
│   ├── review-layers.md          # 叙事类四层审稿 + A/B 卡 + 议论类卡 C + 停止规则
│   ├── official-style.md         # 官方文体一页判定表（四测试、公文惯例 A/B/C）
│   ├── human-voice/              # 人话特征库 + AI→人 改写案例
│   └── genres/                   # 文体矩阵 + 9 个档案（8 类文体 + 润色）
├── research/
│   ├── github-survey.md          # 17 个同类项目调研
│   ├── genre-notes.md            # 分文体外部资料
│   └── deep/                     # 作文评分 / 公文规范 / 政务文风 / AI 使用政策
├── samples/
│   ├── 01–11-*.md                # 正负对照样本（含报告正负样本）
│   ├── external/                 # 外部真实文本（考试作文/通知/总结/文学；版权见该目录 README）
│   ├── hard-cases/               # 坏样本：lint 0 分但人工不过关
│   └── README.md
├── scripts/
│   ├── ai_tell_lint.py           # 文本体检（零依赖）
│   ├── review_extract.py         # 叙事审稿素材提取
│   ├── selftest.py               # 项目自检
│   └── verify_plugin.mjs         # DSH 插件自检
├── dsh-plugin/                   # 可选：把技能注册进 DSH 的桥接插件
└── .github/workflows/ci.yml      # GitHub Actions：跑自检
```

## 八类文体，各用各的标准

| 文体 | 口语容忍 | 一句话标准 |
| --- | --- | --- |
| 作文 / 文学 | 0（引用人物对话除外） | 书面、优美、有个人声音；口语词 0 |
| 公众号 / 文章 | 低（3–5 / 千字） | 让人读完；故事和细节大于结构和总结 |
| 通知 / 公告 | 0 | 准确、完整、可执行；去官话，不加人味 |
| 视频口播 | 高（1–3 / 百字） | 像真人在说话；气口、具体、不念稿 |
| 朋友圈 / 聊天 | 最高 | 短、随意、像本人；不演、不客服 |
| 产品 / 课程文案 | 低 | 具体、可验证、承认局限；不吹、不假 |
| 报告 / 总结 | 0 | 可信优先：数据有口径、问题不虚化、下一步能执行 |
| 演讲稿 | 中（每千字 1–3 个口头衔接） | 念出来像现场的人；结尾不喊口号、不排三连祈使；金句 0–1，上限不是任务 |

详细规则见 [`references/genres/00-文体矩阵.md`](references/genres/00-文体矩阵.md) 和它索引的档案。

## 为什么 lint 0 分也可能不过关

`ai_tell_lint.py` 查的是表面：词表、防御性句式、句长 / 段长、标点、口语标记。它能抓「贴脸」的 AI 腔，但抓不到另一类更高级的假：

- 人物做的事前后矛盾；
- 人物说出一句格言（「哪有不坏的东西」「别用蛮力，找那个劲」）；
- 每个细节都在服务主题，没有一个废的；
- 结构是个闭环，结局完全可预测；
- 结尾用阳光 / 意象收束。

所以加了分层审稿（[`references/review-layers.md`](references/review-layers.md)），并且**按档位分开**：

- **叙事类**（记叙文 / 散文 / 小说 / 公众号故事）：过 L2–L4 + 卡 A 真实感 + 卡 B 文笔。
- **议论类**（议论文 / 评论 / 分析文）：走卡 C（扣题 / 论点链 / 论据真实 / 分析 / 反驳 / 结论）+ 卡 B，不套「悬空 / 闲笔 / 记忆误差」。
- **功能类**（通知 / 公告 / 聊天 / 产品文案 / 报告总结）：只走保真门禁 + 该文体档案自检，不套叙事卡。

叙事类的 L2–L4：

- **L2 逻辑**：行动线、视角、时间线、物件连续性、工序可不可信、事件有没有阻力、有没有记忆误差。
- **L3 人物与细节**：台词三问（禁止长辈说格言）、细节负载审计（每个细节都在服务主题吗？素材里有没有不服务主题的细节可留？不为凑数加；象征细节 ≤1）、表演式人味、叙述者主体性。
- **L4 结构**：可预测性、二元对立闭环、顿悟结尾、结尾三合一要删一个。
- **两张卡**：A 真实感（10 项 / 20 分，从零写作 <14 不交付；改写时缺项 N/A、只作诊断）；B 文笔（5 项 / 10 分，<7 不交付，7 分打磨后复评）。只盯 A 会写成干瘪流水账，只盯 B 会写成漂亮假文。

## 验证与样本

- 机器层：13 组「AI 原稿 → 改后」案例全部降分，平均 18.6 → 0.0；样本区分度见 [`samples/`](samples/README.md)。
- 第二层：标准失败案例 [`hard-cases/01-ai-but-clean.md`](samples/hard-cases/01-ai-but-clean.md)（lint 0 分，卡 A 3/20、B 4/10）与正样本 [`09-essay-zhineng.notes.md`](samples/09-essay-zhineng.notes.md)（lint 0 分、零第二层提示；两轮独立盲评 A 17/20 · B 9/10、A 15/20 · B 9/10，均判「能交付」）。
- 报告 / 总结：正负样本 [`10-ai-report.md`](samples/10-ai-report.md)（36 分）与 [`11-human-report.md`](samples/11-human-report.md)（0 分）；lint 新增「报告 / 总结套话」检测。
- 外部真实文本：开发用 15 篇（调参 3 / 回归 12，不再对外报误报率）+ **真留出集 4 篇**（`samples/external-holdout/`，冻结标签 `holdout-v1`）；真留出集一次性评估 **0/4**。样本含考试作文、学校/政府通知、工作总结、公文、评析与公有领域文学。
- `selftest.py` 覆盖上述全部回归项；`verify_plugin.mjs` 覆盖 DSH 集成文件。

## 安装为 DSH skill（可选）

DSH 的技能通过一个桥接插件注册，桥接插件在 [`dsh-plugin/`](dsh-plugin/)。

1. 把仓库克隆到固定位置，例如 `~/skills/duiwei`。
2. 在 DSH desktop profile 的 `package.json` `dependencies` 里加一条 link 依赖：
   `"de-ai-flavor-dsh": "link:<你的路径>/duiwei/dsh-plugin"`
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
- 分层审稿靠人（或独立 critic 代理）判断，没有自动化评分；脚本 0 分不代表过关。
- 真留出集只有 4 篇（长度约 200–1150 字），且偏通知/散文；完整 800 字考场作文、企业工作总结、真实公众号文章还缺，0/4 不能外推到所有真实文本。
- 高考 / 中考评分细则各省不完全公开，深研里的分项数据部分是教研整理（B 级），引用时注意。
- 政策与官方文风会更新，建议每学期复核 `research/deep/`。
- 报告 / 总结目前只有一组正负样本，阈值与套话词表还需要真实工作总结、述职、情况报告来校准。
- 演讲稿专档刚建，口号测试与三连短句检测还需要真实演讲稿校准；当前只有一个小例子。

## 贡献

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。核心要求：

- 加样本要附来源与体检分；不要为了凑特征写漫画式 AI 腔。
- 只借鉴方法，不复制没有 LICENSE 的项目文本；引文注明出处。
- 改完跑 `python3 scripts/selftest.py` 和 `node scripts/verify_plugin.mjs`。

## 方法来源与致谢

调研了 17 个同类项目和一批中文外部资料（作文评分、公文规范、政务文风、AI 使用政策），完整清单见 [`research/github-survey.md`](research/github-survey.md)、[`research/deep/`](research/deep/)。

主要参考：[blader/humanizer](https://github.com/blader/humanizer)、[op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)、[taxueseek/say-it-human](https://github.com/taxueseek/say-it-human)、[lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone)、[masonweb3/de-ai-flavor](https://github.com/masonweb3/de-ai-flavor)、[DW-Studio/sloplint](https://github.com/DW-Studio/sloplint)。只借鉴方法与流程，未复制无 LICENSE 项目的文本。

## License

[MIT](LICENSE)。注意：`samples/external/` 下的考试作文、学校/政府通知与评析**不适用 MIT**，版权归原作者/发布方，仅作测试用途；详见该目录 README。第三方引文与政策原文已在各研究文件中标注来源。
