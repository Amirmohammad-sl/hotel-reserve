#!/usr/bin/env python3
"""
scripts/build_report.py — Assemble the Final Course Report
Course: Web Programming (دانشگاه تهران / درس برنامه‌نویسی وب)
Project: Hotel Reservation & Management System (سامانه رزرواسیون هتل)
Operators: Operator A (Amirmohammad Soleimani) & Operator B (Mahdi Moradi)

This script aggregates all individual report markdown sections in docs/report/:
  1. overall-diagram.md
  2. process-per-app.md
  3. models.md
  4. managers.md
  5. views.md
  6. testing.md
  7. bonuses.md

Outputs:
  - docs/report/FINAL_REPORT.md   (Single unified GitHub-flavored Markdown file)
  - docs/report/FINAL_REPORT.html (Standalone print-ready RTL HTML file with Mermaid & Vazirmatn font)
"""

import os
import re
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "docs" / "report"

SECTIONS = [
    ("overall-diagram.md", "۱. معماری کلان و دیاگرام‌های سیستم"),
    ("process-per-app.md", "۲. جریان فرایندها به تفکیک وب‌اپلیکیشن"),
    ("models.md", "۳. مدل‌های داده و ساختار پایگاه داده"),
    ("managers.md", "۴. معرفی Managerها و QuerySetهای سفارشی"),
    ("views.md", "۵. معرفی Viewها و وب‌سرویس‌های سامانه"),
    ("testing.md", "۶. استراتژی آزمون‌ها و راهنمای اجرا"),
    ("bonuses.md", "۷. قابلیت‌های امتیازی و توسعه‌های پیشرفته"),
]

HEADER_MD = """# گزارش نهایی و مستندات فنی سامانه رزرواسیون هتل
> **پروژه پایانی درس برنامه‌نویسی وب**  
> **سامانه جامع جستجو، مدیریت و رزرواسیون هتل** (Hotel Booking & Management System)  
> **نیم‌سال تحصیلی:** پاییز ۱۴۰۳ (۲۰۲۶)  
> **توسعه‌دهندگان (تیم دونفره):**  
> - **اپراتور A:** امیرمحمد سلیمانی (`Amirmohammad-sl`) — امضا: `amirmohammad.slmni@gmail.com`  
> - **اپراتور B:** مهدی مرادی (`mahdimoradi-tech`) — امضا: `mahdimoradi.tech@gmail.com`  
> **مخاطبان:** استاد محترم درس، سرکار خانم دکتر سلطانی و دستیاران آموزشی  
> **مخزن گیت‌هاب:** [https://github.com/Amirmohammad-sl/hotel-reserve](https://github.com/Amirmohammad-sl/hotel-reserve)

---

## شناسنامه فنی پروژه

| مؤلفه سیستم | فناوری و نسخه انتخابی | توضیحات معماری |
|---|---|---|
| **Backend Framework** | Python 3.12 + Django 5.1.x | استفاده از Plain Django Views و Django Forms بدون DRF طبق ضوابط درس |
| **Database** | PostgreSQL 16+ | اعتبارسنجی سطح دیتابیس (`CheckConstraint`)، کلیدهای خارجی با کنترل دقیق یکپارچگی |
| **Frontend Framework** | React 19 + Vite 6 + Tailwind CSS 4 | تک‌صفحه‌ای (SPA) کاملاً RTL با فونت وزیرمتن و طراحی ریسپانسیو |
| **Authentication** | Django Session Auth + CSRF Cookies | نشست‌های امن سرور بر بستر کوکی `HttpOnly`، پشتیبانی از `remember_me` و توکن امنیتی CSRF |
| **Testing Suite** | Django Test Runner + Coverage.py + Node Smoke | **۳۱۳ تست خودکار** (۲۹۹ تست یکپارچه بک‌اند + ۱۴ تست رابط کاربری فرانت‌اند) با پوشش بالای ۸۰٪ |
| **Logging & Audit** | Python Standard Logging (`backend/logs/`) | سه کانال تفکیک‌شده: لاگ ساختاریافته درخواست‌ها (`app.log`)، رویدادهای امنیتی (`security.log`) و خطاها (`error.log`) |

---

## فهرست مندرجات گزارش
- [بخش ۱: معماری کلان و دیاگرام‌های سیستم](#۱-معماری-کلان-و-دیاگرامهای-سیستم)
- [بخش ۲: جریان فرایندها به تفکیک وب‌اپلیکیشن](#۲-جریان-فرایندها-به-تفکیک-وباپلیکیشن)
- [بخش ۳: مدل‌های داده و ساختار پایگاه داده](#۳-مدلهای-داده-و-ساختار-پایگاه-داده)
- [بخش ۴: معرفی Managerها و QuerySetهای سفارشی](#۴-معرفی-managerها-و-querysetهای-سفارشی)
- [بخش ۵: معرفی Viewها و وب‌سرویس‌های سامانه](#۵-معرفی-viewها-و-وبسرویسهای-سامانه)
- [بخش ۶: استراتژی آزمون‌ها و راهنمای اجرا](#۶-استراتژی-آزمونها-و-راهنمای-اجرا)
- [بخش ۷: قابلیت‌های امتیازی و توسعه‌های پیشرفته](#۷-قابلیتهای-امتیازی-و-توسعههای-پیشرفته)

---
"""


