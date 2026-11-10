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
