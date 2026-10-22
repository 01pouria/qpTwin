> **توسعه‌دهنده و مالک پروژه: Pouriya Khalilian** — پروژه‌ای مستقل و غیرمتعلق به شرکت رستانو.

# qpTwin Universal MCP — نسخه 0.4.0

نام عمومی محصول **qpTwin** است. ماژول داخلی Python فقط برای سازگاری با نصب‌های پیشین همچنان `twindev_mcp` نام دارد.

## نتیجه آزمون

- ۱۲ نمونه پیکربندی اتصال برای کلاینت‌های دارای پشتیبانی MCP.
- ۷۵ تست خودکار (شامل تست‌های قبلی به‌علاوه سنجش قالب ۱۲ کلاینت).
- آزمون ارتباط واقعی STDIO با کلاینت آزمایشی مستقل: Initialize، List Tools و فراخوانی ابزار `workspace_overview`.
- **تأیید نشده:** اجرای واقعی داخل رابط هر IDE یا Agent؛ سرور HTTP، احراز هویت چندمشتری و پایداری در بار Production.

## نصب و اجرا

در ریشه پروژه، در Python 3.11 یا جدیدتر:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e .
python -m pytest -q   # پس از pip install pytest
```

نسخه مستقل از SDK خارجی با `python -m twindev_mcp.offline_stdio` از طریق STDIO اجرا می‌شود. این رابط برای ابزارهای پایه طراحی شده و تمام قابلیت‌های SDK رسمی MCP را پیاده‌سازی نمی‌کند. نسخه SDK رسمی با نصب اختیاری `pip install -e '.[mcp]'` در نظر گرفته شده ولی در این محیط تأیید اجرایی نشده است.

## تولید بسته تنظیمات

```bash
python scripts/generate_qptwin_configs.py \\
  --workspace /absolute/path/to/your/repo \\
  --python /absolute/path/to/python/in/venv \\
  --output ./connection-presets
```

این فرمان ۱۲ نمونه پیکربندی می‌سازد، تنظیمات اصلی کلاینت‌ها را تغییر نمی‌دهد، و فایل موجود را بدون `--force` بازنویسی نمی‌کند. برای ویندوز از مسیرهای ویندوزی استفاده کنید. مسیر `--python` باید به محیطی اشاره کند که qpTwin در آن نصب شده است.

## کلاینت‌ها

| محیط | فایل نمونه در خروجی | یادداشت |
|---|---|---|
| Cursor | `configs/cursor/.cursor/mcp.json` | STDIO محلی |
| Codex CLI/IDE | `configs/codex/.codex/config.toml` | TOML |
| Google Antigravity | `configs/antigravity/.agents/mcp_config.json` | تنظیم پروژه |
| Claude Code | `configs/claude-code/.mcp.json` | تنظیم پروژه |
| Hermes Agent | `configs/hermes/config-snippet.yaml` | قطعه برای `~/.hermes/config.yaml` |
| OpenClaw | `configs/openclaw/mcp-snippet.json` | قطعه برای `mcp.servers`؛ با فایل کامل ادغام شود |
| OpenCode v2 | `configs/opencode/opencode.json` | نسخه v2؛ روی نسخه‌های قدیمی تفاوت دارد |
| Gemini CLI | `configs/gemini-cli/.gemini/settings.json` | از محتوا فقط بخش `mcpServers` را ادغام کنید |
| Windsurf | `configs/windsurf/mcp_config.json` | فایل Global در محیط Windsurf |
| Cline | `configs/cline/cline_mcp_settings.json` | فایل Global/IDE |
| Roo Code | `configs/roo-code/.roo/mcp.json` | فایل پروژه |
| VS Code | `configs/vscode/.vscode/mcp.json` | کلید بالایی `servers` نه `mcpServers` |

**نکته:** نمونه‌ها در پوشه‌های جداگانه قرار دارند تا فایل‌های یکسان (مانند `.mcp.json`) روی هم بازنویسی نشوند. آنها را پس از بررسی و ادغام به مقصد مناسب منتقل کنید. برای Copilot harness می‌توان از قالب قابل حمل `.mcp.json` نیز استفاده کرد.

## محدودیت و امنیت

1. فقط Workspace مورد اعتماد را در `TWINDEV_WORKSPACE` قرار دهید. سرور محلی را با دسترسی مدیر سیستم اجرا نکنید.
2. لاگ یا محتوای محرمانه مشتری را بدون نیاز در اختیار مدل یا کلاینت قرار ندهید.
3. ابزارهای خواندنی را با ابزارهای قابل تغییر متمایز کنید؛ ابزار `save_architecture_snapshot` نوشتنی است.
4. خروجی Twin شبیه‌سازی/ارزیابی است، نه مجوز انتشار؛ CI، بازبینی انسانی و آزمون واقعی الزامی هستند.
5. **این نسخه Multi-Tenant نیست** و قابلیت پذیرش اتصال عمومی اینترنتی به‌عنوان سرویس اشتراکی را ندارد.
6. تنظیمات Hermes و OpenClaw قطعات الحاقی هستند، نه کل تنظیمات محصول؛ جایگزین‌کردن تنظیمات فعلی ممکن است آنها را خراب کند.

## مراجع مستندات

- Hermes: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/
- OpenClaw: https://docs.openclaw.ai/tools/mcp
- OpenCode v2: https://dev.opencode.ai/v2/docs/mcp-servers/
- Antigravity: https://antigravity.google/docs/mcp
- Gemini CLI: https://geminicli.com/docs/tools/mcp-server/
- VS Code: https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- Cursor: https://prod.cursor.com/docs/mcp

## هدف بعدی

اجرای آزمون رابط واقعی با یکی از محیط‌های کلاینت، سپس راه‌اندازی Streamable HTTP + احراز هویت مناسب، محدودسازی دسترسی چندمشتری، Observability و مدل واقعی Runtime Digital Twin. این قابلیت‌ها هنوز پیاده‌سازی نشده‌اند.

## مجوز و انتشار

نسخه Community پروژه qpTwin با مجوز **Apache License 2.0** منتشر می‌شود و بنا بر اعلام توسعه‌دهنده، متعلق به **Pouriya Khalilian** و مستقل از رستانو است. نسخه‌های اختصاصی/پولی آینده می‌توانند جداگانه عرضه شوند؛ حقوق استفاده از نسخه‌های قبلاً منتشرشده Apache همچنان برقرار است. برای جزئیات [LICENSE](LICENSE)، [NOTICE](NOTICE) و [COMMERCIAL.md](COMMERCIAL.md) را ببینید.
