# گزارش نهایی و مستندات فنی سامانه رزرواسیون هتل
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

---



<!-- SECTION BREAK: overall-diagram.md -->


# بخش اول گزارش نهایی: معماری کلان و دیاگرام‌های سیستم (Overall Architecture & Diagrams)

## ۱. نمای کلی سیستم و پشته فناوری (System Overview & Tech Stack)

سامانه رزرواسیون هتل یک برنامه کاربردی تحت وب چندکاربره (Multi-Role Web Application) است که به صورت معماری کلاینت-سرور جداشده (Decoupled Client-Server) طراحی و پیاده‌سازی شده است. سیستم به دو نقش اصلی **مدیر هتل (Hotel Manager)** و **مهمان (Guest)** به همراه کاربران ناشناس و مدیر ارشد سیستم (Superadmin) خدمات ارائه می‌دهد.

### جدول پشته فناوری (Technology Stack)

| لایه سیستم | فناوری انتخاب‌شده | نسخه / ابزار | دلیل انتخاب و ویژگی‌های فنی |
|---|---|---|---|
| **Frontend (کلاینت)** | React SPA | React 18 + Vite | معماری تک‌صفحه‌ای سبک، سریع و ماژولار بدون وابستگی به TypeScript (جاوااسکریپت خالص طبق الزامات درس) |
| **Styling & UI** | Tailwind CSS | Tailwind v3 | طراحی واکنش‌گرا (Responsive) سازگار با استانداردهای راست‌به‌چپ (RTL) و قلم استاندارد وزیرمتن (Vazirmatn) |
| **Backend (وب‌سرویس)** | Django | Python 3.12 + Django 5.x | وب‌ویوهای صریح جنگو (Plain Views) مبتنی بر فرم‌های اعتبارسنجی (`Django Forms`) بدون استفاده از فریم‌ورک‌های سنگین خارجی مانند DRF |
| **پایگاه داده (DB)** | PostgreSQL | PostgreSQL 16 | پایگاه داده رابطه‌ای قدرتمند، پشتیبانی از قفل‌گذاری سطری بدبینانه (`SELECT FOR UPDATE`)، قیود جامعیت داده‌ها (`CheckConstraint`, `UniqueConstraint`) و تراکنش‌های اتمیک |
| **احراز هویت و امنیت** | Django Session Auth | Session Cookie + CSRF | استفاده از کوکی‌های ایمن سشن (`HttpOnly`, `SameSite=Lax`) و توکن‌های محافظت از حمله جعل درخواست میان‌وب‌گاهی (`CSRF`) |
| **تایید هویت ایمیل** | Stateless Signed Tokens | `django.core.signing.TimestampSigner` | اعتبارسنجی بدون حالت و ۴۸ ساعته با امضای رمزنگاری‌شده بدون نیاز به ایجاد جداول سربار در پایگاه داده |
| **مدیریت لاگ و مانیتورینگ** | Python Logging | File & Stream Handlers | جداسازی کانال‌های لاگ امنیتی (`apps.security`)، لاگ عمومی درخواست‌ها (`apps.core.middleware`) و رهگیری رخدادهای تجاری |

---

## ۲. دیاگرام معماری لایه‌ای سیستم (Layered System Architecture)

معماری سامانه بر مبنای تفکیک دقیق وظایف (Separation of Concerns) در ۵ لایه مجزا سازمان‌دهی شده است:

```mermaid
flowchart TD
    subgraph ClientLayer["۱. لایه کلاینت (Presentation Layer - React SPA)"]
        UI_Guest["پنل مهمان (جستجو، پیش‌فاکتور، ثبت رزرو، تاریخچه)"]
        UI_Manager["پنل مدیریت هتل (افزودن هتل، تعریف انواع اتاق، تقویم و گزارش رزروها)"]
        UI_Auth["ماژول احراز هویت و تایید ایمیل (ورود، ثبت‌نام، بنر تایید ایمیل)"]
        API_Client["کلاینت ارتباطی Fetch API (مدیریت خودکار CSRF Token، خطایابی یکپارچه)"]
    end

    subgraph GatewayLayer["۲. لایه کنترل و امنیت (Security & Middleware Layer)"]
        MW_Log["RequestLogMiddleware (ثبت شناسه کاربر، متد، مسیر، کد وضعیت و زمان پردازش ms)"]
        MW_Session["SessionMiddleware (بارگذاری و اعتبارسنجی کوکی نشست کاربر)"]
        MW_CSRF["CsrfViewMiddleware (محافظت در برابر حملات Cross-Site Request Forgery)"]
        DEC_Auth["دکوراتور login_required_json (بررسی ورود، پاسخ 401 استاندارد)"]
        DEC_Role["دکوراتور role_required (بررسی نقش کاربر، پاسخ 403 استاندارد)"]
        DEC_Verified["دکوراتور verified_required (بررسی تایید ایمیل در تراکنش‌های حساس، پاسخ 403)"]
    end

    subgraph AppViewLayer["۳. لایه منطق وب و کنترلرها (Application & Views Layer)"]
        V_Accounts["apps.accounts (احراز هویت، ثبت‌نام، خروج، /me/، تایید ایمیل و ارسال مجدد)"]
        V_Hotels["apps.hotels (کاتالوگ هتل‌ها، جستجوی بلادرنگ، CRUD هتل و اتاق با تفکیک مالکیت 404)"]
        V_Bookings["apps.bookings (استعلام قیمت، اعتبارسنجی کدهای تخفیف، ثبت و لغو اتمیک رزرو)"]
        V_Core["apps.core (هندلرهای خطای 400/401/403/404/500، پاکت پاسخ استاندارد JSON)"]
    end

    subgraph DomainLayer["۴. لایه دامنه و مدل‌های سفارشی (Domain & Custom Managers Layer)"]
        M_User["UserManager & User Model (مدیریت کاربران، فیلتر guests/managers)"]
        M_Hotel["HotelQuerySet & Hotel Model (فیلترهای active/city/price، واکشی بهینه select_related)"]
        M_Booking["BookingQuerySet & Booking Model (محاسبه تداخل بازه‌ها، رزروهای فعال/لغوشده)"]
        M_Service["Availability Service & Pricing Engine (سنجش ظرفیت، محاسبه پیش‌فاکتور و تخفیف)"]
    end

    subgraph PersistenceLayer["۵. لایه پایگاه داده و ذخیره‌سازی (Data Persistence Layer)"]
        DB_Postgres[("پایگاه داده PostgreSQL\n(جداول اصلی، قفل‌گذاری سطری select_for_update)")]
        DB_Session[("جدول django_session\n(نشست‌های پایدار کاربر در دیتابیس)")]
        File_Logs[("فایل‌های لاگینگ سرور\n(logs/security.log, logs/app.log)")]
        Email_Backend["سیستم ارسال ایمیل جنگو\n(Console Backend / SMTP)"]
    end

    ClientLayer -->|"درخواست‌های HTTP REST با پاکت JSON"| GatewayLayer
    GatewayLayer -->|"پایش امنیت و دسترسی‌ها"| AppViewLayer
    AppViewLayer -->|"اعتبارسنجی با فرم‌ها و فراخوانی مدیران"| DomainLayer
    DomainLayer -->|"اجرای تراکنش‌های اتمیک و کوئری‌های بهینه"| PersistenceLayer
```

---

## ۳. چرخه حیات درخواست سراسری (End-to-End Request/Response Lifecycle)

دیاگرام توالی زیر، جریان یک سناریوی حیاتی در سیستم (استعلام قیمت توسط مهمان، ثبت قطعی رزرو و ثبت رخدادها) را از لحظه کلیک کاربر تا ذخیره‌سازی در پایگاه داده و بازگشت پاسخ نشان می‌دهد:

```mermaid
sequenceDiagram
    autonumber
    actor Guest as کاربر مهمان (Browser)
    participant React as کلاینت فرانت‌اند (React)
    participant MW as میدل‌ورهای جنگو (Middleware)
    participant View as لایه ویو (Booking Views)
    participant Manager as مدیر مدل و سرویس (Managers & Services)
    participant DB as پایگاه داده (PostgreSQL)

    Guest->>React: انتخاب هتل، بازه اقامت و کلیک «استعلام قیمت»
    React->>MW: POST /api/bookings/quote/ (check_in, check_out, room_type, discount_code)
    MW->>MW: ثبت زمان شروع در RequestLogMiddleware
    MW->>MW: اعتبارسنجی کوکی سشن و توکن CSRF
    MW->>View: هدایت درخواست به quote_booking_view
    View->>Manager: اعتبارسنجی فرم و فراخوانی calculate_booking_quote
    Manager->>DB: کوئری محاسبه ظرفیت آزاد اتاق در بازه زمانی انتخابی
    DB-->>Manager: بازگرداندن تعداد اتاق‌های رزرو شده
    Manager->>Manager: ارزیابی شروط کد تخفیف (تاریخ، حداقل مبلغ، سقف مصرف)
    Manager-->>View: بازگرداندن پیش‌فاکتور (قیمت پایه، مبلغ تخفیف، قیمت نهایی)
    View-->>MW: پاسخ استاندارد 200 با پاکت {"data": {...}}
    MW->>MW: لاگ زمان پاسخ‌دهی (duration_ms)
    MW-->>React: تحویل پیش‌فاکتور رسمی به کلاینت
    React-->>Guest: نمایش پیش‌فاکتور شفاف به مهمان

    Guest->>React: کلیک «تأیید و پرداخت نهایی رزرو»
    React->>MW: POST /api/bookings/ (room_type, check_in, check_out, guest_count, discount_code)
    MW->>MW: بررسی دکوراتورهای @login_required_json و @verified_required
    Note over MW: در صورت عدم تایید ایمیل، خطای 403 بازگردانده می‌شود
    MW->>View: هدایت درخواست به booking_create_view
    View->>DB: آغاز تراکنش اتمیک transaction.atomic()
    View->>DB: قفل‌گذاری سطری بدبینانه RoomType.objects.select_for_update()
    View->>Manager: بررسی مجدد ظرفیت با تضمین عدم تداخل همزمانی (Race Condition)
    alt ظرفیت تکمیل شده باشد
        Manager-->>View: صدور خطای AvailabilityConflictError
        View->>DB: Rollback خودکار تراکنش
        View-->>React: پاسخ HTTP 409 Conflict (ظرفیت در این تاریخ به پایان رسید)
        React-->>Guest: نمایش هشدار و پیشنهاد تغییر تاریخ
    else ظرفیت آزاد است
        View->>DB: ثبت رکورد رزرو با وضعیت confirmed
        View->>DB: افزایش شمارنده مصرف کد تخفیف (used_count + 1)
        View->>DB: Commit موفقیت‌آمیز تراکنش
        View-->>MW: پاسخ HTTP 201 Created با شناسه رزرو
        MW-->>React: دریافت نتیجه رزرو قطعی
        React-->>Guest: هدایت به صفحه جزئیات رزرو با پیام موفقیت
    end
```

---

## ۴. تفکیک نقش‌ها و ماتریس سطوح دسترسی (Role-Based Access Matrix)

سیستم دسترسی‌ها را بر اساس مدل مبتنی بر نقش (Role-Based Access Control) مدیریت می‌کند:

| بخش و ماژول سیستم | کاربر ناشناس (Anonymous) | کاربر مهمان (Guest) | مدیر هتل (Manager) | مدیر ارشد (Superadmin) |
|---|:---:|:---:|:---:|:---:|
| **مشاهده کاتالوگ و جستجوی هتل‌ها** | مجاز (Public) | مجاز | مجاز | مجاز |
| **مشاهده جزئیات هتل و اتاق‌ها** | مجاز (Public) | مجاز | مجاز | مجاز |
| **استعلام قیمت و پیش‌فاکتور** | مجاز (Public) | مجاز | مجاز | مجاز |
| **ثبت‌نام و ایجاد حساب کاربری** | مجاز | – | – | مجاز |
| **ورود، خروج و بررسی سشن (`/me/`)** | ورود/ثبت‌نام | مجاز | مجاز | مجاز |
| **تایید ایمیل و درخواست مجدد لینک** | مجاز با توکن | مجاز | مجاز | مجاز |
| **ثبت قطعی رزرو اتاق** | نیازمند ورود (۴۰۱) | مجاز (ایمیل تاییدشده) | ممنوع (۴۰۳) | مجاز |
| **مشاهده تاریخچه رزروهای شخصی** | ممنوع (۴۰۱) | مجاز | ممنوع (۴۰۳) | مجاز |
| **لغو رزروهای شخصی (پیش از موعد)** | ممنوع (۴۰۱) | مجاز | ممنوع (۴۰۳) | مجاز |
| **ایجاد، ویرایش و حذف هتل** | ممنوع (۴۰۱) | ممنوع (۴۰۳) | مجاز (فقط هتل‌های خود) | دسترسی کامل |
| **تعریف انواع اتاق و تعیین قیمت** | ممنوع (۴۰۱) | ممنوع (۴۰۳) | مجاز (فقط هتل‌های خود) | دسترسی کامل |
| **ایجاد و مدیریت کدهای تخفیف** | ممنوع (۴۰۱) | ممنوع (۴۰۳) | مجاز (فقط هتل‌های خود) | دسترسی کامل |
| **مشاهده تقویم و ماتریس ظرفیت هتل** | ممنوع (۴۰۱) | ممنوع (۴۰۳) | مجاز (فقط هتل‌های خود) | دسترسی کامل |
| **مشاهده لیست رزروهای ورودی هتل** | ممنوع (۴۰۱) | ممنوع (۴۰۳) | مجاز (فقط هتل‌های خود) | دسترسی کامل |
| **پنل مدیریت جنگو (`/admin/`)** | ممنوع (۴۰۳/Redirect) | ممنوع (۴۰۳) | ممنوع (بدون دسترسی Staff) | دسترسی کامل |

---

## ۵. امنیت و تدابیر ضد نفوذ در معماری

