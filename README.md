# Resume Auto Delivery

一个用于“简历 PDF 自动命名 + 邮件投递 + 台账记录”的工具。

## 适用人群
- 不懂代码也可以使用
- 希望减少重复投递操作
- 需要记录“投递了什么、投递给谁、什么时候投递”

## 0. 下载到哪里？
建议放在本地目录：
- `/Users/<你的用户名>/Documents/webagent`

如果还没下载仓库：
```bash
git clone <你的仓库地址> /Users/<你的用户名>/Documents/webagent
cd /Users/<你的用户名>/Documents/webagent
```

## 1. 安装依赖（只需一次）
```bash
npm install -g @tencent-qqmail/agently-cli
```

## 2. 绑定 Agent 邮箱（只需一次）
1) 在 [agent.qq.com](https://agent.qq.com/) 注册并开通邮箱。  
2) 终端执行：
```bash
agently-cli auth login
agently-cli +me
```
看到 `ok: true` 且有 `xxx@agent.qq.com` 就表示成功。

## 3. 放入简历 PDF
把简历 PDF 放到：
- `/Users/<你的用户名>/Documents/webagent/resume`

文件名可以随意（例如 `cv.pdf`、`我的简历.pdf`）。

## 4. 填写配置文件
复制模板并填写：
- 模板文件：`templates/user-input-template.json`

### 必填信息（人话版）
- 简历来源（二选一）：
  - `source_mode = latest_pdf_in_dir` + `source_dir`（推荐，自动选最新 PDF）
  - `source_mode = explicit_file` + `source_file`（手动指定某个 PDF）
- 求职信息：`candidate_name`、`school`、`company`、`position`
- 投递目标：`recipient_email`、`jd_text_or_link`
- 命名规则：`filename_rule`
- 台账位置：`log_csv_path`
- 是否自动发：`auto_send`（建议先 `false`）

## 5. 运行
```bash
python3 scripts/resume_delivery.py templates/user-input-template.json
```

## 6. 结果在哪看？
- 重命名后的简历：默认在 `resume` 目录
- 投递记录台账：`data/applications.csv`

## 投递记录包含哪些字段？
- `company`（公司）
- `delivery_time`（投递时间）
- `resume_filename`（使用的简历文件名）
- `jd_text_or_link`（JD 文本或链接）
- `position`（岗位名称）
- `base_city`（base 地，如果有）
- 以及收件人、主题、状态等辅助字段

## 常见问题
### Q1: 报错 `agently-cli: command not found`
先执行：
```bash
npm install -g @tencent-qqmail/agently-cli
```

### Q2: 报错附件路径不安全
请确保附件传的是相对路径（脚本已内置处理）。

### Q3: 我不想自动发邮件
把配置中的 `auto_send` 设为 `false`，先检查 PDF 和邮件内容。

### Q4: 简历文件名经常变怎么办？
使用：
- `source_mode = latest_pdf_in_dir`
- `source_dir = 你的简历目录`
脚本会自动取最新 PDF。
