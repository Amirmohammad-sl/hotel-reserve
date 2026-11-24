# سناریوی ارائه و دمو فاز ۳ (Demo Script — Phase 3)
- **زمان تخمینی:** ۵ الی ۸ دقیقه
- **مخاطب:** استاد محترم و دستیاران آموزشی درس برنامه‌نویسی وب
- **هدف:** نمایش قابلیت‌های معماری فاز ۳ شامل Managerها و QuerySetهای سفارشی، مدیریت نشست (Session) و کوکی‌ها، تراکنش‌های همزمان امن در رزرو (Concurrency Safety)، و زیرساخت جامع لاگ‌گذاری در تمام بخش‌ها.

---

## مشخصات حساب‌های کاربری دمو (برگرفته از `seed_demo`)

| نقش | نام کاربری | ایمیل | کلمه عبور | مشخصات و کاربرد در دمو |
|---|---|---|---|---|
| **Hotel Manager** | `manager1` | `manager1@hotel.com` | `Manager123!` | علیرضا رضایی (مدیر هتل‌های تهران، اصفهان، شیراز) |
| **Hotel Manager** | `manager2` | `manager2@hotel.com` | `Manager123!` | سارا احمدی (مدیر هتل‌های کیش و مشهد) |
| **Guest** | `guest1` | `guest1@test.com` | `Guest123!` | علی محمدی (تست رزرو مسافر، بررسی کوکی سشن) |
| **Guest** | `guest2` | `guest2@test.com` | `Guest123!` | مریم کریمی (تست رزروهای همزمان) |

---

## بخش ۱: تجربه مسافر، سشن و کوکی، رزرو امن و لاگ‌های سمت مهمان
**ارائه‌دهنده:** مهدی مرادی (اپراتور B) — زمان: ۳ الی ۴ دقیقه  
*(اپراتور A آماده پاسخگویی به سوالات فنی و هم‌افزایی در این بخش است)*

### ۱. ورود مسافر و بررسی چرخه کوکی و نشست (۱ دقیقه)
- باز کردن صفحه ورود (`http://localhost:8000/login`).
- ورود با حساب `guest1` و فعال کردن چک‌باکس «مرا به خاطر بسپار» (`remember_me=True`).
- باز کردن تب Application / Storage در DevTools مرورگر:
  - نمایش کوکی `sessionid` با فلگ `HttpOnly=True` و تاریخ انقضای ۱۴ روزه (۱,۲۰۹,۶۰۰ ثانیه).
  - نمایش کوکی `csrftoken` با فلگ `HttpOnly=False` (طبق قرارداد API_CONTRACT جهت خواندن توسط هدر `X-CSRFToken` فرانت‌اند React).
- خروج (`Logout`) و ورود مجدد بدون تیک `remember_me`:
  - نمایش تبدیل کوکی سشن به Session Cookie (با بستن مرورگر منقضی می‌شود).
- باز کردن فایل `backend/logs/security.log` و نمایش لاگ ورود موفق کاربر با IP و وضعیت `remember_me`.

### ۲. جستجوی هتل با متدهای QuerySet و استعلام آنی قیمت (۱.۵ دقیقه)
- رفتن به صفحه اصلی و جستجوی هتل‌های شهر تهران با فیلتر بودجه.
- توضیح استفاده از `HotelQuerySet.with_min_price()` و حذف مشکل N+1.
- کلیک روی هتل و باز شدن صفحه جزئیات هتل (`/hotels/:id`):
  - توضیح محاسبه برخط موجودی اتاق‌ها توسط `RoomTypeQuerySet.with_availability()`.
- انتخاب اتاق و استعلام قیمت (Quote) با اعمال کد تخفیف دمو (`NOROOZ1403`).
- نمایش فایل `backend/logs/app.log`:
  - ثبت لاگ اعتبارسنجی تخفیف و محاسبه Quote با ذکر شناسه هتل و درصد تخفیف.

### ۳. ثبت رزرو با همزمانی امن (Concurrency-Safe Booking) (۱ دقیقه)
- نهایی‌سازی رزرو و دریافت کد پیگیری.
- توضیح فنی عملکرد اتمیک رزرو با `select_for_update()` روی ردیف `RoomType` جهت جلوگیری از Overbooking در صورت درخواست همزمان دو مسافر.
- نمایش ثبت لاگ رزرو موفق در `backend/logs/app.log`:
  - `Booking created: booking_id=X guest_id=Y room_type_id=Z total_price=W`.

---

## بخش ۲: پنل مدیر هتل، ایزولاسیون داده، لاگ‌های امنیتی و پشتیبان‌گیری دیتابیس
**ارائه‌دهنده:** امیرمحمد سلیمانی (اپراتور A) — زمان: ۳ الی ۴ دقیقه  
*(اپراتور B آماده پاسخگویی به سوالات فنی و هم‌افزایی در این بخش است)*