1. **جلوگیری از حدس‌زدن شناسه‌ها (Anti-Enumeration Protection):** در صورتی که مدیر هتل قصد دسترسی، ویرایش یا حذف منبع متعلق به مدیر دیگری را داشته باشد، سیستم به جای خطای ۴۰۳، پاسخ **404 Not Found** ارسال می‌کند تا از وجود شناسه هتل یا اتاق در سیستم اطلاعی نشت پیدا نکند.
2. **عدم ذخیره‌سازی داده‌های حساس در لاگ‌ها (Hard Rule 9):** کلمات عبور، کلیدهای کامل سشن و محتوای حساس به هیچ عنوان لاگ نمی‌شوند؛ در لاگ‌های امنیتی تنها شناسه کاربر، متد، مسیر و آدرس IP ثبت می‌گردد.
3. **حفاظت در برابر شرایط مسابقه (Race Condition):** قفل سطری PostgreSQL بر روی جدول `RoomType` به همراه تراکنش‌های `atomic` مانع از رزرو همزمان بیش از ظرفیت (Overbooking) توسط چند کاربر همزمان می‌شود.
4. **توکن‌های بدون حالت با امنیت بالا:** توکن‌های تایید ایمیل به کمک الگوریتم امضای هش با کلید رمز (`SECRET_KEY`) و سالت اختصاصی تولید شده و انقضای ۴۸ ساعته آن‌ها بدون وابستگی به دیتابیس به صورت ریاضی ارزیابی می‌شود.


---



<!-- SECTION BREAK: process-per-app.md -->


# بخش دوم گزارش نهایی: تحلیل فرآیندها به تفکیک برنامه‌های جنگو (Process per Django App)

این بخش به تشریح گام‌به‌گام فرآیندها، جریان داده‌ها و منطق تجاری در هر یک از چهار برنامه اصلی وب‌سرویس جنگو (`core`، `accounts`، `hotels`، `bookings`) به تفکیک نقش‌های کاربری (کاربر مهمان، مدیر هتل، کاربر ناشناس و سیستم) می‌پردازد.

---

## ۱. برنامه هسته و زیرساخت (`apps.core`)

### ۱.۱. مسئولیت‌ها و مرزهای برنامه
برنامه `core` وظیفه فراهم‌سازی زیرساخت مشترک، میدل‌ورهای امنیتی و مانیتورینگ، توابع استانداردسازی پاکت پاسخ JSON، دکوراتورهای اعتبارسنجی سطوح دسترسی و میزبانی اپلیکیشن تک‌صفحه‌ای React (SPA Host) را بر عهده دارد. طبق قوانین معماری پروژه، `core` به هیچ‌یک از برنامه‌های دیگر وابستگی مستقیم ندارد.

### ۱.۲. خط لوله پردازش درخواست‌ها (Request Middleware Pipeline)
هنگام ورود هر درخواست HTTP به سرور:
1. **ثبت لاگ و زمان‌سنجی (`RequestLogMiddleware`):** زمان ورود درخواست ثبت شده و پس از اتمام پردازش، متد HTTP، مسیر URL، کد وضعیت پاسخ، شناسه کاربر لاگین‌شده (یا `anon`) و مدت زمان پردازش به میلی‌ثانیه (`duration_ms`) در لاگر `apps.core.middleware` ذخیره می‌شود. درخواست‌های بیش از ۵۰۰ میلی‌ثانیه به عنوان اخطار کندی ثبت می‌شوند.
2. **مدیریت نشست (`SessionMiddleware`):** کوکی نشست امن کاربر واکشی و داده‌های سشن از جدول دیتابیس بازخوانی می‌شوند.
3. **محافظت CSRF (`CsrfViewMiddleware`):** برای متدهای تغییردهنده وضعیت (POST, PUT, DELETE)، هدر `X-CSRFToken` با مقدار توکن کوکی مقایسه و اعتبارسنجی می‌شود.

### ۱.۳. دکوراتورهای امنیتی و کنترل دسترسی
- **`@login_required_json`:** احراز هویت را بررسی کرده و در صورت ناشناس بودن کاربر، پاسخ یکپارچه `HTTP 401 Unauthorized` با پیام `"Authentication required."` بازمی‌گرداند.
- **`@role_required(*allowed_roles)`:** نقش کاربر (`request.user.role`) را ارزیابی می‌کند. در صورت عدم احراز هویت کد ۴۰۱ و در صورت عدم تطابق نقش با لیست مجاز، پاسخ `HTTP 403 Forbidden` با پیام `"Permission denied."` ارسال و رخداد در `apps.security` لاگ می‌شود.
- **`@verified_required(methods=[...])`:** وضعیت تایید ایمیل کاربر (`request.user.email_verified`) را می‌سنجد. این دکوراتور از فیلتر متدهای HTTP پشتیبانی می‌کند؛ به عنوان نمونه برای ایجاد هتل یا رزرو اتاق با متد `POST` خطای ۴۰۳ صادر می‌کند، اما متد `GET` جهت بررسی لیست هتل‌ها بدون مانع عبور داده می‌شود.

### ۱.۴. ساختار استاندارد پاکت پاسخ‌های JSON
تمام پاسخ‌های ارسالی از API از الگوی قراردادی یکنواخت پیروی می‌کنند:
- **پاسخ موفق:** `{"data": {...}}` با کد وضعیت 200 یا 201.
- **پاسخ خطا:** `{"message": "شرح خطا", "errors": {"field": ["خطا"]}}` با کدهای 400، 401، 403، 404، 409 یا 500.

---

## ۲. برنامه مدیریت حساب‌ها و احراز هویت (`apps.accounts`)

### ۲.۱. مسئولیت‌ها و مدل هویتی
این برنامه وظیفه ثبت‌نام کاربران، احراز هویت نشست‌محور (Session-based)، تخصیص نقش (`guest` یا `manager`)، مدیریت نشست‌های ماندگار (`remember_me`) و سرویس تایید ایمیل بدون حالت (Stateless Verification) را بر عهده دارد.

### ۲.۲. فرآیندهای گام‌به‌گام

#### الف) فرآیند ثبت‌نام کاربر جدید (`POST /api/auth/register/`)
```mermaid
flowchart TD
    A[کاربر: ارسال فرم ثبت‌نام نام‌کاربری، ایمیل، گذرواژه، نقش] --> B{اعتبارسنجی RegisterForm}
    B -- خطا در اعتبارسنجی --> C[پاسخ 400 Validation failed + جزییات خطای فیلدها]
    B -- معتبر --> D[ایجاد کاربر در دیتابیس با email_verified=False]
    D --> E[تولید توکن امضاشده TimestampSigner و ارسال ایمیل تایید]
    E --> F[ثبت لاگ امنیتی در apps.security]
    F --> G[پاسخ 201 Created با آبجکت کاربر]
```
1. کاربر داده‌های فرم را ارسال می‌کند. نام کاربری و ایمیل از نظر یکتایی بررسی می‌شوند.
2. گذرواژه از نظر پیچیدگی (طول، تطابق تکرار گذرواژه) اعتبارسنجی و به صورت امن هش (PBKDF2) می‌شود.
3. رکورد کاربر با وضعیت `email_verified=False` در جدول `accounts_user` ذخیره می‌شود.
4. سیستم به طور خودکار توکن تایید ایمیل را تولید و از طریق سرویس ایمیل برای کاربر ارسال می‌کند.

#### ب) فرآیند تایید ایمیل با توکن رمزشده (`POST /api/auth/verify-email/`)
1. مهمان یا مدیر روی پیوند ارسالی در ایمیل کلیک می‌کند (`/verify-email?token=<token>`).
2. کلاینت توکن را به اندپوینت تایید ارسال می‌نماید.
3. تابع `verify_token`:
   - امضای توکن را با کلید مخفی و سالت اختصاصی ارزیابی می‌کند (`BadSignature` -> خطای ۴۰۰).
   - سن مهر زمانی توکن را می‌سنجد (`max_age=172800` معادل ۴۸ ساعت؛ در صورت انقضا -> خطای ۴۰۰).
   - شناسه کاربر را استخراج و در صورت حذف کاربر، خطای ۴۰۰ صادر می‌کند.
4. فیلد `email_verified = True` در دیتابیس ذخیره شده و موفقیت عملیات در `apps.security` ثبت می‌گردد.

#### ج) فرآیند ورود به سامانه و مدیریت نشست (`POST /api/auth/login/`)
1. کاربر نام‌کاربری یا ایمیل خود را به همراه گذرواژه ارسال می‌کند (`LoginForm`).
2. سیستم شناسه را به صورت غیرحساس به حروف بزرگ و کوچک (Case-Insensitive) با رکورد کاربر تطبیق می‌دهد.
3. در صورت فعال بودن گزینه `remember_me`، انقضای نشست روی ۲ هفته (`set_expiry(1209600)`) و در غیر این صورت روی انقضا با بستن مرورگر (`set_expiry(0)`) تنظیم می‌شود.
4. تابع `django.contrib.auth.login` شناسه کاربر را در نشست ذخیره کرده و ردیف سشن در دیتابیس نوشته می‌شود.
5. زمان ورود (`last_login`) در جدول سشن ذخیره شده و در پاسخ بازگردانده می‌شود.

#### د) فرآیند دریافت وضعیت کاربر جاری (`GET /api/auth/me/`)
- در صورت ورود کاربر: آبجکت مشخصات (`id`, `username`, `email`, `role`, `email_verified`, `last_login`) با کد ۲۰۰ بازگردانده می‌شود.
- در صورت ناشناس بودن: پاسخ معتبر `{"data": null}` با کد ۲۰۰ ارسال می‌گردد تا فرانت‌اند وضعیت ورود را تشخیص دهد.

#### ه) فرآیند خروج از سامانه (`POST /api/auth/logout/`)
- درخواست با دکوراتور `@login_required_json` محافظت شده است.
- متد `request.session.flush()` سشن کاربر را از حافظه و جدول پایگاه‌داده به طور کامل پاکسازی می‌کند.

---

## ۳. برنامه هتل‌ها و انواع اتاق (`apps.hotels`)

### ۳.۱. مسئولیت‌ها و مدل داده
این برنامه مسئولیت ذخیره مشخصات هتل‌ها (`Hotel`)، امکانات رفاهی (`Amenity`) و انواع اتاق (`RoomType`) را به همراه خدمات جستجو برای مهمانان و پنل مدیریت CRUD برای مدیران بر عهده دارد.

### ۳.۲. فرآیندهای عمومی و مهمان (Public / Guest Flows)

#### الف) فرآیند جستجو و فیلتر هتل‌ها (`GET /api/hotels/`)
```mermaid
flowchart TD
    Req[درخواست جستجو با پارامترهای q, city, min_price, max_price, check_in, check_out] --> Val{اعتبارسنجی SearchForm}
    Val -- تاریخ گذشته یا نامعتبر --> Err[پاسخ 400 Bad Request]
    Val -- معتبر --> QS[اجرای HotelQuerySet.active]
    QS --> F_City[فیلتر شهر و تطابق عنوان هتل]
    F_City --> F_Price[فیلتر بازه قیمت روی اتاق‌های وابسته]
    F_Price --> F_Avail[محاسبه ظرفیت خالی اتاق‌ها در بازه تاریخی]
    F_Avail --> Opt[بهینه‌سازی واکشی با select_related و prefetch_related]
    Opt --> Resp[پاسخ 200 با لیست هتل‌ها، کمترین قیمت هر شب و تصویر]
```
1. پارامترهای ارسالی در `SearchForm` بررسی می‌شوند (عدم انتخاب تاریخ ورود در گذشته و رعایت `check_out > check_in`).
2. فیلترها روی متدهای زنجیره‌ای `HotelQuerySet` (`active()`, `by_city()`, `by_price_range()`, `search()`) اعمال می‌شوند.
3. جهت جلوگیری از مشکل کارایی N+1، هتل‌ها همراه با مالک و امکانات با متدهای `select_related("owner")` و `prefetch_related("room_types__amenities")` واکشی می‌شوند.

#### ب) مشاهده جزئیات هتل و اتاق‌ها (`GET /api/hotels/<id>/`)
- اطلاعات کامل هتل همراه با انواع اتاق‌های موجود بازگردانده می‌شود.
- در صورت فعال بودن نشست، شناسه هتل به عنوان آخرین هتل‌های مشاهده‌شده (`recent_hotels`) در سشن مهمان نگهداری می‌شود تا در صفحه اصلی دسترسی سریع فراهم باشد.

### ۳.۳. فرآیندهای اختصاصی مدیر هتل (Manager CRUD Flows)

#### الف) ایجاد و ویرایش هتل (`POST / PUT /api/manager/hotels/`)
1. دسترسی با دکوراتورهای `@role_required("manager")` و `@verified_required(methods=["POST"])` بررسی می‌شود.
2. فرم `HotelForm` اطلاعات ارسالی (نام، شهر، آدرس، امتیاز ستاره) را اعتبارسنجی می‌کند.
3. فیلد `owner` به طور خودکار برابر با مدیر واردشده (`request.user`) تنظیم می‌شود.

#### ب) تفکیک مالکیت و جلوگیری از افشای داده‌ها (Ownership 404 Guard)
- در تمامی عملیات ویرایش (`PUT`)، مشاهده جزئیات (`GET`) یا حذف (`DELETE`) هتل یا نوع اتاق:
  ```python
  hotel = get_object_or_404(Hotel.objects.filter(owner=request.user), id=hotel_id)
  ```
- **تدبیر امنیتی:** اگر مدیر A شناسه هتل مدیر B را درخواست کند، سیستم خطای **404 Not Found** صادر می‌کند تا مهاجم نتواند با حدس زدن شناسه‌ها، ساختار داده‌های دیگران را بررسی کند.

#### ج) مدیریت انواع اتاق (`/api/manager/hotels/<id>/room-types/`)
- مدیر نوع اتاق جدید (عنوان، ظرفیت، قیمت هر شب و تعداد اتاق فیزیکی موجود) را ثبت و امکانات رفاهی (`Amenity`) را به آن متصل می‌کند.
- عنوان اتاق درون یک هتل با قود یکتایی `unique_together = [("hotel", "title")]` محافظت می‌شود.

---

## ۴. برنامه رزرواسیون و تخفیف‌ها (`apps.bookings`)

### ۴.۱. مسئولیت‌ها و هسته محاسباتی سیستم
برنامه `bookings` قلب تپنده تجاری سیستم است که وظایف زیر را به انجام می‌رساند:
- استعلام قیمت و پیش‌فاکتور پویا
- کنترل تداخل تاریخ‌ها و مدیریت جابجایی روزانه (Same-day Turnover)
- جلوگیری از رزرو مازاد بر ظرفیت (Overbooking) با قفل سطری PostgreSQL
- اعتبارسنجی و اعمال کدهای تخفیف با قوانین چندگانه
- ثبت قطعی و لغو اتمیک با احیای ظرفیت و سهمیه تخفیف
- ارائه ماتریس و تقویم ظرفیت هتل به مدیر

