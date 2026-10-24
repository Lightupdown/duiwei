import { readFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

export const inject = ['skills']

// 技能本体与桥接插件放在同一项目树内，移动整个文件夹不会断链。
const HERE = dirname(fileURLToPath(import.meta.url))
const SKILL_DIR = process.env.DE_AI_FLAVOR_SKILL_DIR || join(HERE, '..', '..')
const SKILL_MD = join(SKILL_DIR, 'SKILL.md')

const FALLBACK_DESCRIPTION =
  '中文写作与改写的「去 AI 味」规范：先判文体再改，覆盖作文/文学、公众号/文章、通知/公告、视频口播、朋友圈/聊天、产品/课程文案、报告/总结；' +
  '或让 AI 自查文本有没有 AI 腔时使用。不代写、不帮规避 AI 检测。'

// 从 SKILL.md frontmatter 读 description，避免插件里再维护一份会过期的简介。
function readFrontmatterDescription(body) {
  const m = body.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!m) return ''
  const lines = m[1].split(/\r?\n/)
  const i = lines.findIndex((line) => /^description:/.test(line))
  if (i < 0) return ''
  const first = lines[i].replace(/^description:\s*/, '').trim()
  if (first && first !== '|' && first !== '>') return first.replace(/^["']|["']$/g, '')
  const buf = []
  for (let j = i + 1; j < lines.length; j++) {
    const line = lines[j]
    if (line.trim() === '') continue
    if (/^\s+/.test(line)) {
      buf.push(line.trim())
      continue
    }
    break
  }
  return buf.join(' ')
}

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
    const content = loadContent()
    const parsed = readFrontmatterDescription(content)
    ctx.skills.register({
      name: 'de-ai-flavor',
      source: 'runtime',
      description: parsed || FALLBACK_DESCRIPTION,
      content,
    })
  } catch (e) {
    console.error('[de-ai-flavor-dsh] skill 注册失败：' + String((e && e.message) || e))
  }
}
