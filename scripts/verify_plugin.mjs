#!/usr/bin/env node
/**
 * verify_plugin.mjs — 不安装、不重启，验证 DSH 桥接插件能否正确注册 skill。
 *
 * 做法：用假的 ctx.skills.register 调用 apply()，检查注册名、description、
 * SKILL.md 内容、注入的技能目录，以及 references/ 和 scripts/ 是否都在。
 *
 * 用法：node scripts/verify_plugin.mjs
 */

import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { apply } from '../dsh-plugin/lib/index.js'

const SKILL_DIR = join(dirname(fileURLToPath(import.meta.url)), '..')
let registered = null
let failures = 0

function check(ok, label) {
  if (ok) {
    console.log('  ✓ ' + label)
  } else {
    failures += 1
    console.log('  ✗ ' + label)
  }
}

apply({
  skills: {
    register: (skill) => {
      registered = skill
    },
  },
})

console.log('== DSH 桥接插件自检 ==')
check(registered !== null, 'apply() 调用了 ctx.skills.register')
check(registered?.name === 'de-ai-flavor', `注册名是 de-ai-flavor（实际：${registered?.name}）`)
check(typeof registered?.description === 'string' && registered.description.length > 50,
  'description 已提供且长度足够')
check(typeof registered?.content === 'string' && registered.content.includes('# 去 AI 味写作规范'),
  'SKILL.md 正文已读入')
check(registered?.content.includes('**技能目录**'), '正文末尾注入了技能目录绝对路径')
check(registered?.content.includes(SKILL_DIR), '注入的目录路径与本项目一致')

const required = [
  'SKILL.md',
  'references/ai-tells-cn.md',
  'references/human-voice/human-voice-patterns.md',
  'references/human-voice/rewrite-examples.md',
  'references/genres/00-文体矩阵.md',
  'references/genres/01-作文与文学写作.md',
  'references/genres/02-公众号与文章.md',
  'references/genres/03-通知与公告.md',
  'references/genres/04-视频口播.md',
  'references/genres/05-朋友圈与聊天.md',
  'references/genres/06-产品与课程文案.md',
  'references/genres/07-润色与改稿.md',
  'references/genres/08-报告与总结.md',
  'references/review-layers.md',
  'references/official-style.md',
  'samples/hard-cases/01-ai-but-clean.md',
  'samples/hard-cases/01-ai-but-clean.raw.md',
  'samples/09-essay-zhineng.md',
  'samples/09-essay-zhineng.notes.md',
  'samples/10-ai-report.md',
  'samples/11-human-report.md',
  'samples/external/zhuziqing-congcong.md',
  'samples/external/zhuziqing-beiying.md',
  'samples/external/luxun-guxiang.md',
  'samples/external/gaokao-beijing-2020-zhongguo-jingshen.md',
  'samples/external/gaokao-beijing-2020-shuo-weiji.md',
  'samples/external/gaokao-beijing-2020-wo-yu-guo.md',
  'samples/external/zhongkao-beijing-2024-baibeixin.md',
  'samples/external/notice-moe-2025.md',
  'samples/external/gov-report-work-2025.md',
  'samples/external/article-shmeea-essay-review.md',
  'samples/external/article-bjksb-2024-gaokao-review.md',
  'samples/external/notice-school-nwu-2025.md',
  'samples/external/notice-school-nwu-studentcard-2025.md',
  'samples/external/report-vocational-school-2024.md',
  'samples/external/gov-summary-yuanjiang-2024.md',
  'research/github-survey.md',
  'research/genre-notes.md',
  'research/deep/gaokao-essay.md',
  'research/deep/official-docs.md',
  'research/deep/gov-tone.md',
  'research/deep/ai-policy.md',
  'scripts/ai_tell_lint.py',
  'scripts/review_extract.py',
  'scripts/selftest.py',
]
for (const rel of required) {
  check(existsSync(join(SKILL_DIR, rel)), `文件存在：${rel}`)
}

console.log(failures === 0 ? '\n✓ 桥接插件自检通过，可以安装进 DSH' : `\n✗ ${failures} 项失败`)
process.exit(failures === 0 ? 0 : 1)