### ۴.۲. فرآیندهای گام‌به‌گام

#### الف) استعلام قیمت و بررسی ظرفیت (`POST /api/bookings/quote/`)
1. مهمان تاریخ‌های ورود و خروج، تعداد اتاق و کد تخفیف اختیاری را ارسال می‌کند.
2. سامانه موجودی فعال اتاق را در تمام روزهای بازه ارزیابی می‌کند:
   - شرط تداخل دو رزرو: `check_in < req_out AND check_out > req_in`.
   - به دلیل ساعت خروج ۱۲ ظهر و ورود ۱۴ بعدازظهر، خروج در همان روز ورودِ مهمان بعدی (`req_in == exist_out`) مجاز بوده و تداخل محسوب نمی‌شود (Same-day Turnover).
3. در صورت وجود ظرفیت، قیمت پایه به فرمول `تعداد شب‌ها × قیمت هر شب × تعداد اتاق` محاسبه می‌شود.
4. در صورت ورود کد تخفیف، اعتبارسنجی شروط در `calculate_discount` انجام می‌پذیرد:
   - وضعیت فعال بودن (`is_active=True`)
   - بازه زمانی اعتبار (`valid_from <= today <= valid_to`)
   - سقف دفعات استفاده (`used_count < max_uses`)
   - حداقل مبلغ رزرو (`subtotal >= min_booking_amount`)
   - انطباق با هتل انتخاب‌شده (کوپن هتل دیگر رد می‌شود)
5. پیش‌فاکتور رسمی با تفکیک قیمت کل، سود تخفیف و مبلغ نهایی تولید می‌شود.

#### ب) ثبت نهایی و قطعی رزرو (`POST /api/bookings/`)
```mermaid
sequenceDiagram
    participant Guest as مهمان لاگین‌شده
    participant View as booking_create_view
    participant DB as PostgreSQL
    participant Service as Availability & Booking Service

    Guest->>View: ارسال فرم رزرو (اتاق، تاریخ‌ها، تعداد، کد تخفیف)
    View->>View: بررسی @verified_required (ایمیل باید تایید باشد)
    View->>DB: آغاز تراکنش transaction.atomic()
    View->>DB: قفل‌گذاری سطری بدبینانه RoomType.objects.select_for_update().get(id=...)
    View->>Service: بررسی قطعی موجودی اتاق در بازه اقامت
    alt ظرفیت در حداقل یک شب پر باشد
        Service-->>View: صدور AvailabilityConflictError
        View->>DB: Rollback تراکنش
        View-->>Guest: پاسخ HTTP 409 Conflict
    else ظرفیت آزاد موجود است
        Service->>DB: قفل‌گذاری سطر کد تخفیف select_for_update (در صورت وجود)
        Service->>DB: ثبت رکورد Booking با وضعیت confirmed
        Service->>DB: افزایش اتمیک شمارنده کد تخفیف F('used_count') + 1
        View->>DB: Commit تراکنش
        View-->>Guest: پاسخ HTTP 201 Created با جزئیات رزرو
    end
```

#### ج) لغو رزرو اقامت (`POST /api/bookings/<id>/cancel/`)
1. مهمان درخواست لغو رزرو شخصی خود را ارسال می‌کند.
2. بررسی مالکیت: مهمان تنها می‌تواند رزروهای شخص خود را لغو کند (`user=request.user`)؛ در غیر این صورت خطای ۴۰۴ بازگردانده می‌شود.
3. بررسی امکان لغو: رزرو نباید از قبل لغو شده باشد و تاریخ ورود نباید در گذشته باشد.
4. تراکنش اتمیک لغو:
   - وضعیت رزرو به `cancelled` تغییر می‌یابد.
   - ظرفیت اتاق فیزیکی به طور خودکار برای سایر مهمانان آزاد می‌شود.
   - در صورت استفاده از کد تخفیف با سقف محدود، شمارنده `used_count` کد تخفیف با یک واحد کاهش اتمیک احیا می‌شود (`F('used_count') - 1`) تا مهمان دیگری بتواند از آن استفاده کند.

#### د) گزارش رزروها و تقویم ظرفیت برای مدیر هتل
- مدیر هتل از طریق `/api/manager/hotels/<id>/bookings/` لیست رزروهای مهمانان را همراه با فیلتر وضعیت (`confirmed`, `cancelled`) مشاهده می‌کند.
- از طریق `/api/manager/hotels/<id>/availability/?start_date=...&end_date=...` ماتریس روزانه ظرفیت برای هر نوع اتاق (`total_rooms`, `reserved_rooms`, `free_rooms`) محاسبه و نمایش داده می‌شود.


---



<!-- SECTION BREAK: models.md -->


# بخش سوم گزارش نهایی: مدل‌های داده و روابط (Models & Database Schema)

این بخش به تشریح کامل پایگاه داده، نمودار رابطه موجودیت‌ها (ERD)، جدول مشخصات فیلدها، تحلیل روابط کلید خارجی، دلایل انتخاب سیاست‌های حذف آبشاری (`on_delete`)، قیود جامعیت داده‌ها (`CheckConstraint` و `UniqueConstraint`) و ایندکس‌های بهینه‌سازی در پایگاه داده PostgreSQL می‌پردازد.

---

## ۱. نمودار رابطه موجودیت‌ها (Entity-Relationship Diagram - ERD)

```mermaid
erDiagram
    USER ||--o{ HOTEL : "مالکیت / مدیریت (owner)"
    HOTEL ||--o{ ROOMTYPE : "تعریف انواع اتاق (hotel)"
    ROOMTYPE }o--o{ AMENITY : "امکانات رفاهی اتاق (amenities)"
    HOTEL ||--o{ DISCOUNTCODE : "صدور کدهای تخفیف (hotel)"
    USER ||--o{ BOOKING : "رزروکننده اقامت (guest)"
    ROOMTYPE ||--o{ BOOKING : "اتاق رزروشده (room_type)"
    DISCOUNTCODE ||--o{ BOOKING : "کد تخفیف اعمال‌شده (discount_code)"
    USER ||--o{ REVIEW : "نویسنده نظر (user)"
    HOTEL ||--o{ REVIEW : "هتل مورد ارزیابی (hotel)"

    USER {
        int id PK
        string username UK "نام کاربری یکتا"
        string email UK "ایمیل یکتا و اجباری"
        string password "گذرواژه هش‌شده با PBKDF2"
        string role "نقش: manager | guest"
        string phone "شماره تماس"
        boolean email_verified "وضعیت تایید ایمیل"
        boolean is_active "فعال بودن حساب"
        boolean is_staff "دسترسی ادمین جنگو"
        datetime date_joined "تاریخ عضویت"
    }

    HOTEL {
        bigint id PK
        int owner_id FK "کلید خارجی به User (CASCADE)"
        string name "نام هتل"
        string city "شهر هتل (دارای ایندکس)"
        text address "آدرس کامل خیابان"
        text description "توضیحات هتل"
        smallint star_rating "درجه ستاره ۱ تا ۵ (اختیاری)"
        decimal latitude "عرض جغرافیایی"
        decimal longitude "طول جغرافیایی"
        string image_url "آدرس تصویر شاخص"
        boolean is_active "وضعیت فعالیت هتل (دارای ایندکس)"
        datetime created_at "تاریخ ثبت"
    }

    AMENITY {
        bigint id PK
        string name UK "عنوان ویژگی (مثلاً WiFi, استخر)"
        text description "توضیحات تکمیلی"
        datetime created_at "تاریخ ایجاد"
    }

    ROOMTYPE {
        bigint id PK
        bigint hotel_id FK "کلید خارجی به Hotel (CASCADE)"
        string title "عنوان نوع اتاق (یکتا در هر هتل)"
        text description "توضیحات چیدمان اتاق"
        smallint capacity "ظرفیت نفرات (حداقل ۱)"
        bigint price_per_night "قیمت هر شب اقامت به تومان"
        int quantity "تعداد کل اتاق‌های فیزیکی (حداقل ۱)"
        datetime created_at "تاریخ ثبت"
    }

    DISCOUNTCODE {
        bigint id PK
        bigint hotel_id FK "کلید خارجی به Hotel (CASCADE)"
        string code "کد تخفیف حروف بزرگ (یکتا در هر هتل)"
        smallint percent "درصد تخفیف ۱ تا ۱۰۰"
        date valid_from "شروع تاریخ اعتبار"
        date valid_to "پایان تاریخ اعتبار"
        int max_uses "حداکثر سقف استفاده (null=نامحدود)"
        int used_count "شمارنده دفعات استفاده"
        boolean is_active "وضعیت فعال بودن کد"
        datetime created_at "تاریخ ایجاد"
    }

    BOOKING {
        bigint id PK
        int guest_id FK "کلید خارجی به User (PROTECT)"
        bigint room_type_id FK "کلید خارجی به RoomType (PROTECT)"
        date check_in "تاریخ ورود مهمان"
        date check_out "تاریخ خروج مهمان"
        smallint rooms_count "تعداد اتاق درخواستی (حداقل ۱)"
        smallint guests_count "تعداد مهمانان (حداقل ۱)"
        smallint nights "تعداد شب‌های محاسبه‌شده"
        bigint price_per_night_snapshot "اسنپ‌شات قیمت در زمان رزرو"
        bigint subtotal "مبلغ پایه فاکتور"
        bigint discount_code_id FK "کلید خارجی به DiscountCode (SET_NULL)"
        bigint discount_amount "سود مهمان از تخفیف به تومان"
        bigint total_price "مبلغ نهایی فاکتور به تومان"
        string status "وضعیت: confirmed | cancelled"
        datetime created_at "تاریخ ثبت رزرو"
        datetime cancelled_at "تاریخ لغو رزرو"
    }

    REVIEW {
        bigint id PK
        bigint hotel_id FK "کلید خارجی به Hotel (CASCADE)"
        int user_id FK "کلید خارجی به User (CASCADE)"
        smallint rating "امتیاز ۱ تا ۵"
        text comment "متن نظر و بازخورد"
        datetime created_at "تاریخ ثبت"
        datetime updated_at "تاریخ ویرایش"
    }
```

---

## ۲. تحلیل روابط و دلایل انتخاب سیاست‌های `on_delete`

انتخاب رفتار کلید خارجی (`on_delete`) در زمان حذف رکوردهای والد یکی از مباحث اساسی طراحی پایگاه داده است که در این پروژه با دقت مهندسی بالا انتخاب شده است:

| رابطه (Relationship) | مدل مبدا → مقصد | سیاست `on_delete` | دلیل فنی و پیامد تجاری |
|---|---|:---:|---|
| **هتل به مدیر هتل** | `Hotel.owner → User` | `CASCADE` | هتل یک دارایی تحت تملک مدیر است. در صورت حذف حساب کاربری مدیر، تمامی هتل‌ها و اطلاعات تابعه او باید به صورت آبشاری حذف شوند. |
| **نوع اتاق به هتل** | `RoomType.hotel → Hotel` | `CASCADE` | اتاق بدون وجود هتل فیزیکی مفهوم تجاری ندارد؛ بنابراین با حذف هتل، انواع اتاق‌های تابعه آن نیز حذف می‌گردند. |
| **کد تخفیف به هتل** | `DiscountCode.hotel → Hotel` | `CASCADE` | کدهای تخفیف به صورت اختصاصی برای یک هتل صادر می‌شوند؛ با حذف هتل، کوپن‌های آن نیز بی‌معنی شده و حذف می‌شوند. |
| **نظر به هتل / کاربر** | `Review.hotel / user` | `CASCADE` | در صورت حذف هتل یا حذف کاربر، نظرات و امتیازات وابسته به آن حذف می‌شوند. |
| **رزرو به مهمان** | `Booking.guest → User` | **`PROTECT`** | **حفظ اسناد مالی:** اگر مهمانی سابقه رزرو در سیستم داشته باشد، حساب کاربری او نباید به سادگی حذف شود تا تاریخچه تراکنش‌های مالی و تعهدات رزرو هتل از بین نرود. جنگو در صورت تلاش برای حذف کاربر با رزرو فعال، خطای `ProtectedError` صادر می‌کند. |
| **رزرو به نوع اتاق** | `Booking.room_type → RoomType` | **`PROTECT`** | **حفظ اسناد رزرو و ظرفیت:** مدیری نمی‌تواند نوع اتاقی را که دارای رزروهای ثبت‌شده در سیستم است حذف کند؛ زیرا باعث از بین رفتن تعهد هتل به مهمان و شکست ارجاعات مالی فاکتور می‌شود. |
| **رزرو به کد تخفیف** | `Booking.discount_code → DiscountCode` | **`SET_NULL`** | اگر مدیر هتل یک کد تخفیف منقضی‌شده را از سیستم حذف کند، فاکتورهای رزرو قبلی که از آن کد استفاده کرده بودند نباید حذف شوند؛ بلکه شناسه کوپن در رزرو برابر `NULL` می‌شود، در حالی که مقادیر مالی `discount_amount` و `total_price` قبلاً در فیلدهای اسنپ‌شات تثبیت شده‌اند و تغییر نمی‌کنند. |

---

## ۳. تحلیل تفصیلی مشخصات هر مدل