def build_markdown_report() -> str:
    """Combines all sections into a unified markdown text."""
    parts = [HEADER_MD]
    for filename, title in SECTIONS:
        file_path = REPORT_DIR / filename
        if not file_path.exists():
            print(f"[WARN] Section file not found: {file_path}")
            continue
        content = file_path.read_text(encoding="utf-8").strip()
        parts.append(f"\n\n<!-- SECTION BREAK: {filename} -->\n\n")
        parts.append(content)
        parts.append("\n\n---\n")
    return "\n".join(parts)


def markdown_to_html(md_text: str) -> str:
    """
    Converts markdown text to HTML with support for:
      - Headings (h1..h6)
      - Code blocks (including mermaid diagrams)
      - Tables
      - Blockquotes
      - Unordered and ordered lists
      - Links, bold, inline code, italics
      - Horizontal rules
    """
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_table = False
    table_lines = []
    in_ul = False
    in_ol = False
    in_blockquote = False

    def close_lists():
        nonlocal in_ul, in_ol
        res = []
        if in_ul:
            res.append("</ul>")
            in_ul = False
        if in_ol:
            res.append("</ol>")
            in_ol = False
        return res

    def close_blockquote():
        nonlocal in_blockquote
        res = []
        if in_blockquote:
            res.append("</blockquote>")
            in_blockquote = False
        return res

    def render_table(tbl_lines):
        if len(tbl_lines) < 2:
            return "".join(tbl_lines)
        out = ['<div class="table-container"><table>']
        # header
        headers = [c.strip() for c in tbl_lines[0].strip().strip("|").split("|")]
        out.append("<thead><tr>")
        for h in headers:
            out.append(f"<th>{inline_format(h)}</th>")
        out.append("</tr></thead><tbody>")

        # skip separator line if present
        data_rows = tbl_lines[2:] if len(tbl_lines) > 2 and re.match(r"^\|?\s*[-:]+[-| :]*\s*\|?$", tbl_lines[1]) else tbl_lines[1:]
        for row in data_rows:
            if not row.strip():
                continue
            cols = [c.strip() for c in row.strip().strip("|").split("|")]
            out.append("<tr>")
            for c in cols:
                out.append(f"<td>{inline_format(c)}</td>")
            out.append("</tr>")
        out.append("</tbody></table></div>")
        return "\n".join(out)

    def inline_format(text: str) -> str:
        # Protect escaped chars or existing entities
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Inline code `code`
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        # Bold **text**
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        # Italic *text*
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        # Markdown links [text](url)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block toggle
        if line.strip().startswith("```"):
            if not in_code_block:
                html_lines.extend(close_lists())
                html_lines.extend(close_blockquote())
                if in_table:
                    html_lines.append(render_table(table_lines))
                    table_lines = []
                    in_table = False
                in_code_block = True
                code_lang = line.strip().lstrip("`").strip().lower()
                code_lines = []
            else:
                in_code_block = False
                code_content = html.escape("\n".join(code_lines))
                if code_lang == "mermaid":
                    html_lines.append(f'<div class="mermaid">\n{chr(10).join(code_lines)}\n</div>')
                else:
                    lang_class = f" class=\"language-{code_lang}\"" if code_lang else ""
                    html_lines.append(f'<pre><code{lang_class}>{code_content}</code></pre>')
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Tables
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            html_lines.extend(close_lists())
            html_lines.extend(close_blockquote())
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
            i += 1
            continue
        elif in_table:
            html_lines.append(render_table(table_lines))
            table_lines = []
            in_table = False

        # Blockquote
        if line.startswith(">"):
            html_lines.extend(close_lists())
            b_text = line.lstrip("> ").strip()
            if not in_blockquote:
                in_blockquote = True
                html_lines.append("<blockquote>")
            html_lines.append(f"<p>{inline_format(b_text)}</p>")
            i += 1
            continue
        elif in_blockquote:
            html_lines.extend(close_blockquote())

        # Horizontal rules
        if re.match(r"^\s*([*\-_])\s*(\1\s*){2,}\s*$", line):
            html_lines.extend(close_lists())
            html_lines.append("<hr>")
            i += 1
            continue

        # Headings
        header_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if header_match:
            html_lines.extend(close_lists())
            level = len(header_match.group(1))
            h_text = header_match.group(2).strip()
            # Generate id for anchors
            clean_id = re.sub(r"[^\w\u0600-\u06FF\- ]", "", h_text).strip().replace(" ", "-").lower()
            html_lines.append(f'<h{level} id="{clean_id}">{inline_format(h_text)}</h{level}>')
            i += 1
            continue

        # Lists (Unordered)
        ul_match = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if ul_match:
            if in_ol:
                html_lines.extend(close_lists())
            if not in_ul:
                in_ul = True
                html_lines.append("<ul>")
            item_text = ul_match.group(1).strip()
            # Support task lists [ ] and [x]
            if item_text.startswith("[ ] "):
                item_text = '<input type="checkbox" disabled> ' + item_text[4:]
            elif item_text.startswith("[x] ") or item_text.startswith("[X] "):
                item_text = '<input type="checkbox" checked disabled> ' + item_text[4:]
            html_lines.append(f"<li>{inline_format(item_text)}</li>")
            i += 1
            continue

        # Lists (Ordered)
        ol_match = re.match(r"^\s*\d+[\.\)]\s+(.*)$", line)
        if ol_match:
            if in_ul:
                html_lines.extend(close_lists())
            if not in_ol:
                in_ol = True
                html_lines.append("<ol>")
            html_lines.append(f"<li>{inline_format(ol_match.group(1).strip())}</li>")
            i += 1
            continue

        # If not a list, close open lists
        html_lines.extend(close_lists())

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Regular paragraph
        html_lines.append(f"<p>{inline_format(line.strip())}</p>")
        i += 1

    # Close any trailing open tags
    html_lines.extend(close_lists())
    html_lines.extend(close_blockquote())
    if in_table:
        html_lines.append(render_table(table_lines))

    return "\n".join(html_lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>گزارش نهایی پروژه درس برنامه‌نویسی وب — سامانه رزرواسیون هتل</title>
  <!-- Vazirmatn Font CDN -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
  <style>
    :root {
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --accent: #0284c7;
      --bg-body: #f8fafc;
      --bg-card: #ffffff;
      --text-main: #0f172a;
      --text-muted: #475569;
      --border: #e2e8f0;
      --code-bg: #0f172a;
      --code-fg: #f8fafc;
      --tag-bg: #eff6ff;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg-body);
      color: var(--text-main);
      line-height: 1.8;
      font-size: 15px;
      direction: rtl;
    }

    .container {
      max-width: 1050px;
      margin: 0 auto;
      padding: 40px 24px;
      background-color: var(--bg-card);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
      border-radius: 12px;
      margin-top: 30px;
      margin-bottom: 50px;
    }

    .no-print-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
      color: #ffffff;
      padding: 14px 24px;
      border-radius: 8px;
      margin-bottom: 30px;
      box-shadow: 0 2px 10px rgba(30, 58, 138, 0.2);
    }

    .no-print-bar h3 {
      font-size: 16px;
      font-weight: 600;
    }

    .print-btn {
      background-color: #ffffff;
      color: var(--primary);
      border: none;
      padding: 8px 18px;
      border-radius: 6px;
      font-family: inherit;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .print-btn:hover {
      background-color: #f1f5f9;
      transform: translateY(-1px);
    }

    h1, h2, h3, h4, h5, h6 {
      color: var(--primary);
      font-weight: 700;
      margin-top: 1.6em;
      margin-bottom: 0.6em;
      line-height: 1.4;
    }

    h1 {
      font-size: 26px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 12px;
      margin-top: 1.2em;
    }

    h2 {
      font-size: 21px;
      border-right: 4px solid var(--primary-light);
      padding-right: 12px;
      background-color: var(--tag-bg);
      padding-top: 6px;
      padding-bottom: 6px;
      border-radius: 0 6px 6px 0;
    }

    h3 {
      font-size: 18px;
      color: #1e293b;
    }

    h4 {
      font-size: 16px;
      color: #334155;
    }

    p {
      margin-bottom: 14px;
      text-align: justify;
      color: #334155;
    }

    a {
      color: var(--primary-light);
      text-decoration: none;
      font-weight: 500;
    }

    a:hover {
      text-decoration: underline;
    }

    hr {
      border: 0;
      height: 1px;
      background: var(--border);
      margin: 36px 0;
    }

    blockquote {
      border-right: 4px solid var(--primary-light);
      padding: 14px 20px;
      background-color: #f8fafc;
      color: var(--text-muted);
      border-radius: 0 8px 8px 0;
      margin: 18px 0;
      font-size: 14.5px;
    }

    blockquote p {
      margin-bottom: 6px;
    }

    blockquote p:last-child {
      margin-bottom: 0;
    }

    ul, ol {
      margin: 14px 28px 18px 0;
    }

    li {
      margin-bottom: 6px;
      color: #334155;
    }

    li input[type="checkbox"] {
      margin-left: 8px;
      vertical-align: middle;
    }

    .table-container {
      overflow-x: auto;
      margin: 20px 0;
      border-radius: 8px;
      border: 1px solid var(--border);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: right;
      font-size: 14px;
    }

    th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
      padding: 12px 14px;
      border-bottom: 2px solid var(--border);
      white-space: nowrap;
    }

    td {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      color: #334155;
    }

    tr:nth-child(even) {
      background-color: #f8fafc;
    }

    tr:hover {
      background-color: #eff6ff;
    }

    code {
      font-family: Consolas, 'Courier New', monospace;
      direction: ltr;
      display: inline-block;
      background-color: #f1f5f9;
      color: #be185d;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 13.5px;
    }

    pre {
      background-color: var(--code-bg);
      color: var(--code-fg);
      padding: 16px 20px;
      border-radius: 8px;
      overflow-x: auto;
      direction: ltr;
      text-align: left;
      margin: 18px 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    pre code {
      background-color: transparent;
      color: #e2e8f0;
      padding: 0;
      border-radius: 0;
      font-size: 13px;
      line-height: 1.6;
    }

    .mermaid {
      background-color: #ffffff;
      padding: 20px;
      border-radius: 8px;
      border: 1px solid var(--border);
      margin: 24px 0;
      text-align: center;
      direction: ltr;
      overflow-x: auto;
    }

    @media print {
      body {
        background-color: #ffffff;
        font-size: 12pt;
      }

      .container {
        max-width: 100%;
        margin: 0;
        padding: 0;
        box-shadow: none;
        border-radius: 0;
      }

      .no-print-bar {
        display: none !important;
      }

      h1, h2 {
        page-break-before: always;
      }

      pre, blockquote, .table-container, .mermaid {
        page-break-inside: avoid;
      }

      a {
        color: #000000;
        text-decoration: none;
      }
    }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function () {
      mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Vazirmatn, sans-serif'
      });
    });
  </script>