### ۱. پنل مدیریت و ایزولاسیون چندمستأجری با Managerها (۱.۵ دقیقه)
- خروج از حساب مهمان و ورود با حساب مدیر `manager1`.
- رفتن به داشبورد هتل‌ها (`/manager/hotels`):
  - مشاهده هتل‌های تهران، اصفهان و شیراز و عدم مشاهده هتل‌های `manager2` (کیش و مشهد).
  - توضیح فنی نحوه اعمال `.owned_by(request.user)` در `HotelQuerySet` و `RoomTypeQuerySet` جهت جلوگیری از نفوذ افقی (Horizontal Privilege Escalation).
- باز کردن تقویم ظرفیت هتل (`/manager/hotels/:id/availability`):
  - نمایش تعداد کل اتاق‌ها، اتاق‌های رزروشده و باقیمانده به تفکیک روز.
  - توضیح نحوه استفاده از `BookingQuerySet.overlapping()` برای محاسبه دقیق اشغال روزانه بدون تداخل جابجایی در یک روز (Same-day Turnover).

### ۲. مدیریت کدهای تخفیف و اعمال سقف استفاده (۱ دقیقه)
- رفتن به بخش کدهای تخفیف هتل (`/manager/hotels/:id/discounts`):
  - نمایش کدهای تخفیف با ستون‌های تاریخ اعتبار، درصد و تعداد استفاده‌شده (`used_count / max_uses`).
  - توضیح متد `DiscountCodeQuerySet.valid_now()` و متمرکزسازی قیود تجاری تخفیف در لایه مدل.

### ۳. حسابرسی امنیتی لاگ‌ها و آزمون یکپارچگی پایگاه داده (۱ دقیقه)
- تست دسترسی غیرمجاز: ارسال یک درخواست غیرمجاز به مسیر ادمین یا هتل دیگر.
- نمایش لاگ‌های امنیتی ثبت‌شده در `backend/logs/security.log`:
  - `Forbidden role access: user_id=X role='guest' denied access to /api/manager/...`
- نمایش میان‌افزار مرکزی لاگ‌گذاری (`RequestLogMiddleware`) در `backend/logs/app.log`:
  - ثبت خودکار متد، مسیر، کد وضعیت HTTP، شناسه کاربر و مدت زمان پردازش به میلی‌ثانیه (`duration_ms`).
- نمایش فایل پشتیبان رسمی دیتابیس فاز ۳ در `db_backup/hotel_db_phase3.sql` و تایید اجرای موفقیت‌آمیز ۲۳۵ آزمون خودکار در کنسول.

---

## ۵ نقطه عطف جهت نمایش کد (Show the Code Moments)

در صورت درخواست استاد جهت مشاهده کد، این ۵ نقطه مسیر کامل **View → Form → Model/Manager** را نشان می‌دهند:

1. **جستجوی عمومی هتل و تجمیع کمترین قیمت در SQL:**
   - مسیر فایل: `backend/apps/hotels/views.py` (`hotel_list_view`)
   - فرم: `HotelSearchForm` در `backend/apps/hotels/forms.py`
   - کوئری‌ست: متد `with_min_price()` در `backend/apps/hotels/models.py` (`HotelQuerySet`)
   - *نکته کلیدی:* استفاده از `models.Min('room_types__price_per_night')` جهت جلوگیری از کوئری‌های N+1.

2. **محاسبه موجودی ظرفیت اتاق با Subquery:**
   - مسیر فایل: `backend/apps/hotels/views.py` (`hotel_rooms_view`)
   - کوئری‌ست: متد `with_availability()` در `backend/apps/hotels/models.py` (`RoomTypeQuerySet`)
   - *نکته کلیدی:* ادغام رزروهای دارای تداخل از جدول رزروها از طریق `models.Subquery` و `Coalesce` مستقیماً در دیتابیس.

3. **رزرو همزمان و اعتبارسنجی کد تخفیف:**
   - مسیر فایل: `backend/apps/bookings/views.py` (`BookingCreateView`)
   - فرم: `BookingCreateForm` در `backend/apps/bookings/forms.py`
   - سرویس و منیجر: متد `create_booking_atomic()` در `services.py` و `DiscountCodeManager.get_valid()`
   - *نکته کلیدی:* قفل ردیف اتاق با `select_for_update()` داخل `transaction.atomic()` جهت تضمین همزمانی امن.

4. **مدیریت سشن و چرخه حیات کوکی:**
   - مسیر فایل: `backend/apps/accounts/views.py` (`login_view`)
   - فرم: `LoginForm` در `backend/apps/accounts/forms.py`
   - متدها: `request.session.set_expiry(1209600 if remember_me else 0)` و `request.session.cycle_key()`
   - *نکته کلیدی:* جلوگیری از حمله Session Fixation با چرخش کلید سشن و انقضای داینامیک کوکی.

5. **میان‌افزار مرکزی لاگ و ردگیری زمان پاسخ‌دهی:**
   - مسیر فایل: `backend/apps/core/middleware.py` (`RequestLogMiddleware`)
   - تنظیمات لاگ: دیکشنری `LOGGING` در `backend/config/settings.py` با ۳ فایل تفکیک‌شده (`app.log`, `error.log`, `security.log`)
   - *نکته کلیدی:* ثبت مدت زمان پاسخ با دقت صدم میلی‌ثانیه و لاگ تمام استثناها همراه با Traceback کامل.
