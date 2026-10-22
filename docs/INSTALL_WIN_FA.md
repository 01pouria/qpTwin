# نصب در Windows (بدون Docker)

ابتدا Python 3.11 یا بالاتر را نصب کنید و سپس در پوشه پروژه qpTwin ترمینال PowerShell را باز کنید.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
$env:TWINDEV_WORKSPACE = 'C:\\Path\\To\\SoftwareRepository'
python -m twindev_mcp.offline_stdio
```

پس از اجرای خط آخر پنجره ممکن است خالی بماند. این رفتار طبیعی یک سرور MCP مبتنی بر stdio است؛ برنامه از طرف AI Coding Agent فراخوانی می‌شود. مسیر Python و Workspace باید در فایل پیکربندی MCP کلاینت به‌صورت مسیر مطلق وارد شود. ساختار نمونه در `config/claude-desktop.example.json` موجود است.

برای نسخه SDK رسمی (در صورت دسترسی به اینترنت):

```powershell
python -m pip install -e '.[mcp]'
python -m twindev_mcp.server
```

**نکته:** قبل از اتصال به محیط کاری واقعی، تست‌ها را اجرا کنید و مجوزهای دسترسی به فایل‌ها را محدود کنید. با هر Repository ناشناخته یا کد دریافت‌شده از مشتری باید مانند منبع غیرقابل‌اعتماد رفتار شود.
