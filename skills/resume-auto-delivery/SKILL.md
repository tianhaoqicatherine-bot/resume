# resume-auto-delivery

## 适用场景
当用户希望基于 JD 自动完成：
1) 定制化 LaTeX 简历；
2) 按要求命名导出 PDF；
3) 自动生成并发送邮件；
4) 自动记录投递台账。

## 第一步（必须先完成）：收集用户输入
在执行任何自动化步骤前，必须先确认并收集以下信息；任一缺失则停止执行并提示补充。

### A. 候选人基础信息（必填）
- `candidate_name`：姓名（用于命名）
- `school`：学校（用于命名）
- `onboard_time`：到岗时间（用于命名）
- `max_intern_duration`：最长实习时间（用于命名）

### B. 简历源文件（必填）
- `resume_tex_path`：LaTeX 主文件绝对路径（例如 `/abs/path/resume.tex`）
- 若仅有 PDF，需要先执行“PDF 重建为 LaTeX”步骤，得到可编辑 tex 后再继续。

### C. 目标岗位信息（必填）
- `company`：公司名
- `position`：岗位名
- `jd_text_or_link`：JD 文本或链接
- `recipient_email`：投递邮箱
- `subject_rule`：邮件标题规则（若 JD 指定）
- `filename_rule`：附件命名规则（默认 `姓名-学校-到岗时间-最长实习时间.pdf`）

### D. 发信与记录配置（必填）
- `sender_alias`：发件邮箱别名（默认主别名）
- `log_csv_path`：投递记录 CSV 路径（例如 `/abs/path/data/applications.csv`）

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
