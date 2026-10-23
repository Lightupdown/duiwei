import { readFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

export const inject = ['skills']

// 技能本体与桥接插件放在同一项目树内，移动整个文件夹不会断链。
const HERE = dirname(fileURLToPath(import.meta.url))
const SKILL_DIR = process.env.DE_AI_FLAVOR_SKILL_DIR || join(HERE, '..', '..')
const SKILL_MD = join(SKILL_DIR, 'SKILL.md')

const DESCRIPTION =
  '中文写作与改写的「去 AI 味」规范：写视频口播稿、产品/课程文案、公众号/小红书、朋友圈、评论回复、通知，' +
  '或把已有文本改得更像真人写的、更口语化，或让 AI 自查文本有没有 AI 腔时使用。' +
  '目标不是堆口语词，而是恢复人类语言的自然损耗（停顿、冗余、不均匀、具体、不完美）。'

function loadContent() {
  if (!existsSync(SKILL_MD)) {
    return `# de-ai-flavor（未找到本地文件）\n\n${SKILL_MD} 不存在，请向用户确认技能目录位置。`
  }
  const body = readFileSync(SKILL_MD, 'utf-8')
  return (
    body +
    `\n\n---\n\n**技能目录**：\`${SKILL_DIR}\`\n` +
    '本目录下有 `references/`（完整词句清单、人话特征库、改写案例）、`research/`（同类项目调研）、' +
    '`scripts/ai_tell_lint.py`（文本体检脚本）。需要时用这个绝对路径读取。\n'
  )
}

export function apply(ctx) {
  try {
    ctx.skills.register({
      name: 'de-ai-flavor',
      source: 'runtime',
      description: DESCRIPTION,
      content: loadContent(),
    })
  } catch (e) {
    console.error('[de-ai-flavor-dsh] skill 注册失败：' + String((e && e.message) || e))
  }
}