### ۳.۱. مدل کاربر (`apps.accounts.models.User`)
- **هدف:** مدل احراز هویت سفارشی و متمرکز که از `AbstractUser` جنگو ارث‌بری می‌کند و به تفکیک نقش‌های مهمان و مدیر می‌پردازد.
- **مدیر سفارشی (`UserManager`):** تضمین مقداردهی پیش‌فرض نقش مهمان (`guest`)، اعتبارسنجی اجباری بودن فیلد ایمیل، و ارائه متدهای کمکی `User.objects.managers()` و `User.objects.guests()`.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | مقادیر پیش‌فرض / توضیحات |
|---|---|---|:---:|---|
| `id` | `AutoField` | `serial PRIMARY KEY` | خیر | شناسه خودکار افزایشی |
| `username` | `CharField(150)` | `varchar(150) UNIQUE` | خیر | نام کاربری یکتا |
| `email` | `EmailField(254)` | `varchar(254) UNIQUE` | خیر | ایمیل یکتا و اجباری جهت ارتباط و ورود |
| `password` | `CharField(128)` | `varchar(128)` | خیر | گذرواژه هش‌شده با الگوریتم امن PBKDF2 |
| `role` | `CharField(20)` | `varchar(20)` | خیر | نقش کاربر (`manager` یا `guest`؛ پیش‌فرض: `guest`) |
| `phone` | `CharField(20)` | `varchar(20)` | بله | شماره تماس تلفن همراه مهمان/مدیر |
| `email_verified` | `BooleanField` | `boolean` | خیر | وضعیت تایید ایمیل (پیش‌فرض: `False`) |
| `is_active` | `BooleanField` | `boolean` | خیر | وضعیت فعال بودن حساب (پیش‌فرض: `True`) |
| `date_joined` | `DateTimeField` | `timestamp with time zone` | خیر | زمان ایجاد حساب کاربری |

---

### ۳.۲. مدل ویژگی‌ها و امکانات رفاهی (`apps.hotels.models.Amenity`)
- **هدف:** تعریف ویژگی‌های استاندارد اتاق‌ها و هتل‌ها (مانند اینترنت پرسرعت، استخر، صبحانه، پارکینگ، بالکن).

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شناسه کلید اصلی |
| `name` | `CharField(100)` | `varchar(100) UNIQUE` | خیر | عنوان یکتای ویژگی |
| `description` | `TextField` | `text` | بله | توضیحات اختیاری |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | زمان ایجاد رکورد |

---

### ۳.۳. مدل هتل (`apps.hotels.models.Hotel`)
- **هدف:** معرفی واحد اقامتی تحت مدیریت یک مدیر هتل به همراه موقعیت مکانی و مشخصات ستاره.
- **مدیر سفارشی (`HotelQuerySet`):** فیلترهای بهینه `active()`، `in_city()`، `priced_between()`، و الحاق محاسبه کمترین قیمت هر شب با متد `with_min_price()`.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شناسه کلید اصلی |
| `owner_id` | `ForeignKey(User)` | `integer REFERENCES accounts_user` | خیر | مالک هتل (`on_delete=CASCADE`) |
| `name` | `CharField(255)` | `varchar(255)` | خیر | نام هتل |
| `city` | `CharField(100)` | `varchar(100)` | خیر | شهر هتل (دارای ایندکس جهت جستجوی سریع) |
| `address` | `TextField` | `text` | خیر | آدرس کامل خیابان |
| `description` | `TextField` | `text` | بله | متن توضیحات و معرفی هتل |
| `star_rating` | `PositiveSmallIntegerField` | `smallint` | بله | درجه ستاره بین ۱ تا ۵ (دارای اعتبارسنجی) |
| `latitude` | `DecimalField(9, 6)` | `numeric(9,6)` | بله | عرض جغرافیایی |
| `longitude` | `DecimalField(9, 6)` | `numeric(9,6)` | بله | طول جغرافیایی |
| `image_url` | `URLField(500)` | `varchar(500)` | بله | پیوند تصویر شاخص هتل |
| `is_active` | `BooleanField` | `boolean` | خیر | وضعیت فعالیت در نتایج جستجو (پیش‌فرض: `True`) |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | تاریخ ثبت هتل |

#### ایندکس‌ها و قیود دیتابیسی مدل Hotel:
1. `hotel_city_idx`: ایندکس روی فیلد `city` برای پاسخ‌دهی بلادرنگ فیلتر شهر.
2. `hotel_is_active_idx`: ایندکس روی فیلد `is_active` جهت فیلتر سریع هتل‌های عمومی.
3. قید دامنه `hotel_star_rating_1_to_5`: قید `CHECK (star_rating BETWEEN 1 AND 5 OR star_rating IS NULL)`.

---

### ۳.۴. مدل نوع اتاق (`apps.hotels.models.RoomType`)
- **هدف:** دسته‌بندی اتاق‌های هتل با ظرفیت، قیمت هر شب و موجودی فیزیکی مستقل.
- **مدیر سفارشی (`RoomTypeQuerySet`):** ارائه متد حیاتی `with_availability(check_in, check_out)` که با یک زیرکوئری پایگاه داده، تعداد اتاق‌های آزاد را بدون افتادن در تله کوئری N+1 محاسبه می‌کند.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شناسه کلید اصلی |
| `hotel_id` | `ForeignKey(Hotel)` | `bigint REFERENCES hotels_hotel` | خیر | هتل مربوطه (`on_delete=CASCADE`) |
| `title` | `CharField(150)` | `varchar(150)` | خیر | عنوان اتاق (مانند سوییت دونفره رویال) |
| `description` | `TextField` | `text` | بله | امکانات و چیدمان تخت‌ها |
| `capacity` | `PositiveSmallIntegerField`| `smallint` | خیر | حداکثر ظرفیت پذیرش نفرات (حداقل ۱) |
| `price_per_night` | `PositiveBigIntegerField` | `bigint` | خیر | بهای هر شب به تومان (پشتیبانی از اعداد بزرگ) |
| `quantity` | `PositiveIntegerField` | `integer` | خیر | تعداد کل اتاق‌های فیزیکی موجود از این نوع (حداقل ۱) |
| `amenities` | `ManyToManyField` | جدول واسط M2M | بله | امکانات اتاق متصل به `Amenity` |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | تاریخ تعریف نوع اتاق |

#### ایندکس‌ها و قیود دیتابیسی مدل RoomType:
1. قید یکتایی `unique_hotel_roomtype_title`: قید `UNIQUE (hotel_id, title)` مانع از ایجاد دو نوع اتاق با نام یکسان در یک هتل می‌شود.
2. قید جامعیت `roomtype_capacity_gte_1`: قید `CHECK (capacity >= 1)`.
3. قید جامعیت `roomtype_quantity_gte_1`: قید `CHECK (quantity >= 1)`.

---

### ۳.۵. مدل کد تخفیف (`apps.bookings.models.DiscountCode`)
- **هدف:** کدهای پروموشن و تخفیف درصدی تعریف‌شده توسط مدیر برای یک هتل مشخص.
- **مدیر سفارشی (`DiscountCodeManager`):** متد `valid_now(hotel, today)` برای ارزیابی تجاری وضعیت فعال بودن، بازه تاریخی و سقف مجاز استفاده.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شناسه کلید اصلی |
| `hotel_id` | `ForeignKey(Hotel)` | `bigint REFERENCES hotels_hotel` | خیر | هتل صادرکننده کوپن (`CASCADE`) |
| `code` | `CharField(50)` | `varchar(50)` | خیر | کد تخفیف (ذخیره با حروف بزرگ انگلیسی) |
| `percent` | `PositiveSmallIntegerField`| `smallint` | خیر | درصد کسر تخفیف (بین ۱ تا ۱۰۰) |
| `valid_from` | `DateField` | `date` | خیر | شروع تاریخ مجاز استفاده (شامل) |
| `valid_to` | `DateField` | `date` | خیر | پایان تاریخ مجاز استفاده (شامل) |
| `max_uses` | `PositiveIntegerField` | `integer` | بله | سقف دفعات استفاده مجاز (`null` به معنی نامحدود) |
| `used_count` | `PositiveIntegerField` | `integer` | خیر | شمارنده تعداد مصرف‌شده (پیش‌فرض: ۰) |
| `is_active` | `BooleanField` | `boolean` | خیر | وضعیت فعال/غیرفعال دستی توسط مدیر |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | تاریخ ایجاد کد |

#### قیود دیتابیسی مدل DiscountCode:
1. قید یکتایی `unique_hotel_discount_code`: قید `UNIQUE (hotel_id, code)` جهت یکتایی کد در سطح هر هتل.
2. قید بازه درصد `discount_percent_1_to_100`: قید `CHECK (percent >= 1 AND percent <= 100)`.
3. قید تقدم تاریخ `discount_valid_to_gte_valid_from`: قید `CHECK (valid_to >= valid_from)`.
4. قید عدم منفی شدن شمارنده `discount_used_count_gte_0`: قید `CHECK (used_count >= 0)`.

---

### ۳.۶. مدل رزرو اقامت (`apps.bookings.models.Booking`)
- **هدف:** سند رزرو قطعی اقامت مهمان در هتل، نگهداری اسنپ‌شات‌های مالی، وضعیت سفارش و بازه‌های زمانی ورود/خروج.
- **مدیر سفارشی (`BookingQuerySet`):** متدهای دامنه `active()` (تنها رزروهای `confirmed`)، `overlapping(check_in, check_out)` و تفکیک دسترسی‌های مهمان و مدیر.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شماره فاکتور و شناسه رزرو |
| `guest_id` | `ForeignKey(User)` | `integer REFERENCES accounts_user` | خیر | مهمان رزروکننده (`on_delete=PROTECT`) |
| `room_type_id` | `ForeignKey(RoomType)` | `bigint REFERENCES hotels_roomtype` | خیر | اتاق رزروشده (`on_delete=PROTECT`) |
| `check_in` | `DateField` | `date` | خیر | تاریخ ورود (ساعت ۱۴:۰۰) |
| `check_out` | `DateField` | `date` | خیر | تاریخ خروج (ساعت ۱۲:۰۰ ظهر، نامتقاطع) |
| `rooms_count` | `PositiveSmallIntegerField`| `smallint` | خیر | تعداد اتاق رزروشده (حداقل ۱) |
| `guests_count` | `PositiveSmallIntegerField`| `smallint` | خیر | تعداد مسافران مقیم (حداقل ۱) |
| `nights` | `PositiveSmallIntegerField`| `smallint` | خیر | مدت شب اقامت (`check_out - check_in`) |
| `price_per_night_snapshot` | `PositiveBigIntegerField` | `bigint` | خیر | تثبیت قیمت هر شب اتاق در لحظه ثبت رزرو |
| `subtotal` | `PositiveBigIntegerField` | `bigint` | خیر | جمع پایه قبل از تخفیف (`nights × price × rooms`) |
| `discount_code_id` | `ForeignKey(DiscountCode)`| `bigint REFERENCES ...` | بله | کوپن اعمال‌شده (`on_delete=SET_NULL`) |
| `discount_amount` | `PositiveBigIntegerField` | `bigint` | خیر | مبلغ ریالی تخفیف کسرشده به تومان |
| `total_price` | `PositiveBigIntegerField` | `bigint` | خیر | مبلغ نهایی پرداختی (`subtotal - discount_amount`) |
| `status` | `CharField(20)` | `varchar(20)` | خیر | وضعیت رزرو (`confirmed` یا `cancelled`) |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | زمان ایجاد و ثبت رزرو |
| `cancelled_at` | `DateTimeField` | `timestamp with time zone` | بله | زمان لغو رزرو توسط مهمان یا سیستم |

#### ایندکس‌ها و قیود دیتابیسی مدل Booking:
1. ایندکس ترکیبی تداخل `booking_rt_dates_idx`: ایندکس روی `(room_type, check_in, check_out)` برای سریع‌ترین پردازش ارزیابی تداخل تاریخ‌ها.
2. ایندکس تاریخچه مهمان `booking_guest_status_idx`: ایندکس روی `(guest, status)` جهت شتاب‌بخشی به فهرست «رزروهای من».
3. ایندکس وضعیت `booking_status_idx`: ایندکس روی `status` جهت فیلتر سریع رزروهای فعال در محاسبات موجودی.
4. قید تاریخ خروج `booking_check_out_gt_check_in`: قید `CHECK (check_out > check_in)`.
5. قیود مثبت بودن `rooms_count_gte_1`، `guests_count_gte_1` و `nights_gte_1`.

---

### ۳.۷. مدل نظرات مهمانان (`apps.reviews.models.Review` - بخش امتیازی)
- **هدف:** ثبت ارزیابی و امتیازدهی ۱ تا ۵ ستاره مهمانان نسبت به اقامت در هتل.

| فیلد | نوع داده در جنگو | نوع داده در PostgreSQL | اختیاری؟ | توضیحات |
|---|---|---|:---:|---|
| `id` | `BigAutoField` | `bigserial PRIMARY KEY` | خیر | شناسه کلید اصلی |
| `hotel_id` | `ForeignKey(Hotel)` | `bigint REFERENCES hotels_hotel` | خیر | هتل مورد ارزیابی (`CASCADE`) |
| `user_id` | `ForeignKey(User)` | `integer REFERENCES accounts_user` | خیر | مهمان ثبت‌کننده نظر (`CASCADE`) |
| `rating` | `PositiveSmallIntegerField`| `smallint` | خیر | امتیاز هتل از ۱ تا ۵ ستاره |
| `comment` | `TextField` | `text` | بله | متن نظر و بازخورد مهمان |
| `created_at` | `DateTimeField` | `timestamp with time zone` | خیر | زمان ثبت نظر |
| `updated_at` | `DateTimeField` | `timestamp with time zone` | خیر | زمان آخرین ویرایش |

#### قیود دیتابیسی مدل Review:
1. قید یکتایی `unique_hotel_user_review`: قید `UNIQUE (hotel_id, user_id)` مانع از ثبت چندباره نظر توسط یک کاربر برای همان هتل می‌شود.
2. قید امتیاز `review_rating_1_to_5`: قید `CHECK (rating >= 1 AND rating <= 5)`.


---



<!-- SECTION BREAK: managers.md -->


# بخش ۴: معرفی Managerها و QuerySetهای سفارشی و دلایل تعریف آن‌ها

