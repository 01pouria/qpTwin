# qpTwin Community

**هوشمندی معماری و تحلیل ریسک تغییر برای مهندسی نرم‌افزار مبتنی بر هوش مصنوعی**

qpTwin یک سرور Model Context Protocol است که توسط **Pouriya Khalilian** توسعه یافته است. این محصول پیش و پس از هر تغییر، تصویری ساختاریافته از مخزن نرم‌افزار در اختیار AI Coding Agent قرار می‌دهد: کشف معماری، تحلیل وابستگی و Endpoint، ارزیابی اثر تغییر، بررسی قرارداد API، شبیه‌سازی ظرفیت، تحلیل شواهد کیفیت و بازبینی ریسک.

نسخه **0.4.0** نسخه جاری Community با مجوز Apache-2.0 است و برای جریان‌های کاری حرفه‌ای، محلی و مبتنی بر MCP طراحی شده است.

## قابلیت‌های اصلی

- شناسایی Componentها، Importها و Routeهای پشتیبانی‌شده در Python، JavaScript و TypeScript بدون اجرای کد پروژه
- تحلیل اثر تغییر فایل‌ها یا Unified Diff بر وابستگی‌ها و Endpointها
- بررسی و مقایسه قراردادهای OpenAPI JSON
- کنترل مرزهای معماری با Policy قابل تنظیم
- شبیه‌سازی محدودشده ظرفیت یک سرویس یا زنجیره چندمرحله‌ای
- کالیبراسیون با متریک‌های تجمیعی CSV و اعتبارسنجی Holdout زمانی
- تحلیل نتایج JUnit، متریک‌های منتخب OTLP و شواهد تغییر
- بازبینی ساختاریافته معماری، محرمانگی، یکپارچگی و دسترس‌پذیری
- ذخیره و مقایسه Snapshot فراداده معماری با درخواست صریح کاربر
- ارائه **۲۳ ابزار MCP** از طریق STDIO محلی
- تولید **۱۲ پروفایل اتصال** برای Cursor، Codex، Claude Code، Antigravity، Hermes Agent، OpenClaw، OpenCode، Gemini CLI، Windsurf، Cline، Roo Code و VS Code

## اصول طراحی

- **Local-first:** تحلیل سورس و ارتباط MCP روی سیستم توسعه‌دهنده انجام می‌شود.
- **دسترسی محدود:** تمام عملیات به یک Workspace مشخص و صریح محدود است.
- **رفتار امن پیش‌فرض:** کد پروژه Parse می‌شود و Import یا اجرا نمی‌شود.
- **پردازش کنترل‌شده:** اندازه فایل، تعداد فایل و حجم شبیه‌سازی محدود شده است.
- **تصمیم‌گیری مبتنی بر شواهد:** qpTwin اطلاعات مهندسی تولید می‌کند و اختیار Merge و Deploy در فرایند توسعه باقی می‌ماند.
- **مدل‌های شفاف:** فرضیات و محدودیت‌های شبیه‌سازی همراه خروجی ارائه می‌شوند.

## نصب

Python 3.11 یا جدیدتر مورد نیاز است.

```bash
git clone https://github.com/01pouria/qpTwin.git
cd qpTwin
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

python -m pip install -e '.[test]'
python -m pytest -q
```

## اجرای سرور MCP

Workspace را روی مخزنی تنظیم کنید که مجاز به تحلیل آن هستید:

```bash
export TWINDEV_WORKSPACE=/absolute/path/to/repository
python -m twindev_mcp.offline_stdio
```

در Windows PowerShell:

```powershell
$env:TWINDEV_WORKSPACE = 'C:\Path\To\Repository'
python -m twindev_mcp.offline_stdio
```

این فرایند از طریق STDIO ارتباط برقرار می‌کند و معمولاً Prompt تعاملی نمایش نمی‌دهد. نام داخلی `twindev_mcp` و متغیر `TWINDEV_WORKSPACE` برای سازگاری نسخه‌های قبلی حفظ شده‌اند؛ نام محصول و CLI، qpTwin است.

برای Adapter مبتنی بر SDK رسمی MCP:

```bash
python -m pip install -e '.[mcp]'
python -m twindev_mcp.server
```

## تولید تنظیمات کلاینت

qpTwin فایل‌های تنظیمات را برای بازبینی تولید می‌کند و تنظیمات فعال کلاینت را تغییر نمی‌دهد.

```bash
python scripts/generate_qptwin_configs.py \
  --workspace /absolute/path/to/repository \
  --python /absolute/path/to/.venv/bin/python \
  --output ./connection-presets
```

فایل‌های خروجی شامل مسیرهای مطلق همان سیستم هستند و به همین دلیل در Git ثبت نمی‌شوند. پروفایل تولیدشده را بررسی و سپس با تنظیمات کلاینت موردنظر ادغام کنید.

جزئیات در [راهنمای اتصال کلاینت‌ها](README_QPTWIN_FA.md) و [راهنمای نصب Windows](docs/INSTALL_WIN_FA.md) آمده است.

## اعتبارسنجی

CI پروژه روی Python 3.11، 3.12 و 3.13 اجرا می‌شود. تست‌ها مرزبندی Workspace، پروتکل MCP، کشف معماری، شبیه‌سازی، قرارداد API، شواهد تغییر، Snapshot و تولید تنظیمات کلاینت را پوشش می‌دهند.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/demo_review.py
```

دموی پروژه عمداً یک تغییر ناسازگار API دارد و باید نتیجه `BLOCKED_FOR_REVIEW` تولید کند.

## محدوده عملیاتی

qpTwin Community v0.4.0 هوشمندی مخزن محلی را از طریق STDIO ارائه می‌کند. این نسخه تست‌های پروژه را اجرا نمی‌کند، سورس برنامه را تغییر نمی‌دهد و Endpoint عمومی چندمشتری ایجاد نمی‌کند. همگام‌سازی پیوسته Runtime، کنترل هویت سازمانی و سرویس مدیریت‌شده در لایه‌های استقرار یا نسخه‌های تجاری ارائه خواهند شد.

خروجی تحلیل ایستا و شبیه‌سازی، ورودی تصمیم مهندسی است. مدل‌ها را با داده نماینده کالیبره کنید و CI، Code Review، تست امنیت و کنترل انتشار را در زنجیره تحویل حفظ کنید.

## امنیت

qpTwin را با حداقل سطح دسترسی اجرا کنید و فقط به مخازنی متصل کنید که مجاز به بررسی آنها هستید. پاسخ MCP می‌تواند اطلاعات مشتق‌شده از معماری را در اختیار کلاینت قرار دهد. کنترل Path Traversal، Symlink، فایل‌های حساس متداول، ورودی‌های بزرگ و فرمت‌های پشتیبانی‌نشده در محصول اعمال شده است؛ ایزوله‌سازی سیستم‌عامل و کنترل دسترسی مخزن همچنان بخشی از معماری استقرار هستند.

جزئیات: [سیاست امنیت](SECURITY.md) و [مدل تهدید](docs/REDTEAM.md).

## مجوز و مالکیت

Copyright © 2026 **Pouriya Khalilian**.

qpTwin Community تحت [Apache License 2.0](LICENSE) منتشر می‌شود. اطلاعات Attribution در [NOTICE](NOTICE) و [OWNERSHIP.md](OWNERSHIP.md)، و راهبرد نسخه‌های Community و تجاری در [COMMERCIAL.md](COMMERCIAL.md) قرار دارد.