</head>
<body>
  <div class="container">
    <div class="no-print-bar">
      <div>
        <h3>سامانه رزرواسیون هتل — نسخه نهایی گزارش پروژه</h3>
        <p style="margin: 0; color: #e0e7ff; font-size: 13px;">طراحی‌شده جهت ارائه به استاد و ذخیره به عنوان PDF رسمی (A4 RTL)</p>
      </div>
      <button class="print-btn" onclick="window.print()">🖨️ چاپ / ذخیره به عنوان PDF</button>
    </div>

    <!-- DOCUMENT CONTENT -->
    {{CONTENT}}
  </div>
</body>
</html>
"""


def main():
    print("[1/3] Assembling markdown sections into FINAL_REPORT.md...")
    md_content = build_markdown_report()
    md_out_path = REPORT_DIR / "FINAL_REPORT.md"
    md_out_path.write_text(md_content, encoding="utf-8")
    print(f" -> Generated: {md_out_path} ({len(md_content.encode('utf-8'))} bytes)")

    print("[2/3] Rendering standalone print-ready HTML with Mermaid & Vazirmatn...")
    body_html = markdown_to_html(md_content)
    full_html = HTML_TEMPLATE.replace("{{CONTENT}}", body_html)
    html_out_path = REPORT_DIR / "FINAL_REPORT.html"
    html_out_path.write_text(full_html, encoding="utf-8")
    print(f" -> Generated: {html_out_path} ({len(full_html.encode('utf-8'))} bytes)")

    print("[3/3] Report build completed successfully!")


if __name__ == "__main__":
    main()
