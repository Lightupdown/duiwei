# 隐私事件与清除请求（维护者必读）

## 发生了什么

早期提交曾包含考试作文的学生姓名（含一名未成年人）。这些姓名已从当前工作树删除，`main` 历史也已重写；但 **GitHub 仍可能通过旧提交 SHA、缓存页面或 API 展示旧提交**。仅重写历史不能清除 GitHub 侧缓存。

## 需要维护者操作（代码解决不了）

1. **临时降低暴露面**：在清除完成前，可把仓库设为 private（Settings → General → Danger Zone → Change visibility）。
2. **联系 GitHub Support**：打开 https://support.github.com/contact ，选择 *Repository* → *Removing sensitive data*（或直接说明 "request removal of cached views and unreachable commits"）。
3. **工单里提供**：
   - 仓库：`https://github.com/Lightupdown/duiwei`
   - 旧提交哈希（向维护者索取；不要写进公开文件）
   - 涉及文件：`samples/external/*.md`
   - 说明：包含学生实名，其中一名为未成年人；已从当前版本删除并重写分支；请求清除缓存视图和无引用提交（unreachable commits）。
4. **模板（英文）**：

   > Subject: Request removal of sensitive data (student names) from cached/unreachable commits
   >
   > Hello GitHub Support,
   >
   > In the repository `<repo URL>`, an earlier commit `<SHA>` contains the real names of students, including a minor. I have removed the names from the current tree and rewritten the branch history, but the old commit may still be accessible via its SHA or cached views.
   >
   > Please remove the cached views and unreachable commits containing this data, per GitHub's "Removing sensitive data from a repository" guidance. I understand forks and clones outside this repository cannot be removed.
   >
   > Thank you.

5. **无法远程删除的**：任何人已经 fork 或 clone 的副本。只能接受，或逐一联系对方删除。

## 以后

- 外部样本只保留来源、期号、公开机构；不写学生姓名、学校、联系方式。
- 收真实稿件时，先脱敏再入库。
