> **توسعه‌دهنده و مالک: Pouriya Khalilian؛ پروژه مستقل از رستانو.**

# qpTwin MCP — نسخه قابل اجرا برای ارزیابی

**وضعیت: نسخه 0.4، پیش‌نمایش مهندسی با ۱۲ پروفایل اتصال MCP. هنوز محصول نهایی سازمانی و Digital Twin پیوسته نیست.**

هدف پروژه این است که AI Coding Agent پیش از تولید و ادغام تغییرات، شناخت ساختاری از Repository، ارزیابی اثر تغییر و شواهد اولیه عملکرد/امنیت به دست آورد.

### قابلیت‌های موجود

- کشف خودکار ساختار فایل‌های Python، JavaScript و TypeScript و شناسایی تعدادی از Routeهای Flask، FastAPI و Express؛ بدون اجرای کد.
- ساخت گراف وابستگی و تحلیل اثر تغییر یک فایل بر سایر فایل‌ها و APIها.
- قوانین معماری قابل تنظیم مانند ممنوعیت وابستگی Core به API Layer.
- شبیه‌ساز بار رویدادگسسته برای صف درخواست‌ها، Replicas، خرابی ظرفیت و محاسبه P95 به‌صورت فرضی.
- برآورد نرخ ورود و سرعت خدمت از داده‌های آماری تجمیعی CSV.
- تحلیل برخی نشانه‌های امنیتی و اجرای چک‌لیست CIA /redteam.
- خواندن نتایج JUnit و ارائه گزارش راهنمای تصمیم، بدون اجرای تست یا صدور مجوز Production.
- ذخیره و مقایسه Snapshot **فراداده معماری**؛ بدون ذخیره سورس کد در Snapshot.
- اتصال از طریق ابزارهای MCP استاندارد به AI Coding Agentها.

