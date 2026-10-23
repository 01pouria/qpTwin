# راهنمای اتصال qpTwin به کلاینت‌های MCP

این راهنما نحوه تولید و استفاده از پروفایل‌های اتصال qpTwin Community v0.4.0 را توضیح می‌دهد. qpTwin از طریق STDIO اجرا می‌شود و یک Workspace مشخص را در اختیار ابزارهای تحلیل معماری و ریسک تغییر قرار می‌دهد.

## پیش‌نیازها

- Python 3.11 یا جدیدتر
- نصب qpTwin در یک Virtual Environment
- مسیر مطلق مخزنی که مجاز به تحلیل آن هستید
- کلاینتی با پشتیبانی از MCP و Transport نوع STDIO

```bash
git clone https://github.com/01pouria/qpTwin.git
cd qpTwin
python -m venv .venv
python -m pip install -e .
```

## تولید پروفایل‌ها

```bash
python scripts/generate_qptwin_configs.py \
  --workspace /absolute/path/to/repository \
  --python /absolute/path/to/.venv/bin/python \
  --output ./connection-presets
```

این فرمان ۱۲ پروفایل مستقل تولید می‌کند و هیچ فایل تنظیمات فعالی را تغییر نمی‌دهد. مسیر Python و Workspace در خروجی به‌صورت مطلق ثبت می‌شوند؛ بنابراین پوشه خروجی مخصوص همان سیستم است و نباید در Git commit شود.

## کلاینت‌های پشتیبانی‌شده

| کلاینت | فایل تولیدشده | ساختار |
|---|---|---|
| Cursor | `configs/cursor/.cursor/mcp.json` | `mcpServers` |
| Codex | `configs/codex/.codex/config.toml` | TOML `mcp_servers` |
| Antigravity | `configs/antigravity/.agents/mcp_config.json` | `mcpServers` |
| Claude Code | `configs/claude-code/.mcp.json` | `mcpServers` |
| Hermes Agent | `configs/hermes/config-snippet.yaml` | قطعه YAML |
| OpenClaw | `configs/openclaw/mcp-snippet.json` | قطعه `mcp.servers` |
| OpenCode | `configs/opencode/opencode.json` | آرایه Command و Environment |
| Gemini CLI | `configs/gemini-cli/.gemini/settings.json` | `mcpServers` |
| Windsurf | `configs/windsurf/mcp_config.json` | `mcpServers` |
| Cline | `configs/cline/cline_mcp_settings.json` | `mcpServers` |
| Roo Code | `configs/roo-code/.roo/mcp.json` | `mcpServers` |
| VS Code | `configs/vscode/.vscode/mcp.json` | `servers` |

پروفایل‌های Hermes Agent و OpenClaw قطعه تنظیمات هستند و باید با فایل موجود ادغام شوند. برای سایر کلاینت‌ها نیز پیش از جایگزینی فایل، تنظیمات فعلی را بررسی و Backup تهیه کنید.

## حالت‌های اجرا

### سرور STDIO داخلی

حالت پیش‌فرض و بدون dependency خارجی:

```bash
python -m twindev_mcp.offline_stdio
```

### Adapter مبتنی بر SDK رسمی MCP

```bash
python -m pip install -e '.[mcp]'
python -m twindev_mcp.server
```

در هر دو حالت، متغیر `TWINDEV_WORKSPACE` باید به یک Directory موجود و مورداعتماد اشاره کند. نام این متغیر و ماژول `twindev_mcp` برای سازگاری نسخه‌های قبلی حفظ شده است.

## بررسی اتصال

پس از افزودن تنظیمات به کلاینت:

1. کلاینت را Restart یا MCP Server را Reload کنید.
2. وجود سرور `qptwin` و فهرست ابزارها را بررسی کنید.
3. ابتدا `workspace_overview` را اجرا کنید.
4. سپس `discover_architecture` و `twindev_help` را برای شناخت Workspace فراخوانی کنید.
5. پیش از تحلیل پروژه اصلی، اتصال را روی یک مخزن آزمایشی بررسی کنید.

## اصول امنیتی

- Workspace باید صریح، موجود و مورداعتماد باشد.
- qpTwin را با دسترسی Administrator یا Root اجرا نکنید.
- فایل تنظیمات تولیدشده را commit نکنید؛ این فایل شامل مسیرهای محلی است.
- دسترسی MCP Client به Toolها و داده‌های بازگشتی را متناسب با سیاست سازمان تنظیم کنید.
- ابزار `save_architecture_snapshot` با درخواست صریح، فراداده معماری را در `.twindev/` ذخیره می‌کند؛ سایر ابزارهای qpTwin Community سورس برنامه را تغییر نمی‌دهند.
- برای محیط‌های سازمانی، اجرای ایزوله، کنترل هویت، Audit و سیاست نگهداری داده را در معماری استقرار لحاظ کنید.

## رفع اشکال

- **سرور نمایش داده نمی‌شود:** مسیر Python و نام فایل تنظیمات کلاینت را بررسی کنید.
- **Workspace پیدا نمی‌شود:** از مسیر مطلق استفاده کنید و وجود Directory را کنترل کنید.
- **سرور بدون خروجی در ترمینال باقی می‌ماند:** رفتار طبیعی STDIO است؛ ارتباط از سمت MCP Client آغاز می‌شود.
- **Import ماژول ناموفق است:** مطمئن شوید همان Python ثبت‌شده در تنظیمات، qpTwin را نصب کرده است.
- **Timeout رخ می‌دهد:** اندازه Workspace، محدودیت‌های کلاینت و `tool_timeout` را بررسی کنید.

## اعتبارسنجی پروژه

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/demo_review.py
```

CI رسمی مخزن نسخه‌های Python 3.11، 3.12 و 3.13 را پوشش می‌دهد. قالب هر ۱۲ پروفایل و ارتباط JSON-RPC/STDIO در تست‌های خودکار بررسی می‌شود.

## مجوز

qpTwin Community توسط **Pouriya Khalilian** توسعه یافته و تحت [Apache License 2.0](LICENSE) منتشر می‌شود.
