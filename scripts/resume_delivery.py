#!/usr/bin/env python3
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = [
    "candidate_name", "school", "onboard_time", "max_intern_duration",
    "resume_tex_path", "company", "position", "jd_text_or_link",
    "recipient_email", "filename_rule", "log_csv_path", "allow_rewrite", "auto_send"
]

def validate_inputs(cfg):
    missing = [k for k in REQUIRED_FIELDS if k not in cfg or cfg[k] in (None, "")]
    return missing

def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', '-', name).strip()

def render_filename(cfg):
    filename = cfg.get("filename_rule", "姓名-学校-到岗时间-最长实习时间.pdf")
    filename = filename.replace("姓名", cfg["candidate_name"])\
                       .replace("学校", cfg["school"])\
                       .replace("到岗时间", cfg["onboard_time"])\
                       .replace("最长实习时间", cfg["max_intern_duration"])
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    return safe_filename(filename)

def compile_pdf(tex_path: Path):
    cwd = tex_path.parent
    cmd = ["tectonic", tex_path.name]
    subprocess.run(cmd, cwd=cwd, check=True)
    pdf = cwd / (tex_path.stem + ".pdf")
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found after compile: {pdf}")
    return pdf

def generate_mail(cfg):
    subject = cfg.get("subject_rule") or f"应聘-{cfg['candidate_name']}-{cfg['position']}"
    body = (
        f"您好，\n\n"
        f"我是{cfg['candidate_name']}，来自{cfg['school']}。\n"
        f"现申请贵司{cfg['position']}岗位，附件为我的简历。\n"
        f"我可在{cfg['onboard_time']}到岗，最长可实习{cfg['max_intern_duration']}。\n\n"
        f"感谢您的时间与考虑！\n"
        f"{cfg['candidate_name']}"
    )
    return subject, body

def send_mail(cfg, subject, body, attachment_path: Path):
    cmd = [
        "agently-cli", "message", "+send",
        "--to", cfg["recipient_email"],
        "--subject", subject,
        "--body", body,
        "--attachment", str(attachment_path)
    ]
    if not cfg.get("auto_send", False):
        return {"sent": False, "command": " ".join(cmd)}
    out = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return {"sent": True, "output": out.stdout.strip()}

def append_log(cfg, subject, attachment_path: Path, send_result):
    log_path = Path(cfg["log_csv_path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    exists = log_path.exists()
    row_id = datetime.now().strftime("%Y%m%d%H%M%S")
    row = {
        "row_id": row_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "company": cfg["company"],
        "position": cfg["position"],
        "recipient_email": cfg["recipient_email"],
        "candidate_name": cfg["candidate_name"],
        "attachment": str(attachment_path),
        "subject": subject,
        "status": "sent" if send_result.get("sent") else "draft",
    }
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)
    return row_id

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/resume_delivery.py <config.json>")
        sys.exit(1)

    cfg_path = Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    missing = validate_inputs(cfg)
    if missing:
        print(json.dumps({"ok": False, "missing_fields": missing}, ensure_ascii=False, indent=2))
        sys.exit(2)

    tex_path = Path(cfg["resume_tex_path"])
    if not tex_path.exists():
        raise FileNotFoundError(f"resume_tex_path not found: {tex_path}")

    built_pdf = compile_pdf(tex_path)
    output_name = render_filename(cfg)
    output_pdf = tex_path.parent / output_name
    shutil.copy2(built_pdf, output_pdf)

    subject, body = generate_mail(cfg)
    send_result = send_mail(cfg, subject, body, output_pdf)
    row_id = append_log(cfg, subject, output_pdf, send_result)

    result = {
        "ok": True,
        "tailored_tex_path": str(tex_path),
        "tailored_pdf_path": str(output_pdf),
        "mail_subject": subject,
        "mail_body": body,
        "send_result": send_result,
        "log_row_id": row_id
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