### شروع سریع

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e .
# Linux/macOS:
export TWINDEV_WORKSPACE="/absolute/path/to/project"
# Windows PowerShell:
# $env:TWINDEV_WORKSPACE = "C:\\absolute\\path\\to\\project"
python -m twindev_mcp.offline_stdio
```

با اجرای خط آخر، نرم‌افزار عمداً روی خروجی ترمینال چیزی نمایش نمی‌دهد؛ از طریق MCP client با آن ارتباط برقرار کنید. الگوی اتصال در `config/claude-desktop.example.json` قرار دارد. پس از نصب SDK رسمی ورژن ۲، از `python -m twindev_mcp.server` استفاده کنید.

### محدودیت مهم

وجود این امکانات به معنای آن نیست که سامانه می‌تواند تمام خطاهای برنامه را تشخیص دهد، معماری نرم‌افزار را صددرصد استنتاج کند یا از خرابی Production جلوگیری کند. شبیه‌ساز فعلی مدل ساده صف M/M/c است و برای دیتاسنتر GPU و مدل‌های زبانی واقعی به Benchmark و کالیبراسیون گسترده‌تر نیاز دارد. اتصال مستقیم به داده زنده Production، سیستم IAM سازمانی، اتصال به PR و قابلیت کنترل CI در این نسخه وجود ندارد.

### نتیجه آزمون

در نسخه 0.4.0، مجموعه ۷۵ تست خودکار، ارتباط STDIO و بسته Python بررسی شده‌اند. در محیط Windows چهار تست ویژه Symlink به‌علت نبود مجوز سیستم‌عامل رد نشدند و به‌درستی Skip شدند. آداپتور SDK رسمی همچنان باید جداگانه در محیط دارای بسته اختیاری `mcp` ارزیابی شود.

برای جزئیات فنی، امنیت، سناریوهای تست و نقشه راه تجاری به `README.md` و `docs/` مراجعه کنید.

---

## قابلیت‌های تحلیل و شبیه‌سازی

- تشخیص تغییرات API با مقایسه OpenAPI JSON (`compare_openapi_contracts`)؛ تشخیص حذف Endpoint، اضافه شدن پارامتر اجباری و حذف Response Code؛ جایگزین تست قرارداد نیست.
- شبیه‌ساز چندسرویسی (`simulate_microservice_chain`) با رویدادهای مرتب‌شده زمانی، صف و Replica مستقل برای هر مرحله؛ فقط زنجیره سری و توزیع‌های ساده.
- اعتبارسنجی زمانی Data-Driven (`validate_capacity_holdout`) با داده‌های آموزشی و آزمون تفکیک‌شده زمانی، MAE و Bias و MAPE برای P95؛ نیازمند داده واقعی و آستانه پذیرش.
- تحلیل Diff تولیدی Agent (`analyze_patch`) بدون اعمال Patch یا اجرای کد.
- استخراج متریک‌های محدود از فایل محلی OTLP JSON (`aggregate_otlp_traces`) بدون برگرداندن Payload و شناسه کاربران.
- گزارش یکپارچه بررسی PR (`review_change_evidence`) با قرارداد، کیفیت، شبیه‌سازی و سیاست معماری؛ هیچ مجوز خودکار ادغام یا استقرار صادر نمی‌کند.

### اجرای سریع

```bash
python -m venv .venv
# محیط مجازی را فعال کنید
pip install -e '.[test]'
pytest -q
python scripts/demo_review.py
```

`demo_review.py` از یک پروژه **نمونه ساختگی** در `examples/demo_repository` استفاده می‌کند. عمداً تغییر ناسازگار API در آن طراحی شده است تا نشان دهد Gate چگونه `BLOCKED_FOR_REVIEW` گزارش می‌کند. خروجی این مثال هیچ ادعایی درباره صحت یک پروژه واقعی یا مشتری ندارد.

### اجرای سرور MCP

```bash
export TWINDEV_WORKSPACE="$(pwd)/examples/demo_repository"
python -m twindev_mcp.offline_stdio
```

در ویندوز متغیر محیطی را با روش مناسب PowerShell تنظیم کنید. برای استفاده از سرور با SDK رسمی MCP v2 باید `pip install -e '.[mcp]'` اجرا شود؛ در محیط ساخت این نسخه دریافت SDK به دلیل مشکل DNS ممکن نبود، بنابراین این حالت **هنوز تأیید عملی نشده است**. در این نسخه تست‌های پروتکل روی پیاده‌سازی محلی محدود stdio اجرا شده‌اند.

### وضعیت انتشار و ملاحظات امنیتی

این نسخه **PoC/Engineering Preview** است، نه محصول Enterprise یا Digital Twin عملیاتی کالیبره‌شده. تست‌ها به معنی ممیزی امنیتی مستقل نیستند. MCP را به مخزن قابل‌اعتماد و یک حساب سیستم عامل با حداقل سطح دسترسی محدود کنید؛ داده مشتری را بدون اجازه وارد محیط آزمایشی نکنید. انتشار واقعی نیازمند تست اتصال Client موردنظر، تحلیل بار روی سیستم واقعی، RBAC، تفکیک Tenant، Audit، تأیید سیاست حریم خصوصی و بررسی Provenance خروجی CI است.

---

## سازگاری پیکربندی با AI Coding Clients در v0.4.0

ابزار `scripts/generate_qptwin_configs.py` دوازده پروفایل قابل‌بازبینی برای Cursor، Codex، Claude Code، Google Antigravity، Hermes Agent، OpenClaw، OpenCode، Gemini CLI، Windsurf، Cline، Roo Code و VS Code تولید می‌کند. یک MCP Server مشترک به کلاینت انتخابی معرفی می‌شود و نیازی به ساخت بک‌اندهای مستقل نیست. جزئیات در [`README_QPTWIN_FA.md`](README_QPTWIN_FA.md) آمده است.

**وضعیت:** قالب پیکربندی‌ها و ارتباط STDIO محلی آزمایش شده‌اند؛ اجرای واقعی داخل تمام رابط‌های کلاینت و SDK رسمی v2 هنوز نیازمند آزمون مستقل است. این نسخه آماده فروش Production نیست.

## مجوز و انتشار

نسخه Community پروژه qpTwin با مجوز **Apache License 2.0** منتشر می‌شود و بنا بر اعلام توسعه‌دهنده، متعلق به **Pouriya Khalilian** و مستقل از رستانو است. نسخه‌های اختصاصی/پولی آینده می‌توانند جداگانه عرضه شوند؛ حقوق استفاده از نسخه‌های قبلاً منتشرشده Apache همچنان برقرار است. برای جزئیات [LICENSE](LICENSE)، [NOTICE](NOTICE) و [COMMERCIAL.md](COMMERCIAL.md) را ببینید.
