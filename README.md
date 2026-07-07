# Resume Auto Delivery

基于 AI + LaTeX + Agent Mail 的自动化投递工具：
- 解析 JD
- 生成/编译岗位版简历
- 按规则命名附件
- 自动发送邮件
- 自动记录投递台账

## 前置条件（必须满足）
1. 已在 [agent.qq.com](https://agent.qq.com/) 注册账号并可登录。
2. 已开通 Agent 邮箱并确认可用别名（`xxx@agent.qq.com`）。
3. 本机已安装并可调用 `agently-cli`。
4. 已完成 CLI 授权：
   ```bash
   agently-cli auth login
   ```
5. 已完成连通性验证（返回 `ok=true` 且含邮箱别名）：
   ```bash
   agently-cli +me
   ```
6. 已安装 `tectonic`（用于 LaTeX 编译）：
   ```bash
   brew install tectonic
   ```

## 你需要先准备什么（先看这个）
配置文件参考：`templates/user-input-template.json`

### 1) 简历文件来源（必填，二选一）
- 方式 A（推荐）：固定文件夹自动取最新 PDF
  - `source_mode`: `latest_pdf_in_dir`
  - `source_dir`: 简历文件夹绝对路径（例如 `/Users/xxx/resume`）
- 方式 B：手动指定某个 PDF
  - `source_mode`: `explicit_file`
  - `source_file`: 简历 PDF 绝对路径（例如 `/Users/xxx/resume/CV.pdf`）

### 2) 投递信息（必填）
- `candidate_name`: 姓名（如 `桃子`）
- `school`: 学校/学校年级（如 `浙江大学大一`）
- `onboard_time`: `YYYY.MM` 或 `YYYY-MM`（如 `2026.08`）
- `max_intern_duration`: 如 `6个月` 或 `6月`
- `company`: 公司名（如 `阿里巴巴国际电商集团`）
- `position`: 岗位名（如 `战略部实习生`）
- `jd_text_or_link`: JD 文本，或以 `http://` / `https://` 开头的链接
- `recipient_email`: 投递邮箱（合法邮箱）
- `filename_rule`: 附件命名规则（默认 `姓名-学校-到岗时间-最长实习时间.pdf`）
- `subject_rule`: 邮件标题规则（可选，长度 <= 200）
- `log_csv_path`: 投递记录 CSV 绝对路径（以 `.csv` 结尾）
- `allow_rewrite`: `true` / `false`
- `auto_send`: `true` / `false`

### 3) 可选信息
- `sender_alias`: 发件别名（若填写需为合法邮箱）

## 快速开始
1. 准备配置文件（可复制模板并修改）：
   - `templates/user-input-template.json`

2. 执行：
   ```bash
   python3 scripts/resume_delivery.py templates/user-input-template.json
   ```

> 默认建议将 `auto_send` 设为 `false`，先人工预览 PDF。

3. 发送前人工确认（必须）
- 打开生成的 PDF 检查：乱码、断行、错字、命名。
- 确认邮件主题与正文。
- 确认无误后再执行发送命令（脚本输出中会提供）。

4. 输出：
   - 编译后的 PDF（按 `filename_rule` 命名）
   - 邮件主题与正文
   - 发送结果（或草稿命令）
   - 台账记录（CSV）

## 目录说明
- `skills/resume-auto-delivery/SKILL.md`: Skill 说明与流程
- `scripts/resume_delivery.py`: 主执行脚本
- `templates/user-input-template.json`: 输入模板
- `data/applications.csv`: 投递台账
- `resume/resume.tex`: 简历 LaTeX 源
- `resume/resume.pdf`: 简历编译产物
