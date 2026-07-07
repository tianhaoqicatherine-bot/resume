# resume-auto-delivery

## 适用场景
当用户希望基于 JD 自动完成：
1) 定制化 LaTeX 简历；
2) 按要求命名导出 PDF；
3) 自动生成并发送邮件；
4) 自动记录投递台账。

## 第一步（必须先完成）：收集用户输入
在执行任何自动化步骤前，必须先确认并收集以下信息；任一缺失则停止执行并提示补充。

### 0. 前置条件（必须满足）
- 已在 [agent.qq.com](https://agent.qq.com/) 完成账号注册并可正常登录。
- 已开通 Agent 邮箱，并确认存在可用邮箱别名（`xxx@agent.qq.com`）。
- 本机已安装并可调用 `agently-cli`。
- 已完成 CLI 授权：`agently-cli auth login`。
- 已完成连通性验证：`agently-cli +me` 返回 `ok=true` 且包含可用邮箱别名。

若任一前置条件未满足，必须先完成邮箱注册与 CLI 绑定，再继续后续步骤。

### 通用格式规则（全部字段都要遵守）
- 编码：UTF-8。
- 时间：统一使用绝对日期，避免“下周/尽快/ASAP”这类相对描述。
- 路径：必须是绝对路径（例如 `/Users/xxx/...`），不接受相对路径。
- 布尔值：仅允许 JSON 布尔值 `true` 或 `false`。

### A. 候选人基础信息（必填）
- `candidate_name`：姓名（用于命名），字符串，长度 2-30。
- `school`：学校（用于命名），字符串，长度 2-100。
- `onboard_time`：到岗时间（用于命名），建议格式 `YYYY.MM` 或 `YYYY-MM`（如 `2026.08`）。
- `max_intern_duration`：最长实习时间（用于命名），建议格式 `N个月` 或 `N月`（如 `6个月`）。

### B. 简历源文件（必填）
- `resume_tex_path`：LaTeX 主文件绝对路径（例如 `/abs/path/resume.tex`），必须以 `.tex` 结尾且文件存在。
- 若仅有 PDF，需要先执行“PDF 重建为 LaTeX”步骤，得到可编辑 tex 后再继续。

### C. 目标岗位信息（必填）
- `company`：公司名，字符串，长度 2-100。
- `position`：岗位名，字符串，长度 2-100。
- `jd_text_or_link`：JD 文本或链接；若为链接需以 `http://` 或 `https://` 开头。
- `recipient_email`：投递邮箱，需符合邮箱格式（如 `hr@company.com`）。
- `subject_rule`：邮件标题规则（若 JD 指定），字符串，长度 1-200。
- `filename_rule`：附件命名规则，默认 `姓名-学校-到岗时间-最长实习时间.pdf`。
  - 允许占位符：`姓名`、`学校`、`到岗时间`、`最长实习时间`。
  - 最终文件名非法字符 `\\ / : * ? " < > |` 会自动替换为 `-`。

### D. 发信与记录配置（必填）
- `sender_alias`：发件邮箱别名（默认主别名），需符合邮箱格式（如 `xxx@agent.qq.com`）。
- `log_csv_path`：投递记录 CSV 绝对路径（例如 `/abs/path/data/applications.csv`），必须以 `.csv` 结尾。

### E. 用户确认项（必填）
- 是否允许 AI 根据 JD 改写简历措辞（仅优化表达，不得虚构经历）：`allow_rewrite=true/false`
- 是否自动发送（否则先生成草稿并等待确认）：`auto_send=true/false`

## 执行流程
1. 校验第 1 步输入完整性。
2. 从 JD 提取关键词与要求。
3. 基于关键词生成岗位版 LaTeX（不虚构信息）。
4. 编译 PDF（tectonic）。
5. 根据命名规则重命名导出附件。
6. 生成邮件主题与正文。
7. 使用 `agently-cli message +send` 发送（若 `auto_send=false` 则只输出命令与草稿）。
8. 将投递信息写入 CSV 台账。

## 输出产物
- `tailored_tex_path`
- `tailored_pdf_path`
- `mail_subject`
- `mail_body`
- `send_result`
- `log_row_id`

## 失败处理
- 编译失败：返回 TeX 错误日志并停止发送。
- 邮件发送失败：记录失败状态到 CSV，并输出可重试命令。
- 任何必填输入缺失：返回缺失字段列表，不执行后续步骤。