در چارچوب معماری جنگو (Django)، کلاس‌های `Model Manager` و `QuerySet` رابط اصلی ارتباطی میان کدهای پایتون و لایه پایگاه داده (ORM) هستند. در این پروژه جهت رعایت اصول مهندسی نرم‌افزار، به‌ویژه **DRY (Don't Repeat Yourself)**، **SoC (Separation of Concerns)** و اصل **Encapsulation**، تمامی منطق‌های تجاری (Business Logic) مربوط به واکشی، فیلترسازی و محاسبات آماری و اعتبارسنجی داده‌ها از لایه Viewها و Formها منتزع شده و در قالب Managerها و QuerySetهای سفارشی پیاده‌سازی شده‌اند.

---

## ۱. جدول خلاصه Managerها و QuerySetهای پروژه

| اپلیکیشن (App) | نام کلاس | نوع کلاس | مدل مربوطه | متدهای اصلی |
|---|---|---|---|---|
| **accounts** | `UserQuerySet` | `models.QuerySet` | `User` | `.managers()`, `.guests()` |
| **accounts** | `UserManager` | `DefaultUserManager` | `User` | `create_user()`, `create_superuser()` |
| **hotels** | `HotelQuerySet` | `models.QuerySet` | `Hotel` | `.active()`, `.in_city()`, `.owned_by()`, `.with_min_price()`, `.priced_between()` |
| **hotels** | `RoomTypeQuerySet` | `models.QuerySet` | `RoomType` | `.with_availability()`, `.available_in_range()`, `.for_hotel()`, `.owned_by()` |
| **bookings** | `DiscountCodeQuerySet` | `models.QuerySet` | `DiscountCode` | `.valid_now()`, `.get_valid()`, `.for_hotel()`, `.owned_by()` |
| **bookings** | `DiscountCodeManager` | `models.Manager` | `DiscountCode` | مشتق‌شده از `DiscountCodeQuerySet` به عنوان رابط پیش‌فرض `objects` |
| **bookings** | `BookingQuerySet` | `models.QuerySet` | `Booking` | `.active()`, `.overlapping()`, `.for_hotel()`, `.for_guest()` |

---

## ۲. بررسی تفصیلی کلاس‌ها و دلایل تعریف (WHY / Rationale)

### ۲.۱. اپلیکیشن `accounts`

#### الف) کلاس `UserQuerySet`
این کلاس برای فیلترسازی کاربران بر اساس نقش‌های سامانه تعریف شده است:
- **متد `managers()`:**
  - **عملکرد:** کاربران دارای نقش مدیر هتل (`role=Role.MANAGER`) را فیلتر می‌کند.
  - **دلیل تعریف (WHY):** حذف رشته‌های جادویی (Magic Strings) نظیر `role="manager"` از سطح ویوها و دسترسی‌ها، و متمرکزسازی منطق شناسایی مدیران در یک نقطه واحد.
- **متد `guests()`:**
  - **عملکرد:** کاربران دارای نقش مهمان (`role=Role.GUEST`) را فیلتر می‌کند.
  - **دلیل تعریف (WHY):** جلوگیری از تکرار فیلتر `role="guest"` در بخش گزارش‌ها، لیست مسافران و ارسال اعلان‌ها.

#### ب) کلاس `UserManager`
مدیر اختصاصی مدل کاربر که از ترکیب `DefaultUserManager` با `UserQuerySet` حاصل شده است:
- **متد `create_user(username, email=None, password=None, **extra_fields)`:**
  - **عملکرد:** مقداردهی پیش‌فرض نقش کاربر به `Role.GUEST` در صورت عدم تعیین، و اعتبارسنجی الزامی بودن ایمیل.
  - **دلیل تعریف (WHY):** تضمین این‌که هیچ کاربری بدون ایمیل معتبر یا با نقش نامعتبر در پایگاه داده ایجاد نشود.
- **متد `create_superuser(username, email=None, password=None, **extra_fields)`:**
  - **عملکرد:** تخصیص اجباری نقش `Role.MANAGER` به حساب‌های مدیر کل سیستم (Superuser).
  - **دلیل تعریف (WHY):** اطمینان از سازگاری دسترسی‌های پنل مدیریت هتل با دسترسی‌های سطح ریشه جنگو بدون ایجاد تضاد نقشی.

---

### ۲.۲. اپلیکیشن `hotels`

#### الف) کلاس `HotelQuerySet`
این کلاس برای مدیریت هتل‌ها در هر دو سمت کاربری (مهمانان و مدیران هتل) طراحی شده است:
- **متد `active()`:**
  - **عملکرد:** فیلتر هتل‌هایی که وضعیت `is_active=True` دارند.
  - **دلیل تعریف (WHY):** هتل‌های غیرفعال‌شده نباید در جستجوها و رزروهای مهمانان دیده شوند؛ تمرکز این فیلتر از نشت اطلاعات هتل‌های غیرفعال جلوگیری می‌کند.
- **متد `in_city(city)`:**
  - **عملکرد:** پاک‌سازی فاصله‌های اضافی ورودی (`strip`) و فیلتر بدون حساسیت به حروف بزرگ و کوچک (`city__iexact`).
  - **دلیل تعریف (WHY):** استانداردسازی جستجوی شهرها در ورودی کاربر و جلوگیری از خطای ناشی از تفاوت فاصله‌گذاری یا حروف کوچک/بزرگ در مقادیر ورودی.
- **متد `owned_by(user)`:**
  - **عملکرد:** استخراج هتل‌های متعلق به مدیر لاگین‌شده (`owner=user`).
  - **دلیل تعریف (WHY):** برقراری مرزبندی امنیتی (Tenant Isolation) و جلوگیری قطعی از آسیب‌پذیری نشت و تغییر اطلاعات میان مدیران مختلف (Horizontal Privilege Escalation).
- **متد `with_min_price()`:**
  - **عملکرد:** الحاق فیلد محاسباتی `min_price` با استفاده از تابع تجمیعی `models.Min('room_types__price_per_night')`.
  - **دلیل تعریف (WHY):** در کارت‌های نتایج جستجو، عبارت «شروع قیمت از X تومان» نمایش داده می‌شود. محاسبه این مقدار با یک کوئری SQL در سطح دیتابیس انجام می‌شود و مشکل شناخته‌شده **N+1 Queries** را کاملاً ریشه‌کن می‌کند.
- **متد `priced_between(min_price, max_price)`:**
  - **عملکرد:** اعمال فیلتر بازه قیمت روی انواع اتاق‌های یک هتل به صورت اتمیک در یک فراخوانی `filter(...)`.
  - **دلیل تعریف (WHY):** در Django ORM، زنجیره‌سازی دو فیلتر جداگانه روی رابطه معکوس چندبه‌یک باعث ایجاد دو JOIN مجزا می‌شود که ممکن است رکوردهای نادرست را تطبیق دهد. ترکیب هر دو حد در یک شرط تکی، تضمین می‌کند که حداقل یک اتاق خاص درون بازه انتخابی قرار دارد.

#### ب) کلاس `RoomTypeQuerySet`
این کلاس وظیفه استعلام و مدیریت موجودی اتاق‌ها را بر عهده دارد:
- **متد `with_availability(check_in, check_out)`:**
  - **عملکرد:** با استفاده از `Subquery` و `Coalesce`، تعداد اتاق‌های رزرو شده در بازه زمانی را محاسبه کرده و فیلدهای `reserved` و `available_count` را به کوئری الحاق می‌کند.
  - **دلیل تعریف (WHY):** محاسبه برخط ظرفیت آزاد اتاق‌ها مستقیماً در پایگاه داده بدون نیاز به بارگذاری تمام رکوردها در حافظه پایتون، که سرعت پاسخ‌دهی به جستجوها را به شدت افزایش می‌دهد.
- **متد `available_in_range(check_in, check_out, rooms_count)`:**
  - **عملکرد:** اتاق‌هایی که حداقل به اندازه `rooms_count` ظرفیت خالی دارند را فیلتر می‌کند.
  - **دلیل تعریف (WHY):** تسهیل زنجیره‌سازی در ویوهای جستجو و بازگرداندن اتاق‌های واقعاً قابل رزرو به مسافر.
- **متد `for_hotel(hotel)` و `owned_by(user)`:**
  - **عملکرد:** فیلتر انواع اتاق متعلق به هتل یا متعلق به مدیر مشخص.
  - **دلیل تعریف (WHY):** تضمین کنترل دسترسی و سادگی کد در ویوهای مدیریت اتاق‌ها.

---

### ۲.۳. اپلیکیشن `bookings`

#### الف) کلاس‌های `DiscountCodeQuerySet` و `DiscountCodeManager`
این کلاس‌ها مدیریت کدهای تخفیف هتل را متمرکز می‌کنند:
- **متد `valid_now(hotel, today)`:**
  - **عملکرد:** فیلتر کدهای تخفیف فعال هتل که تاریخ امروز در بازه `valid_from` تا `valid_to` قرار داشته و تعداد استفاده‌های آن کمتر از `max_uses` باشد (`used_count < max_uses`).
  - **دلیل تعریف (WHY):** متمرکزسازی تمام قیود زمانی و سهمیه‌ای تخفیف (تصمیم معماری D-004) در لایه مدل، به طوری که در استعلام قیمت (Quote) و ثبت رزرو هیچ تکراری در شرط‌ها وجود نداشته باشد.
- **متد `get_valid(hotel, code, today)`:**
  - **عملکرد:** نرمال‌سازی کد (حذف فضاها و تبدیل به حروف بزرگ) و بازگرداندن رکورد تخفیف معتبر یا `None`.
  - **دلیل تعریف (WHY):** پاک‌سازی کد و انتقال منطق بررسی صحت کوپن از لایه فرم/ویو به لایه منیجر با لاگ‌گذاری جزئیات جهت حسابرسی امنیتی.
- **متد `owned_by(user)` و `for_hotel(hotel)`:**
  - **عملکرد:** محدودسازی دسترسی مدیر به کدهای تخفیف هتل‌های خودش.
  - **دلیل تعریف (WHY):** جلوگیری از دسترسی مدیران دیگر به کدهای تخفیف تعریف‌شده توسط یک مدیر.

#### ب) کلاس `BookingQuerySet`
این کلاس هسته مرکزی استعلام و گزارش‌گیری رزروهای مسافران و هتل‌داران است:
- **متد `active()`:**
  - **عملکرد:** فیلتر رزروهای دارای وضعیت تأییدشده (`status=Booking.Status.CONFIRMED`).
  - **دلیل تعریف (WHY):** تنها رزروهای قطعی ظرفیت اتاق را مسدود می‌کنند؛ رزروهای لغوشده (`CANCELLED`) ظرفیت را آزاد می‌کنند. بنابراین فیلتر `active()` پایه و اساس تمامی محاسبات ظرفیت و تقویم است.
- **متد `overlapping(check_in, check_out)`:**
  - **عملکرد:** فیلتر رزروهایی که با بازه مدنظر مسافر یا مدیر تداخل دارند، با شرط دقیق `check_in < req_out AND check_out > req_in`.
  - **دلیل تعریف (WHY):** پیاده‌سازی فرمول ریاضی همپوشانی بازه‌های زمانی نیمه‌باز (تصمیم معماری D-006). این منطق تضمین می‌کند مسافری که صبح روز پنجم خارج می‌شود و مسافری که عصر همان روز وارد می‌شود تداخل نداشته باشند (Same-day Turnover).
- **متد `for_hotel(hotel)`:**
  - **عملکرد:** فیلتر رزروهای مربوط به یک هتل مشخص.
  - **دلیل تعریف (WHY):** ساده‌سازی واکشی رزروها بدون نیاز به نوشتن دستی JOIN میان `room_type` و `hotel`.
- **متد `for_guest(user)`:**
  - **عملکرد:** فیلتر رزروهای ثبت‌شده توسط یک کاربر مهمان.
  - **دلیل تعریف (WHY):** استفاده در صفحه «رزروهای من» مسافر و تضمین این‌که هیچ مهمانی قادر به دیدن رزروهای دیگران نباشد.

---

## ۳. مقایسه قبل و بعد از استفاده از Managerها (کاهش پیچیدگی و خطوط کد)

### نمونه ۱: استعلام هتل‌ها در جستجوی عمومی
**قبل از تعریف Manager:**
```python
# ویو باید چندین شرط تکراری، نرمال‌سازی دستی و محاسبه N+1 انجام می‌داد:
hotels = Hotel.objects.filter(is_active=True)
if city:
    hotels = hotels.filter(city__iexact=city.strip())
# برای هر هتل در یک حلقه پایتون کمترین قیمت حساب می‌شد (N+1 Query Problem!)
```

**بعد از تعریف Manager:**
```python
# تمام دغدغه‌ها در یک کوئری خوانا، بهینه و زنجیره‌پذیر ترکیب می‌شوند:
hotels = Hotel.objects.active().in_city(city).with_min_price()
if min_price or max_price:
    hotels = hotels.priced_between(min_price, max_price)
```

### نمونه ۲: اعتبارسنجی کد تخفیف در فرآیند رزرو
**قبل از تعریف Manager:**
```python
now = timezone.localdate()
discount = DiscountCode.objects.filter(
    hotel=hotel,
    code=code.strip().upper(),
    is_active=True,
    valid_from__lte=now,
    valid_to__gte=now
).filter(Q(max_uses__isnull=True) | Q(used_count__lt=F('max_uses'))).first()
```

**بعد از تعریف Manager:**
```python
# تمام شروط در متد تخصصی منیجر تجمیع شده است:
discount = DiscountCode.objects.get_valid(hotel=hotel, code=code)
```

---

## ۴. نتایج آزمون‌های واحد (Unit Testing)
برای اطمینان از صحت کامل عملکرد Managerها و QuerySetها، آزمون‌های اختصاصی در تمام اپلیکیشن‌ها پیاده‌سازی شدند:
- در اپلیکیشن `accounts`: کلاس `UserQuerySetTestCase` رفتار متدهای `.managers()`، `.guests()` و خطاهای اعتبارسنجی را بررسی می‌کند.
- در اپلیکیشن `hotels`: کلاس `HotelQuerySetTestCase` و `RoomTypeQuerySetAvailabilityTests` درستی فیلترهای شهر، قیمت، زنجیره‌سازی و محاسبات همپوشانی را می‌سنجند.
- در اپلیکیشن `bookings`: کلاس `BookingQuerySetAndDiscountManagerTests` صحت همپوشانی تاریخ‌ها، فیلترهای رزرو فعال، سقف مصرف کوپن‌ها و اسکوپ‌های دسترسی را تأیید می‌کند.
- **نتیجه اجرای آزمون‌ها:** مجموع ۲۹۹ تست با موفقیت کامل پاس شده‌اند (`Ran 299 tests ... OK`).


---



<!-- SECTION BREAK: views.md -->


# بخش پنجم گزارش نهایی: معرفی Viewها و رابط‌های برنامه‌نویسی وب (Views & Web APIs)

این بخش به تشریح کامل لایه کنترلر و وب در معماری سامانه رزرواسیون هتل می‌پردازد. در این پروژه، کلیه Viewها با استفاده از ویوهای مبتنی بر تابع استاندارد جنگو (Plain Django Function-Based Views) پیاده‌سازی شده و بدون استفاده از کتابخانه‌های حجیم شخص ثالث (مانند Django Rest Framework)، پاسخ‌های استاندارد JSON با پوشش هماهنگ تولید می‌کنند.

---

## ۱. فلسفه طراحی و معماری لایه Views

بر اساس تصمیم‌های معماری پروژه (به‌ویژه تصمیم‌های `D-001` و `D-002` در سند `DECISIONS.md`)، اصول زیر در طراحی تمامی Viewها رعایت شده‌اند:
1. **جداسازی کامل مسئولیت‌ها (Fat Models & Managers, Thin Views):** ویوها صرفاً وظیفه دریافت درخواست، اعتبارسنجی اولیه با استفاده از فرم‌های جنگو، فراخوانی متدهای تخصصی در لایه QuerySet/Manager و بازگرداندن پاسخ خروجی را بر عهده دارند و هیچ‌گونه محاسبات پیچیده تجاری در بدنه ویوها قرار نگرفته است.
2. **اعتبارسنجی اکید داده‌های ورودی با Django Forms:** هیچ داده ورودی به صورت مستقیم و خام (Raw JSON) مورد پردازش قرار نمی‌گیرد؛ کلیه اندپوینت‌های تغییردهنده وضعیت (Write Endpoints) با استفاده از کلاس‌های `Form` یا `ModelForm` جنگو اعتبارسنجی می‌شوند.
3. **پوشش یکنواخت پاسخ‌های وب (Standard JSON Envelope):** کلیه پاسخ‌های موفق در ساختار `{"data": ...}` با وضعیت `200` یا `201`، و کلیه پاسخ‌های خطا در ساختار `{"error": "message", "errors": {...}}` با کدهای وضعیت مناسب (`400`, `401`, `403`, `404`, `409`, `500`) ارسال می‌شوند.
4. **تراکنش‌های اتمیک و کنترل همزمانی (Concurrency Control & ACID):** عملیات‌های بحرانی نظیر ثبت رزرو در بلوک `transaction.atomic()` و با قفل‌گذاری بدبینانه ردیف‌ها (`select_for_update()`) پیاده‌سازی شده‌اند تا از رزرو مازاد (Overbooking) در محیط‌های چندکاربره کاملاً پیشگیری شود.
5. **ایزولاسیون چندمستأجری (Multi-Tenant Isolation):** دسترسی مدیران هتل به هتل‌ها، اتاق‌ها، رزروها و تخفیف‌ها به صورت قطعی از طریق فیلترهای اسکوپ‌بندی شده مدل (`owned_by(request.user)`) ایزوله شده است.

---

## ۲. جدول جامع تمامی Viewهای سامانه

| شماره | اپلیکیشن | نام تابع View | مسیر (URL Path) | متدهای HTTP | سطح دسترسی و نقش | فرم اعتبارسنجی | Manager یا QuerySet مورد استفاده |
|:---:|:---:|:---|:---|:---:|:---|:---|:---|
| **۱** | `core` | `health_check` | `/api/health/` | `GET` | عمومی (Public) | - | - |
| **۲** | `core` | `csrf_token_view` | `/api/auth/csrf/` | `GET` | عمومی (Public) | - | - |
| **۳** | `core` | `spa_host_view` | `/*` (Catch-all) | `GET` | عمومی (Public) | - | - |
| **۴** | `accounts` | `register_view` | `/api/auth/register/` | `POST` | عمومی (Public) | `RegisterForm` | `User.objects.create_user()` |
| **۵** | `accounts` | `login_view` | `/api/auth/login/` | `POST` | عمومی (Public) | `LoginForm` | `authenticate()` |
| **۶** | `accounts` | `logout_view` | `/api/auth/logout/` | `POST` | لاگین‌شده | - | - |
| **۷** | `accounts` | `me_view` | `/api/auth/me/` | `GET` | عمومی / احرازشده | - | - |
| **۸** | `accounts` | `verify_email_view` | `/api/auth/verify-email/` | `POST` | عمومی (Public) | اعتبارسنجی امضای دیجیتال توکن | `User.objects.filter()` |
| **۹** | `accounts` | `resend_verification_view` | `/api/auth/resend-verification/` | `POST` | لاگین‌شده | - | - |
| **۱۰** | `hotels` | `cities_list_view` | `/api/cities/` | `GET` | عمومی (Public) | - | `Hotel.objects.active().distinct()` |
| **۱۱** | `hotels` | `hotels_list_view` | `/api/hotels/` | `GET` | عمومی (Public) | `SearchForm` | `Hotel.objects.active().in_city().with_min_price()`, `RoomType.objects.with_availability()` |
| **۱۲** | `hotels` | `recent_hotels_view` | `/api/hotels/recent/` | `GET` | عمومی (Public) | - | `Hotel.objects.active().with_min_price()` |
| **۱۳** | `hotels` | `hotel_detail_view` | `/api/hotels/<id>/` | `GET` | عمومی (Public) | - | `Hotel.objects.active()`, `RoomType.objects.for_hotel()` |
| **۱۴** | `hotels` | `hotel_rooms_view` | `/api/hotels/<id>/rooms/` | `GET` | عمومی (Public) | `RoomSearchForm` | `RoomType.objects.for_hotel().with_availability()` |
| **۱۵** | `hotels` | `room_detail_view` | `/api/rooms/<id>/` | `GET` | عمومی (Public) | - | `RoomType.objects.filter()` |
| **۱۶** | `hotels` | `amenities_list_view` | `/api/amenities/` | `GET` | عمومی (Public) | - | `Amenity.objects.all()` |
| **۱۷** | `hotels` | `manager_hotels_list_create_view` | `/api/manager/hotels/` | `GET`, `POST` | مدیر هتل (`manager`) | `HotelForm` | `Hotel.objects.owned_by()` |
| **۱۸** | `hotels` | `manager_hotel_detail_update_delete_view` | `/api/manager/hotels/<id>/` | `GET`, `PUT`, `DELETE` | مدیر هتل (`manager`) | `HotelForm` | `Hotel.objects.owned_by()` |
| **۱۹** | `hotels` | `manager_room_types_list_create_view` | `/api/manager/hotels/<id>/room-types/` | `GET`, `POST` | مدیر هتل (`manager`) | `RoomTypeForm` | `RoomType.objects.owned_by()`, `Hotel.objects.owned_by()` |
| **۲۰** | `hotels` | `manager_room_type_detail_update_delete_view` | `/api/manager/room-types/<id>/` | `GET`, `PUT`, `DELETE` | مدیر هتل (`manager`) | `RoomTypeForm` | `RoomType.objects.owned_by()` |
| **۲۱** | `bookings` | `quote_view` | `/api/bookings/quote/` | `POST` | عمومی / مهمان | `BookingQuoteForm` | `RoomType.objects.with_availability()`, `DiscountCode.objects.get_valid()` |
| **۲۲** | `bookings` | `discount_validate_view` | `/api/discounts/validate/` | `POST` | عمومی / مهمان | `DiscountValidateForm` | `DiscountCode.objects.get_valid()` |
| **۲۳** | `bookings` | `booking_create_view` | `/api/bookings/` | `POST` | مهمان تاییدشده (`guest`, `verified`) | `BookingQuoteForm` | `Booking.objects.active().overlapping()`, `DiscountCode.objects.get_valid()` |
| **۲۴** | `bookings` | `my_bookings_list_view` | `/api/bookings/mine/` | `GET` | مهمان (`guest`) | - | `Booking.objects.for_guest()` |
| **۲۵** | `bookings` | `booking_cancel_view` | `/api/bookings/<id>/cancel/` | `POST` | مهمان (`guest`) | - | `Booking.objects.for_guest()`, `Booking.objects.filter()` |
| **۲۶** | `bookings` | `manager_discounts_list_create_view` | `/api/manager/hotels/<id>/discounts/` | `GET`, `POST` | مدیر هتل (`manager`) | `DiscountCodeForm` | `DiscountCode.objects.for_hotel().owned_by()` |
| **۲۷** | `bookings` | `manager_discount_detail_update_delete_view` | `/api/manager/discounts/<id>/` | `GET`, `PUT`, `DELETE` | مدیر هتل (`manager`) | `DiscountCodeForm` | `DiscountCode.objects.owned_by()` |
| **۲۸** | `bookings` | `manager_hotel_bookings_list_view` | `/api/manager/hotels/<id>/bookings/` | `GET` | مدیر هتل (`manager`) | `ManagerBookingFilterForm` | `Booking.objects.for_hotel()`, `Hotel.objects.owned_by()` |
| **۲۹** | `bookings` | `manager_hotel_availability_view` | `/api/manager/hotels/<id>/availability/` | `GET` | مدیر هتل (`manager`) | `ManagerAvailabilityFilterForm` | `Booking.objects.active().for_hotel().overlapping()`, `RoomType.objects.for_hotel()` |

---

## ۳. بررسی تفصیلی Viewها به تفکیک ماژول‌ها

### ۳.۱. اپلیکیشن `core` (هسته سامانه و زیرساخت ارتباطی)

#### ۱. `health_check`
- **مسیر و متد:** `GET /api/health/`
- **مجوز دسترسی:** عمومی (Public)
- **هدف و عملکرد:** ارائه اندپوینت نظارت بر سلامت سامانه برای ابزارهای مانیتورینگ و لود بالانسر.
- **خروجی:** بازگرداندن پاسخ `200 OK` با بدنه `{"data": {"status": "ok"}}`.

#### ۲. `csrf_token_view`
- **مسیر و متد:** `GET /api/auth/csrf/`
- **دکوراتورها:** `@require_GET`, `@ensure_csrf_cookie`
- **هدف و عملکرد:** ارسال کوکی `csrftoken` و مقدار صریح آن در بدنه JSON جهت تغذیه کلاینت SPA فرانت‌اند در بدو ورود.

#### ۳. `spa_host_view`
- **مسیر و متد:** `GET /*` (Regex Pattern: `^(?!api/|admin/|static/|media/).*$`)
- **دکوراتورها:** `@require_GET`, `@ensure_csrf_cookie`
- **هدف و عملکرد:** رندر قالب `index.html` برای مدیریت مسیریابی سمت کلاینت (HTML5 PushState / React Router).

#### ۴. هندلرهای اختصاصی خطاهای HTTP (`bad_request_view`, `permission_denied_view`, `page_not_found_view`, `server_error_view`)
- **کدهای وضعیت:** `400`, `403`, `404`, `500`
- **هدف و عملکرد:** در صورتی که مسیر درخواست با `/api/` آغاز شود، خطای استاندارد JSON بازمی‌گردانند تا کلاینت فرانت‌اند هرگز با صفحات HTML پیش‌فرض جنگو در هنگام بروز خطا مواجه نشود.

---

### ۳.۲. اپلیکیشن `accounts` (احراز هویت و حساب کاربری)

#### ۱. `register_view`
- **مسیر و متد:** `POST /api/auth/register/`
- **مجوز دسترسی:** عمومی
- **فرم اعتبارسنجی:** `RegisterForm` (بررسی یکتایی نام کاربری و ایمیل، تطابق گذرواژه و پیچیدگی رمز عبور)
- **منیجر و منطق کسب‌وکار:** استفاده از `User.objects.create_user()`، صدور توکن امضاشده کریپتوگرافیک توسط ماژول `tokens.py` و ارسال ایمیل فعال‌سازی دو مرحله‌ای در قالب چندبخشی (Multipart HTML/TXT).
- **لاگین امنیتی:** ثبت رویداد با نام کاربری، ایمیل و نقش در `apps.security`.

#### ۲. `login_view`
- **مسیر و متد:** `POST /api/auth/login/`
- **فرم اعتبارسنجی:** `LoginForm` (پشتیبانی از ورود هم با نام کاربری و هم با آدرس ایمیل)
- **منطق سشن و ماندگاری:** استفاده از `login(request, user)`؛ در صورت انتخاب گزینه `remember_me`، انقضای سشن به ۱۴ روز (۱,۲۰۹,۶۰۰ ثانیه) تنظیم می‌شود؛ در غیر این صورت سشن با بستن مرورگر کاربر منقضی می‌گردد (`expiry=0`). همچنین زمان آخرین لاگین در کلید `last_login` در سشن ذخیره می‌گردد.
- **رعایت قوانین امنیتی:** بر اساس قانون شماره ۹ پروژه، هرگز گذرواژه واردشده در لاگ‌ها ثبت نمی‌شود و تنها شناسه کاربر و IP لاگ می‌گردد.

#### ۳. `logout_view`
- **مسیر و متد:** `POST /api/auth/logout/`
- **دکوراتور:** `@login_required_json`
- **عملکرد:** فراخوانی `request.session.flush()` جهت پاک‌سازی قطعی داده‌های سشن در بک‌اند و سپس `logout(request)`.

#### ۴. `me_view`
- **مسیر و متد:** `GET /api/auth/me/`
- **عملکرد:** بررسی وضعیت احراز هویت؛ در صورت ورود کاربر، دیکشنری مشخصات کاربر به همراه نقش (`role`)، وضعیت تایید ایمیل (`email_verified`) و `last_login` بازگردانده می‌شود؛ در صورت ناشناس بودن، `{"data": null}` با کد `200` بازمی‌گردد.

#### ۵. `verify_email_view`
- **مسیر و متد:** `POST /api/auth/verify-email/`
- **منطق امنیتی:** رمزگشایی و اعتبارسنجی امضای دیجیتال توکن با کلاس `TimestampSigner` جنگو. در صورت انقضای مهلت زمانی (۴۸ ساعت) خطای منقضی‌شدن و در صورت جعل یا دستکاری توکن خطای اعتبارسنجی صادر می‌شود. با تایید موفق، فیلد `email_verified=True` به‌روزرسانی اتمیک می‌گردد.

#### ۶. `resend_verification_view`
- **مسیر و متد:** `POST /api/auth/resend-verification/`
- **دکوراتور:** `@login_required_json`
- **عملکرد:** تولید توکن جدید و ارسال مجدد ایمیل فعال‌سازی در صورت عدم تایید قبلی.

---

### ۳.۳. اپلیکیشن `hotels` (جستجو و مدیریت اقامتگاه‌ها)

#### ۱. `cities_list_view`
- **مسیر و متد:** `GET /api/cities/`
- **منیجر مورد استفاده:** `Hotel.objects.active().values_list("city", flat=True).distinct()`
- **عملکرد:** استخراج فهرست الفبایی شهرهایی که حداقل یک هتل فعال دارند جهت پر کردن منوی کرکره‌ای در نوار جستجوی صفحه اصلی.

#### ۲. `hotels_list_view`
- **مسیر و متد:** `GET /api/hotels/`
- **فرم اعتبارسنجی:** `SearchForm` (اعتبارسنجی تاریخ‌های ورود و خروج، تعداد مسافران، بازه قیمت و عبارت جستجو)
- **منیجر و کوئری بهینه:**
  - استفاده همزمان از `Hotel.objects.active().in_city(city).with_min_price()`
  - الحاق بهینه ظرفیت اتاق‌ها با `Prefetch("room_types", queryset=RoomType.objects.with_availability(check_in, check_out))`
  - این ترکیب از بروز خطای **N+1 Queries** کاملاً جلوگیری کرده و کمترین قیمت و موجودی را در قالب یک فراخوانی بهینه پایگاه داده محاسبه می‌کند.
- **کوکی سابقه:** تنظیم کوکی `last_city` با طول عمر ۳۰ روز جهت یادآوری آخرین جستجوی کاربر در مراجعات بعدی.

#### ۳. `recent_hotels_view`
- **مسیر و متد:** `GET /api/hotels/recent/`
- **منطق سشن:** خواندن لیست شناسه‌های ذخیره‌شده در `request.session["recent_hotels"]` و واکشی اطلاعات هتل‌ها با `with_min_price()`.

#### ۴. `hotel_detail_view`
- **مسیر و متد:** `GET /api/hotels/<hotel_id>/`
- **عملکرد:** واکشی مشخصات کامل هتل، تمامی انواع اتاق‌ها و امکانات رفاهی؛ الحاق شناسه هتل به سشن `recent_hotels` با حفظ ترتیب مراجعات اخیر و حداکثر سقف ۵ هتل.

#### ۵. `hotel_rooms_view`
- **مسیر و متد:** `GET /api/hotels/<hotel_id>/rooms/`
- **فرم اعتبارسنجی:** `RoomSearchForm`
- **منیجر:** `RoomType.objects.for_hotel(hotel).with_availability(check_in, check_out).prefetch_related("amenities")`
- **عملکرد:** محاسبه برخط تعداد اتاق‌های آزاد هر نوع اتاق برای بازه تاریخی مشخص‌شده بدون نیاز به محاسبات دستی در پایتون.

#### ۶. `amenities_list_view`
- **مسیر و متد:** `GET /api/amenities/`
- **عملکرد:** بازگرداندن کاتالوگ جامع امکانات رفاهی هتل (وای‌فای، استخر، صبحانه، پارکینگ، باشگاه و...) جهت انتساب در فرم‌های تعریف اتاق توسط مدیر.

#### ۷. اندپوینت‌های پنل مدیریت هتل (`manager_hotels_list_create_view`, `manager_hotel_detail_update_delete_view`)
- **مسیرها:** `GET, POST /api/manager/hotels/` و `GET, PUT, DELETE /api/manager/hotels/<hotel_id>/`
- **دکوراتورها:** `@login_required_json`, `@role_required(Role.MANAGER)`
- **فرم اعتبارسنجی:** `HotelForm` (اعتبارسنجی نام، شهر، آدرس، مختصات جغرافیایی و امتیاز ستاره)
- **منیجر و ایزولاسیون:** `Hotel.objects.owned_by(request.user)`. هر مدیر صرفاً قادر به مشاهده، ویرایش یا حذف هتل‌های تحت مالکیت خود می‌باشد. درخواست دسترسی به هتل سایر مدیران با خطای `404 Not Found` پاسخ داده می‌شود تا هویت داده‌ها نشت نکند.

#### ۸. اندپوینت‌های مدیریت انواع اتاق (`manager_room_types_list_create_view`, `manager_room_type_detail_update_delete_view`)
- **مسیرها:** `/api/manager/hotels/<hotel_id>/room-types/` و `/api/manager/room-types/<room_type_id>/`
- **فرم اعتبارسنجی:** `RoomTypeForm` (اعتبارسنجی عنوان، ظرفیت نفرات، قیمت هر شب، تعداد کل اتاق‌ها و امکانات)
- **منیجر:** `RoomType.objects.owned_by(request.user)` به صورت زنجیره‌شده با هتل مربوطه.

---

### ۳.۴. اپلیکیشن `bookings` (رزرواسیون، استعلام قیمت و تخفیف‌ها)

#### ۱. `quote_view`
- **مسیر و متد:** `POST /api/bookings/quote/`
- **فرم اعتبارسنجی:** `BookingQuoteForm` (بررسی ترتیب تاریخی `check_in < check_out`، معتبر بودن نوع اتاق و ظرفیت نفرات)
- **سرویس و منیجر:** فراخوانی `services.calculate_booking_quote`، استعلام ظرفیت آزاد از `RoomType.objects.with_availability` و اعتبارسنجی کوپن از `DiscountCode.objects.get_valid(hotel, code)`.
- **خروجی:** بازگرداندن پیش‌فاکتور شامل تعداد شب‌ها، قیمت پایه، مبلغ و درصد تخفیف اعمال‌شده، و قیمت نهایی قابل پرداخت.

#### ۲. `discount_validate_view`
- **مسیر و متد:** `POST /api/discounts/validate/`
- **فرم اعتبارسنجی:** `DiscountValidateForm`
- **منیجر:** `DiscountCode.objects.get_valid(hotel, code)`
- **عملکرد:** بررسی آنی فعال بودن کد تخفیف در رویداد خروج فوکوس (onBlur) اینپوت در فرانت‌اند با متد AJAX.

#### ۳. `booking_create_view` (هسته تراکنشی سامانه)
- **مسیر و متد:** `POST /api/bookings/`
- **دکوراتورها:** `@login_required_json`, `@role_required(Role.GUEST)`, `@verified_required`
- **فرم اعتبارسنجی:** `BookingQuoteForm`
- **کنترل همزمانی و تراکنش (ACID & Concurrency):**
  - اجرای سراسری در بلوک `with transaction.atomic():`
  - اعمال قفل بدبینانه روی ردیف نوع اتاق: `RoomType.objects.select_for_update().get(id=...)`
  - استعلام همپوشانی رزروهای قطعی با متد منیجر: `Booking.objects.active().filter(room_type=room_type).overlapping(check_in, check_out)`
  - محاسبه موجودی باقی‌مانده؛ در صورت ناکافی بودن ظرفیت، لغو تراکنش و بازگرداندن خطای `409 Conflict`.
  - در صورت وجود کد تخفیف: قفل‌گذاری روی سطر تخفیف با `select_for_update()`، تایید عدم اتمام سقف مجاز و افزایش اتمیک `used_count` با `F("used_count") + 1`.
  - ارسال ایمیل تاییدیه رزرو در رویداد `transaction.on_commit` جهت اطمینان از پایدار شدن رزرو در پایگاه داده قبل از ارسال ایمیل.

#### ۴. `my_bookings_list_view`
- **مسیر و متد:** `GET /api/bookings/mine/`
- **دکوراتور:** `@login_required_json`, `@role_required(Role.GUEST)`
- **منیجر:** `Booking.objects.for_guest(request.user).select_related("room_type__hotel")`
- **عملکرد:** فهرست‌سازی تاریخچه رزروهای مسافر با جزئیات کامل هتل و اتاق.

#### ۵. `booking_cancel_view`
- **مسیر و متد:** `POST /api/bookings/<booking_id>/cancel/`
- **دکوراتور:** `@login_required_json`, `@role_required(Role.GUEST)`
- **منیجر و تراکنش:**
  - واکشی رزرو با `Booking.objects.for_guest(request.user).filter(id=booking_id).first()`
  - در صورت لغو: اجرای اتمیک تغییر وضعیت به `status = Booking.Status.CANCELLED` و کسر خودکار `used_count` کد تخفیف در صورت استفاده با شرط `F("used_count") - 1`.

#### ۶. اندپوینت‌های مدیریت کدهای تخفیف (`manager_discounts_list_create_view`, `manager_discount_detail_update_delete_view`)
- **مسیرها:** `/api/manager/hotels/<hotel_id>/discounts/` و `/api/manager/discounts/<discount_id>/`
- **دکوراتورها:** `@login_required_json`, `@role_required(Role.MANAGER)`
- **فرم اعتبارسنجی:** `DiscountCodeForm` (اعتبارسنجی کد، درصد تخفیف ۱ تا ۱۰۰، بازه تاریخی، سقف استفاده)
- **منیجر:** `DiscountCode.objects.for_hotel(hotel).owned_by(request.user)`.

#### ۷. `manager_hotel_bookings_list_view`
- **مسیر و متد:** `GET /api/manager/hotels/<hotel_id>/bookings/`
- **فرم فیلتر:** `ManagerBookingFilterForm` (فیلتر بر اساس وضعیت `status` و بازه تاریخی)
- **منیجر:** `Booking.objects.for_hotel(hotel).select_related("room_type", "guest", "discount_code")`.

#### ۸. `manager_hotel_availability_view`
- **مسیر و متد:** `GET /api/manager/hotels/<hotel_id>/availability/`
- **فرم فیلتر:** `ManagerAvailabilityFilterForm` (دریافت بازه تاریخی `date_from` و `date_to`)
- **منیجر و منطق ماتریسی:**
  - استعلام انواع اتاق‌های هتل با `RoomType.objects.for_hotel(hotel)`
  - استعلام تمامی رزروهای فعال بازه مدنظر با `Booking.objects.active().for_hotel(hotel).overlapping(date_from, date_to)`
  - تولید ماتریس روزانه به تفکیک تاریخ و نوع اتاق: تعداد کل اتاق‌ها (`total`)، تعداد اتاق‌های رزروشده (`reserved`) و تعداد اتاق‌های آزاد (`free`).

---

## ۴. جمع‌بندی معیارهای طراحی لایه Views

1. **انطباق ۱۰۰ درصدی با اهداف درس وب:** هیچ چارچوب جادویی و آماده‌ای در لایه وب استفاده نشده و تمامی سازوکارهای اهراز هویت بر پایه سشن، اعتبارسنجی فرم‌ها، کوکی‌ها و پاسخ‌های JSON با کدهای خالص پایتون و جنگو توسعه یافته‌اند.
2. **پوشش تست کامل:** تمامی ۲۹ View فوق در قالب ۲۷۸ تست واحد و یکپارچه در فایل‌های `tests.py` و `test_integration_flows.py` تحت پوشش آزمون‌های اتوماتیک قرار دارند.
3. **لاگ‌گذاری حسابرسی امنیتی (Security Auditing):** در کلیه نقاط حساس احراز هویت و دستکاری داده‌ها، لاگرهای اختصاصی `apps.security` و `apps.<app_name>` وقایع مهم را ثبت می‌کنند.


---



<!-- SECTION BREAK: testing.md -->


# گزارش جامع آزمون‌ها (Testing Strategy & Verification Report)

این سند معماری آزمون‌ها، استراتژی اعتبارسنجی کیفیت نرم‌افزار، جریان‌های یکپارچه انتها به انتها (End-to-End API Integration Flows) و آزمون‌های دود (Smoke Tests) کلاینت فرانت‌اند سامانه رزرواسیون هتل را مستند می‌کند.

---

## ۱. فلسفه و ساختار آزمون‌ها (Testing Pyramid & Architecture)

استراتژی آزمون سامانه رزرواسیون هتل بر پایه **هرم آزمون (Test Pyramid)** طراحی شده است:

```
          / \
         /   \       Frontend Smoke Tests (14 تست)
        / E2E \      API Integration Flows (6 سناریوی جامع E2E)
       /-------\     
      / Service \    Business Logic, Concurrency & Constraints (88 تست)
     / & Manager \   Custom Managers & QuerySets (accounts, hotels, bookings)
    /-------------\  
   /     Unit      \ Model, Forms, Token Signing & Utilities (184 تست)
  /-----------------\
```

### آمار تفکیکی تست‌های سامانه
- **تست‌های بک‌اند جنگو:** ۲۹۹ تست واحد، یکپارچه‌سازی و اعتبارسنجی کسب‌وکار (Ran 299 tests — OK)
- **تست‌های فرانت‌اند:** ۱۴ تست Smoke نرمال‌سازی کلاینت شبکه (Ran 14 tests — Pass)
- **مجموع تست‌های اتوماتیک در CI:** ۳۱۳ تست با نرخ موفقیت ۱۰۰٪

---

## ۲. جریان‌های یکپارچه API (End-to-End Integration Flows)

جریان‌های یکپارچه در فایل `backend/apps/bookings/test_integration_flows.py` پیاده‌سازی شده‌اند و با شبیه‌سازی دقیق رفتار کاربر و کلاینت وب، تمامی لایه‌های Middleware، Authentication، Permission، Form Validation، ORM Queries و Database Constraints را به طور متوالی به بوته آزمون می‌گذارند.

### ۲.۱. داستان کامل کاربر مهمان (Guest Journey Flow)
**کلاس تست:** `GuestJourneyApiIntegrationTests`  
**متد:** `test_complete_guest_journey_e2e`

این سناریو چرخه کامل تجربه مسافر را از بدو ورود ناشناس به سامانه تا رزرو، لغو و خروج بررسی می‌کند:

| گام | عملیات | اندپوینت (Endpoint) | متد | رفتار و شروط مورد اعتبارسنجی |
|:---:|:---|:---|:---:|:---|
| **۱** | دریافت توکن امنیت | `/api/auth/csrf/` | `GET` | تنظیم کوکی `csrftoken` برای تعاملات بعدی |
| **۲** | کشف شهرهای فعال | `/api/cities/` | `GET` | بازگشت شهرهای دارای حداقل یک هتل فعال (نظیر اصفهان) |
| **۳** | جستجوی هتل با فیلتر | `/api/hotels/?city=...&check_in=...&check_out=...&guests=...` | `GET` | فیلتر هتل‌ها، محاسبه `min_price`، تایید فیلد `available: true` و ثبت کوکی `last_city` |
| **۴** | مشاهده مشخصات هتل | `/api/hotels/{id}/` | `GET` | دریافت انواع اتاق، امکانات و ثبت هتل در سشن هتل‌های اخیراً دیده‌شده |
| **۵** | بررسی سشن اخیر | `/api/hotels/recent/` | `GET` | اطمینان از وجود هتل مشاهده‌شده در تاریخچه مرور کاربر |
| **۶** | استعلام موجودی اتاق | `/api/hotels/{id}/rooms/?check_in=...&check_out=...` | `GET` | محاسبه لحظه‌ای موجودی (`available_count = 2`) در بازه تاریخی مدنظر |
| **۷** | ثبت‌نام مسافر جدید | `/api/auth/register/` | `POST` | ایجاد حساب مهمان با `email_verified=False` و ارسال ایمیل حاوی لینک و توکن رمزنگاری‌شده |
| **۸** | فعال‌سازی ایمیل | `/api/auth/verify-email/` | `POST` | اعتبارسنجی امضای دیجیتال توکن، تبدیل `email_verified` به `True` و لاگ امنیتی |
| **۹** | ورود به سامانه | `/api/auth/login/` | `POST` | ایجاد سشن احراز هویت جنگو، ارزیابی وضعیت لاگین در `/api/auth/me/` |
| **۱۰** | اعتبارسنجی کوپن | `/api/discounts/validate/` | `POST` | بررسی فعال بودن، تاریخ اعتبار و سقف مجاز کد تخفیف (`ESFAHAN25` با ۲۵٪ تخفیف) |
| **۱۱** | استعلام پیش‌فاکتور | `/api/bookings/quote/` | `POST` | محاسبه ریاضی دقیق قیمت (۳ شب × ۳,۰۰۰,۰۰۰ = ۹,۰۰۰,۰۰۰ تومان؛ کسر ۲۵٪ تخفیف = ۶,۷۵۰,۰۰۰ تومان) |
| **۱۲** | ثبت قطعی رزرو | `/api/bookings/` | `POST` | ثبت رزرو وضعیت `confirmed` در تراکنش اتمیک، افزایش `used_count` تخفیف، و کسر خودکار موجودی اتاق به ۱ |
| **۱۳** | تاریخچه رزروهای من | `/api/bookings/mine/` | `GET` | مشاهده رزرو ثبت‌شده به همراه مشخصات کامل هتل و اتاق |
| **۱۴** | لغو رزرو مسافر | `/api/bookings/{id}/cancel/` | `POST` | تغییر وضعیت به `cancelled`، بازیابی کامل موجودی اتاق به ۲ و بازگشت `used_count` کد تخفیف به ۰ |
| **۱۵** | خروج از حساب | `/api/auth/logout/` | `POST` | انقضای سشن و تخلیه داده‌های هویتی (`data: null`) |

---

### ۲.۲. داستان کامل مدیر هتل (Manager Journey Flow)
**کلاس تست:** `ManagerJourneyApiIntegrationTests`  
**متد:** `test_complete_manager_journey_and_isolation_e2e`

این سناریو فرایند مدیریت هتل، تعریف اقامتگاه و اتاق، ارائه تخفیف و پایش ظرفیت را پوشش می‌دهد:

| گام | عملیات | اندپوینت (Endpoint) | متد | رفتار و شروط مورد اعتبارسنجی |
|:---:|:---|:---|:---:|:---|
| **۱** | ثبت‌نام و ورود مدیر | `/api/auth/register/` & `/login/` | `POST` | ایجاد حساب با نقش `manager`، تایید ایمیل و ورود به سامانه |
| **۲** | کاتالوگ امکانات رفاهی | `/api/amenities/` | `GET` | واکشی امکانات پیش‌فرض (وای‌فای، باشگاه، رستوران) جهت انتساب به اتاق‌ها |
| **۳** | ثبت و به‌روزرسانی هتل | `/api/manager/hotels/` & `/{id}/` | `POST`/`PUT` | ایجاد هتل اختصاصی مدیر و ویرایش آدرس و اطلاعات هتل |
| **۴** | تعریف انواع اتاق | `/api/manager/hotels/{id}/room-types/` | `POST`/`PUT` | تعریف سوییت سلطنتی با ظرفیت ۳ نفر، تعداد ۳ اتاق و انتساب امکانات رفاهی |
| **۵** | کمپین کد تخفیف | `/api/manager/hotels/{id}/discounts/` | `POST` | تعریف کد تخفیف ۲۰ درصدی با تعیین بازه زمانی معتبر و سقف استفاده |
| **۶** | دریافت سفارش مهمان | `/api/bookings/` (مهمان مجزا) | `POST` | ثبت اقامت ۳ روزه توسط یک مهمان در اتاق تعریف‌شده |
| **۷** | پایش رزروهای دریافتی | `/api/manager/hotels/{id}/bookings/` | `GET` | مشاهده لیست رزروهای هتل همراه با فیلتر وضعیت (`?status=confirmed`) |
| **۸** | ماتریس تقویم موجودی | `/api/manager/hotels/{id}/availability/` | `GET` | استعلام وضعیت روزانه اتاق‌ها در بازه مدنظر: انعکاس دقیق `total: 3`، `reserved: 1`، `free: 2` |

---

### ۲.۳. تست‌های امنیت، ایزولاسیون چندمستأجری و شرایط مرزی (Security & Edge Cases)
**کلاس‌های تست:** `EdgeCasesApiIntegrationTests` و بخش ایزولاسیون `ManagerJourneyApiIntegrationTests`

این آزمون‌ها تضمین می‌کنند که مرزهای امنیتی سامانه تحت هیچ شرایطی نقض نخواهند شد:

1. **ایزولاسیون چندمستأجری مدیران (Multi-Tenant Isolation):**
   - اگر مدیر B تلاش کند هتل، انواع اتاق یا کدهای تخفیف مدیر A را مشاهده یا ویرایش کند، پاسخ `404 Not Found` دریافت می‌کند تا از وجود هویت داده‌ها (Data Leakage) مطلع نشود.
   - مدیر B به تقویم موجودی یا لیست رزروهای هتل مدیر A دسترسی ندارد (`404 Not Found`).
2. **مرزبندی نقشی (Role Boundaries):**
   - کاربران با نقش مهمان (`guest`) در صورت تلاش برای فراخوانی اندپوینت‌های مدیریت هتل خطای `403 Forbidden` دریافت می‌کنند.
   - کاربران با نقش مدیر (`manager`) مجاز به ثبت رزرو اقامتی نیستند و درخواست رزرو آن‌ها با `403 Forbidden` رد می‌شود.
3. **الزام تایید ایمیل (Verified Email Requirement):**
   - مهمانانی که ایمیل خود را تایید نکرده باشند (`email_verified=False`) امکان رزرو ندارند و خطای `403 Forbidden` با پیام راهنمای تایید ایمیل دریافت می‌کنند.
4. **کنترل همزمانی و اتمام ظرفیت (Capacity Conflict):**
   - در صورت تکمیل ظرفیت اتاق برای بازه تاریخی درخواستی، سامانه خطای `409 Conflict` با پیام واضح عدم موجودی صادر می‌کند.
5. **جلوگیری از لغو غیرمجاز (IDOR Defense):**
   - هر مهمان فقط مجاز به لغو رزروهای خود است. تلاش مسافر دیگر برای لغو رزرو غریبه با پاسخ `404 Not Found` مسدود می‌شود.
6. **اعتبارسنجی گاه‌نگاری تاریخ‌ها (Date Validation):**
   - تاریخ ورود در گذشته یا تاریخ خروج قبل/مساوی با تاریخ ورود، با خطای `400 Bad Request` متوقف می‌شود.

---

## ۳. تست‌های دود کلاینت فرانت‌اند (Frontend Smoke Suite)

آزمون‌های فرانت‌اند در فایل `frontend/src/api/client.test.js` مستقر هستند و بدون نیاز به پکیج‌های حجیم شخص ثالث، با تست‌رانر استاندارد Node.js (`node:test` و `node:assert/strict`) با سرعت بالا اجرا می‌شوند.

### سناریوهای پوشش‌داده‌شده:
1. **کلاس `ApiError`:** صحت ساختار شیء، فیلدهای `message`، `status` و دیکشنری `errors`.
2. **مدیریت کوکی‌ها (`getCookie` / `setCookie`):** استخراج امن کوکی‌های CSRF، پشتیبانی از مقداردهی URL-Encoded فارسی و رفتار ایمن در محیط‌های بدون مرورگر.
3. **توکن CSRF هوشمند (`ensureCsrfToken`):** واکشی خودکار توکن از `/api/auth/csrf/` در صورت نبود در کوکی قبل از ارسال درخواست‌های متغیّرساز (POST/PUT/DELETE).
4. **نرمال‌سازی خطاهای اتصال شبکه (Network Error Normalization):** تبدیل خطاهای قطع شبکه به `ApiError` با کد وضعیت 0 و پیام خطای دوستانه فارسی.
5. **نرمال‌سازی خطای اعتبارسنجی 400 (Validation Errors):** استخراج پیام‌های خطا به تفکیک فیلدهای فرم جهت نمایش در زیر اینپوت‌های React.
6. **پیام‌های جایگزین فارسی (Fallbacks):** پوشش پیام‌های شفاف برای کدهای وضعیت 401 (لزوم ورود)، 403 (عدم دسترسی)، و 404 (منبع یافت نشد).
7. **استخراج استاندارد داده (Unpacking Data):** استخراج خودکار فیلد `data` در پاسخ‌های موفق `{"data": ...}`.
8. **پاسخ‌های بدون بدنه 204:** بازگشت `null` در پاسخ‌های موفق خروج یا حذف بدون محتوا.

---

## ۴. راهنمای راه‌اندازی و اجرای پروژه (How to Run / Execution Guide)

این بخش راهنمای گام‌به‌گام راه‌اندازی کامل سامانه رزرواسیون هتل برای شبیه‌سازی و ارائه دمو (Demo) در محیط توسعه محلی را ارائه می‌دهد.

### ۴.۱. پیش‌نیازهای سیستمی
- **Python:** نسخه 3.12 یا بالاتر
- **Node.js:** نسخه 20 یا بالاتر همراه با `npm`
- **PostgreSQL:** نسخه 15 یا 16 در حال اجرا با دیتابیس `hotel_db` و کاربر `postgres`
- **Git:** ابزار مدیریت نسخه

---

### ۴.۲. راه‌اندازی بک‌اند جنگو (Backend Setup)

```bash
# ۱. ورود به پوشه بک‌اند
cd backend

# ۲. ایجاد و فعال‌سازی محیط مجازی پایتون (Virtualenv)
python -m venv .venv
# لینوکس و مک:
source .venv/bin/activate
# ویندوز (PowerShell):
.venv\Scripts\Activate.ps1

# ۳. نصب وابستگی‌های پایتون
pip install -r requirements.txt

# ۴. تنظیم متغیرهای محیطی (فایل .env)
# فایل .env.example را به .env کپی کرده و اطلاعات اتصال دیتابیس را بررسی کنید:
# DATABASE_URL=postgres://postgres:postgres@localhost:5432/hotel_db
# SECRET_KEY=your-development-secret-key
# DEBUG=True

# ۵. اعمال مایگریشن‌های پایگاه داده PostgreSQL
python manage.py migrate

# ۶. بارگذاری داده‌های اولیه و دمو (Seed Data)
python manage.py seed_demo

# ۷. بررسی سلامت پیکربندی جنگو
python manage.py check

# ۸. اجرای سرور توسعه جنگو (پورت ۸۰۰۰)
python manage.py runserver
```

> **کاربران پیش‌فرض جهت دمو و تست:**
> - **مدیر هتل (Hotel Manager):**
>   - نام کاربری: `manager1`
>   - گذرواژه: `Pass1234!`
>   - نقش: `manager` (مالک هتل‌های اصفهان و تهران با دسترسی کامل به پنل مدیریت)
> - **مهمان / مسافر (Guest):**
>   - نام کاربری: `guest1`
>   - گذرواژه: `Pass1234!`
>   - نقش: `guest` (ایمیل تاییدشده، دارای سابقه رزرو)

---

### ۴.۳. راه‌اندازی فرانت‌اند ری‌اکت (Frontend Setup)

```bash
# ۱. باز کردن یک ترمینال جدید و ورود به پوشه فرانت‌اند
cd frontend

# ۲. نصب بسته‌های npm (تطابق کامل با lockfile)
npm ci

# ۳. اجرای سرور توسعه Vite (پورت ۵۱۷۳)
npm run dev
```

مرورگر خود را باز کرده و به آدرس `http://localhost:5173` بروید. تمام درخواست‌های `/api/` به صورت خودکار توسط Vite به سرور جنگو روی پورت ۸۰۰۰ پروکسی می‌شوند.

---

### ۴.۴. ساخت نسخه نهایی و سرو یکپارچه توسط جنگو (Production Build)

برای تست سناریوی واقعی استقرار بدون نیاز به سرور Vite:
```bash
# ۱. بیلد پروژه ری‌اکت
cd frontend
npm run build

# ۲. بازگشت به بک‌اند و اجرای سرور
cd ../backend
python manage.py runserver
```
در این حالت، با مراجعه مستقیم به `http://localhost:8000`، ویوی `spa_host_view` جنگو فایل `index.html` تولیدشده را لود کرده و سامانه به صورت یکپارچه اجرا می‌شود.

---

## ۵. راهنمای اجرای آزمون‌ها (Verification & Test Execution Guide)

### ۵.۱. اجرای تست‌های بک‌اند جنگو:
```bash
cd backend

# اجرای کل پایگاه آزمون‌های پروژه (۲۹۹ تست)
python manage.py test --keepdb

# اجرای اختصاصی تست‌های یکپارچه انتها به انتها (P4-05)
python manage.py test apps.bookings.test_integration_flows --keepdb

# اجرای آزمون‌ها همراه با سنجش درصد پوشش کد (Coverage)
coverage run manage.py test
coverage report
```

### ۵.۲. اجرای تست‌های فرانت‌اند:
```bash
cd frontend

# اجرای آزمون‌های کلاینت شبکه و Smoke
npm test

# بررسی خطاهای ساختاری و Linting
npm run lint

# تست بیلد فرانت‌اند
npm run build
```

تمامی دستورات فوق در پایپ‌لاین Continuous Integration (`.github/workflows/ci.yml`) روی سرورهای ابری GitHub Actions به‌طور خودکار در هر Push و Pull Request اجرا می‌شوند.


---
