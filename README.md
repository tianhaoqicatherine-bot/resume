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

## 必填输入（格式要求）
配置文件参考：`templates/user-input-template.json`

- `candidate_name`: 字符串，长度 2-30
- `school`: 字符串，长度 2-100
- `onboard_time`: `YYYY.MM` 或 `YYYY-MM`（如 `2026.08`）
- `max_intern_duration`: 如 `6个月` 或 `6月`
- `resume_tex_path`: 绝对路径，且以 `.tex` 结尾
- `company`: 字符串，长度 2-100
- `position`: 字符串，长度 2-100
- `jd_text_or_link`: JD 文本，或以 `http://` / `https://` 开头的链接
- `recipient_email`: 合法邮箱
- `subject_rule`: 可选，长度 <= 200
- `filename_rule`: 默认 `姓名-学校-到岗时间-最长实习时间.pdf`
- `sender_alias`: 可选，若填写需是合法邮箱
- `log_csv_path`: 绝对路径，且以 `.csv` 结尾
- `allow_rewrite`: `true` / `false`
- `auto_send`: `true` / `false`

## 快速开始
1. 准备配置文件（可复制模板并修改）：
   - `templates/user-input-template.json`

2. 执行：
   ```bash
   python3 scripts/resume_delivery.py templates/user-input-template.json
   ```

3. 输出：
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
