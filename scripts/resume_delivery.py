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
    "company", "position", "jd_text_or_link", "recipient_email",
    "filename_rule", "log_csv_path", "allow_rewrite", "auto_send"
]

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ONBOARD_TIME_REGEX = re.compile(r"^\d{4}[.-]\d{2}$")
MAX_DURATION_REGEX = re.compile(r"^\d+\s*(个月|月)$")
URL_REGEX = re.compile(r"^https?://", re.IGNORECASE)
GARBLED_PATTERN = re.compile(r"[�□◇◆◊�]")


def validate_inputs(cfg):
    missing = [k for k in REQUIRED_FIELDS if k not in cfg or cfg[k] in (None, "")]

    source_mode = cfg.get("source_mode", "latest_pdf_in_dir")
    if source_mode == "latest_pdf_in_dir":
        if not cfg.get("source_dir"):
            missing.append("source_dir")
    elif source_mode == "explicit_file":
        if not cfg.get("source_file"):
            missing.append("source_file")
    else:
        missing.append("source_mode")

    if missing:
        return {"missing_fields": sorted(set(missing)), "format_errors": []}

    errors = []

    if not (2 <= len(str(cfg["candidate_name"])) <= 30):
        errors.append("candidate_name length must be 2-30")
    if not (2 <= len(str(cfg["school"])) <= 100):
        errors.append("school length must be 2-100")
    if not ONBOARD_TIME_REGEX.match(str(cfg["onboard_time"])):
        errors.append("onboard_time format must be YYYY.MM or YYYY-MM")
    if not MAX_DURATION_REGEX.match(str(cfg["max_intern_duration"])):
        errors.append("max_intern_duration format must be like 6个月 or 6月")

    if source_mode == "latest_pdf_in_dir":
        source_dir = str(cfg["source_dir"])
        if not os.path.isabs(source_dir):
            errors.append("source_dir must be absolute path")
    if source_mode == "explicit_file":
        source_file = str(cfg["source_file"])
        if not os.path.isabs(source_file):
            errors.append("source_file must be absolute path")
        if not source_file.endswith(".pdf"):
            errors.append("source_file must end with .pdf")

    if not (2 <= len(str(cfg["company"])) <= 100):
        errors.append("company length must be 2-100")
    if not (2 <= len(str(cfg["position"])) <= 100):
        errors.append("position length must be 2-100")

    jd_value = str(cfg["jd_text_or_link"]).strip()
    if jd_value.startswith("http") and not URL_REGEX.match(jd_value):
        errors.append("jd_text_or_link URL must start with http:// or https://")

    if not EMAIL_REGEX.match(str(cfg["recipient_email"])):
        errors.append("recipient_email is invalid")

    subject_rule = cfg.get("subject_rule")
    if subject_rule is not None and len(str(subject_rule)) > 200:
        errors.append("subject_rule length must be <= 200")

    sender_alias = str(cfg.get("sender_alias", "")).strip()
    if sender_alias and not EMAIL_REGEX.match(sender_alias):
        errors.append("sender_alias is invalid")

    log_csv_path = str(cfg["log_csv_path"])
    if not os.path.isabs(log_csv_path):
        errors.append("log_csv_path must be absolute path")
    if not log_csv_path.endswith(".csv"):
        errors.append("log_csv_path must end with .csv")

    if not isinstance(cfg.get("allow_rewrite"), bool):
        errors.append("allow_rewrite must be boolean")
    if not isinstance(cfg.get("auto_send"), bool):
        errors.append("auto_send must be boolean")

    return {"missing_fields": [], "format_errors": errors}


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', '-', name).strip()


def render_filename(cfg):
    filename = cfg.get("filename_rule", "姓名-学校-到岗时间-最长实习时间.pdf")
    filename = filename.replace("姓名", cfg["candidate_name"]) \
        .replace("学校", cfg["school"]) \
        .replace("到岗时间", cfg["onboard_time"]) \
        .replace("最长实习时间", cfg["max_intern_duration"])
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    return safe_filename(filename)


def pick_latest_pdf(source_dir: Path) -> Path:
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"source_dir not found or not a directory: {source_dir}")
    pdfs = [p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdfs:
        raise FileNotFoundError(f"no PDF files found in source_dir: {source_dir}")
    return max(pdfs, key=lambda p: p.stat().st_mtime)


def resolve_source_pdf(cfg):
    source_mode = cfg.get("source_mode", "latest_pdf_in_dir")
    if source_mode == "latest_pdf_in_dir":
        return pick_latest_pdf(Path(cfg["source_dir"]))
    source_file = Path(cfg["source_file"])
    if not source_file.exists():
        raise FileNotFoundError(f"source_file not found: {source_file}")
    return source_file


def detect_possible_garbled_text(file_path: Path):
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        suspicious = GARBLED_PATTERN.findall(text)
        return len(suspicious)
    except Exception:
        return 0


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
    attachment_rel = attachment_path.name
    cmd = [
        "agently-cli", "message", "+send",
        "--to", cfg["recipient_email"],
        "--subject", subject,
        "--body", body,
        "--attachment", attachment_rel
    ]
    if not cfg.get("auto_send", False):
        return {
            "sent": False,
            "reason": "await_user_review",
            "command": " ".join(cmd),
            "attachment_preview_path": str(attachment_path)
        }
    out = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=str(attachment_path.parent))
    return {"sent": True, "output": out.stdout.strip(), "attachment_preview_path": str(attachment_path)}


def append_log(cfg, subject, attachment_path: Path, send_result, source_pdf: Path):
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
        "source_pdf": str(source_pdf),
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

    validation = validate_inputs(cfg)
    if validation["missing_fields"] or validation["format_errors"]:
        print(json.dumps({"ok": False, **validation}, ensure_ascii=False, indent=2))
        sys.exit(2)

    source_pdf = resolve_source_pdf(cfg)

    output_name = render_filename(cfg)
    output_dir = Path(cfg.get("output_dir", str(source_pdf.parent)))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = output_dir / output_name
    shutil.copy2(source_pdf, output_pdf)

    subject, body = generate_mail(cfg)
    send_result = send_mail(cfg, subject, body, output_pdf)
    row_id = append_log(cfg, subject, output_pdf, send_result, source_pdf)
    suspicious_count = detect_possible_garbled_text(source_pdf)

    result = {
        "ok": True,
        "source_pdf_path": str(source_pdf),
        "tailored_pdf_path": str(output_pdf),
        "mail_subject": subject,
        "mail_body": body,
        "send_result": send_result,
        "log_row_id": row_id,
        "review_required": True,
        "review_checklist": [
            "请先打开 PDF 检查是否有乱码、错字、断行异常",
            "请确认附件命名与 JD 要求一致",
            "请确认邮件主题与正文内容无误"
        ],
        "possible_garbled_token_count": suspicious_count
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
