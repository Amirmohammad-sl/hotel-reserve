# مستند فرآیندهای اصلی سامانه رزرواسیون هتل (Business Process Diagrams)

این مستند شامل نمودارهای فرآیندی مستقل برای **فرآیندهای اصلی کسب‌وکار (Main Business Processes)** سامانه رزرواسیون هتل است که منطبق بر شیوه‌نامه ارزیابی درس برنامه‌نویسی وب طراحی شده‌اند.

> **نکات طراحی طبق شیوه‌نامه استاد:**
> ۱. فرآیندهای روتین (نظیر ثبت‌نام/ورود، CRUD ساده و فیلترهای پایه‌ای) حذف شده و تمرکز بر منطق تجاری اصلی سیستم است.
> ۲. از رسم نمودار بسیار بزرگ و یکپارچه خودداری شده و هر فرآیند در نموداری مستقل از نقطه شروع تا پایان با ساختار خطوط شناوری (Swimlane/Subgraph) ترسیم شده است.
> ۳. در تمام نمودارها، **اقدامات کاربر (مهمان/مدیر)** و **واکنش‌ها و پردازش سیستم (فرانت‌اند/بک‌اند/دیتابیس)** در دو ستون جداگانه تفکیک شده‌اند.
> ۴. نقاط تصمیم‌گیری (Decision Points)، شرایط خطا (۴۰۰، ۴۰۱، ۴۰۳، ۴۰۹)، مسیرهای جایگزین و بازگشت منابع به طور کامل مدل شده‌اند.

---

## فهرست فرآیندهای اصلی:
1. [فرآیند ۱: استعلام موجودی، محاسبه قیمت پویا و اعتبارسنجی کد تخفیف](#۱-فرآیند-استعلام-موجودی-محاسبه-قیمت-پویا-و-اعتبارسنجی-کد-تخفیف)
2. [فرآیند ۲: ثبت قطعی رزرو اتاق با کنترل همزمانی و تراکنش اتمیک (جلوگیری از Overbooking)](#۲-فرآیند-ثبت-قطعی-رزرو-اتاق-با-کنترل-همزمانی-و-تراکنش-اتمیک)
3. [فرآیند ۳: لغو رزرو، اعتبارسنجی بازه زمانی، آزادسازی ظرفیت و بازگشت سهمیه تخفیف](#۳-فرآیند-لغو-رزرو-اعتبارسنجی-بازه-زمانی-آزادسازی-ظرفیت-و-بازگشت-سهمیه)
4. [فرآیند ۴: پایش ماتریس ظرفیت و تقویم وضعیت اتاق‌های پر و خالی توسط مدیر هتل](#۴-فرآیند-پایش-ماتریس-ظرفیت-و-تقویم-وضعیت-اتاقهای-پر-و-خالی)
5. [فرآیند ۵ (امتیازی): ثبت و اعتبارسنجی نظر مهمان بر اساس سابقه اقامت قطعی](#۵-فرآیند-امتیازی-ثبت-و-اعتبارسنجی-نظر-مهمان-بر-اساس-سابقه-اقامت-قطعی)
6. [ضمیمه فنی: دیاگرام‌های توالی (Sequence Diagrams)](#ضمیمه-فنی-دیاگرامهای-توالی-sequence-diagrams)

---

## ۱. فرآیند استعلام موجودی، محاسبه قیمت پویا و اعتبارسنجی کد تخفیف
**Guest Room Quote, Capacity Pre-check & Discount Validation**

### مشخصات فرآیند:
- **هدف (Goal):** محاسبه بلادرنگ و شفاف پیش‌فاکتور اقامت برای مهمان با بررسی اولیه دسترسی‌پذیری اتاق و ارزیابی شروط چندگانه کد تخفیف پیش از تعهد رزرو.
- **نقش‌های درگیر (Actors):** کاربر مهمان (Guest)، سیستم (کلاینت React، اندپوینت استعلام جنگو، پایگاه داده PostgreSQL).
- **پیش‌شرط‌ها (Pre-conditions):**
  1. هتل و نوع اتاق (`RoomType`) فعال در پایگاه‌داده وجود داشته باشد.
  2. مهمان صفحه جزئیات اتاق را باز کرده باشد.
- **گام‌های اصلی (Main Flow):**
  1. مهمان بازه تاریخی ورود و خروج (`check_in`, `check_out`)، تعداد اتاق درخواستی و در صورت تمایل کد تخفیف را وارد می‌کند.
  2. کلاینت درخواست `POST /api/bookings/quote/` را به سرور ارسال می‌نماید.
  3. سیستم معتبر بودن تاریخ‌ها (تاریخ خروج بعد از ورود و عدم انتخاب تاریخ در گذشته) را بررسی می‌کند.
  4. سیستم موجودی اسمی اتاق را در برابر رزروهای قطعی جاری در آن بازه زمانی می‌سنجد.
  5. در صورت کافی بودن ظرفیت، قیمت پایه به فرمول `تعداد شب‌ها × قیمت هر شب × تعداد اتاق` محاسبه می‌شود.
  6. در صورت ارسال کد تخفیف، سیستم شرایط اعتبار را ارزیابی می‌کند:
     - فعال بودن کد (`is_active`)
     - معتبر بودن تاریخ انقضا (`valid_from <= today <= valid_to`)
     - پر نشدن سقف مجاز استفاده (`used_count < max_uses`)
     - رسیدن به حداقل مبلغ فاکتور (`subtotal >= min_booking_amount`)
     - اختصاصی نبودن کد برای هتل دیگر
  7. در صورت انطباق، مبلغ تخفیف محاسبه و از فاکتور کسر می‌شود؛ در غیر این صورت هشدار عدم تطابق تخفیف داده شده اما پیش‌فاکتور پایه تولید می‌گردد.
  8. پیش‌فاکتور نهایی با تفکیک قیمت پایه، سود مهمان از تخفیف و مبلغ نهایی قابل پرداخت رندر می‌شود.
- **جریان‌های استثنا و خطا (Alternative & Error Flows):**
  - **خطای تاریخ نامعتبر:** در صورت `check_out <= check_in`، خطای 400 برگردانده شده و مهمان به اصلاح تقویم هدایت می‌شود.
  - **خطای نبود ظرفیت در بازه:** در صورت تکمیل ظرفیت اتاق‌ها در حتی یک شب از بازه، پیام تکمیل ظرفیت بازگردانده شده و تقویم روزهای آزاد پیشنهاد می‌گردد.
  - **کد تخفیف نامعتبر/منقضی:** سیستم فرآیند را لغو نمی‌کند؛ بلکه با صدور هشدار، قیمت عادی بدون تخفیف را محاسبه می‌نماید تا کاربر سردرگم نشود.
- **پس‌شرط‌ها (Post-conditions):**
  - پیش‌فاکتور معتبر تولید شده و مهمان دکمه فعال «تأیید و ثبت نهایی رزرو» را در اختیار دارد.

```mermaid
flowchart TD
    subgraph Guest["اقدامات کاربر مهمان (Guest Actions)"]
        G_Start([شروع: مشاهده جزئیات هتل و نوع اتاق])
        G_Input["انتخاب بازه اقامت (check_in, check_out) و کد تخفیف (اختیاری)"]
        G_Submit["ارسال فرم استعلام قیمت (POST /api/bookings/quote/)"]
        G_FixDates["اصلاح تاریخ‌ها در تقویم انتخاب روز"]
        G_ChangeDates["تغییر بازه زمانی یا انتخاب نوع اتاق دیگر"]
        G_Review["مشاهده پیش‌فاکتور شفاف (قیمت، تخفیف، مبلغ نهایی)"]
        G_End([پایان فرآیند استعلام: آماده‌سازی برای رزرو])
    end

    subgraph System["پردازش و واکنش‌های سیستم (System Processing)"]
        S_ValDates{"آیا تاریخ‌ها معتبرند؟\n(check_out > check_in & در آینده)"}
        S_ErrDates["خطای 400: بازه تاریخی نامعتبر"]
        S_CheckAvail{"آیا اتاق در کل بازه انتخابی ظرفیت خالی دارد؟"}
        S_ErrAvail["خطای عدم ظرفیت و پیشنهاد تاریخ‌های مجاور"]
        S_CalcBase["محاسبه قیمت پایه:\n(تعداد شب‌ها × قیمت هر شب × تعداد اتاق)"]
        S_HasCode{"آیا کد تخفیف وارد شده است؟"}
        S_ValCode{"اعتبارسنجی شروط تخفیف:\nفعال؟ منقضی نشده؟ سقف پر نشده؟ حداقل خرید؟"}
        S_WarnCode["هشدار: کد تخفیف نامعتبر یا منقضی است\n(ادامه با محاسبه قیمت عادی)"]
        S_ApplyCode["محاسبه تخفیف (درصدی با سقف یا مبلغ ثابت) و اعمال در فاکتور"]
        S_RenderQuote["تولید پیش‌فاکتور رسمی شامل قیمت پایه، تخفیف و مبلغ نهایی"]
    end

    G_Start --> G_Input
    G_Input --> G_Submit
    G_Submit --> S_ValDates

    S_ValDates -- "خیر" --> S_ErrDates
    S_ErrDates --> G_FixDates
    G_FixDates --> G_Submit

    S_ValDates -- "بله" --> S_CheckAvail
    S_CheckAvail -- "خیر (تکمیل ظرفیت)" --> S_ErrAvail
    S_ErrAvail --> G_ChangeDates
    G_ChangeDates --> G_Input

    S_CheckAvail -- "بله" --> S_CalcBase
    S_CalcBase --> S_HasCode

    S_HasCode -- "خیر" --> S_RenderQuote
    S_HasCode -- "بله" --> S_ValCode

    S_ValCode -- "نامعتبر / منقضی" --> S_WarnCode
    S_WarnCode --> S_RenderQuote

    S_ValCode -- "معتبر" --> S_ApplyCode
    S_ApplyCode --> S_RenderQuote

    S_RenderQuote --> G_Review
    G_Review --> G_End
```

---

## ۲. فرآیند ثبت قطعی رزرو اتاق با کنترل همزمانی و تراکنش اتمیک
**Booking Creation & Concurrency Control Process (Overbooking Prevention)**

### مشخصات فرآیند:
- **هدف (Goal):** ثبت امن و بدون خطای رزرو با مکانیزم همزمانی پایگاه‌داده به گونه‌ای که در صورت ثبت همزمان آخرین اتاق توسط دو کاربر، فقط یکی موفق شود و از پدیده Overbooking به طور کامل جلوگیری گردد.
- **نقش‌های درگیر (Actors):** کاربر مهمان (Guest)، سیستم (ویو جنگو، BookingForm، BookingManager با تراکنش PostgreSQL).
- **پیش‌شرط‌ها (Pre-conditions):**
  1. مهمان در سیستم لاگین کرده باشد (`request.user.is_authenticated`).
  2. پیش‌فاکتور با پارامترهای مشخص اقامت تأیید شده باشد.
- **گام‌های اصلی (Main Flow):**
  1. مهمان با فشردن دکمه «تأیید نهایی و ثبت رزرو»، درخواست `POST /api/bookings/` را همراه با CSRF توکن ارسال می‌کند.
  2. سیستم وضعیت نشست (Session) را احراز می‌کند.
  3. فرم `BookingForm` صحت ساختار ورودی‌ها را اعتبارسنجی می‌نماید.
  4. لایه بیزینس یک تراکنش اتمیک پایگاه‌داده (`transaction.atomic`) باز می‌کند.
  5. رکوردهای رزرو همپوشان و ظرفیت نوع اتاق در بازه اقامت در سطح دیتابیس قفل و مجدداً محاسبه می‌شوند.
  6. شرط ظرفیت قطعی بررسی می‌شود: `active_bookings + requested_rooms <= total_rooms`.
  7. در صورت تایید ظرفیت، سند رزرو با وضعیت `confirmed` و شناسه یکتا درج می‌گردد.
  8. در صورت استفاده از تخفیف، فیلد `used_count` کد تخفیف اتمیک یک واحد افزایش می‌یابد.
  9. تراکنش کامیت (Commit) شده، ظرفیت کسر می‌گردد و رسید رزرو با وضعیت 201 Created به مهمان تحویل می‌شود.
- **جریان‌های استثنا و خطا (Alternative & Error Flows):**
  - **کاربر لاگین نباشد:** پاسخ خطای 401 Unauthorized و هدایت به صفحه ورود با حفظ داده‌های رزرو.
  - **نقض همزمانی / تکمیل ظرفیت در آخرین لحظه:** اگر کاربر دیگری چند میلی‌ثانیه قبل اتاق آخر را گرفته باشد، بررسی ظرفیت ناموفق شده، تراکنش سریعاً Rollback می‌شود و خطای `409 Conflict` (تکمیل ظرفیت همزمان) صادر می‌گردد.
  - **خطای اعتبارسنجی فرم:** پاسخ 400 Bad Request همراه با ذکر فیلدهای مشکل‌دار.
- **پس‌شرط‌ها (Post-conditions):**
  - رکورد رزرو پایدار در دیتابیس ثبت شده، ظرفیت اتاق برای سایرین کاهش یافته و رسید رزرو در داشبورد مهمان ذخیره است.

```mermaid
flowchart TD
    subgraph Guest["اقدامات کاربر مهمان (Guest Actions)"]
        B_Start([شروع: مشاهده پیش‌فاکتور تاییدشده])
        B_Click["کلیک روی دکمه 'تأیید نهایی و ثبت رزرو'"]
        B_Login["ورود به حساب کاربری و بازگشت خودکار"]
        B_HandleConflict["مشاهده خطای تکمیل ظرفیت همزمان (409) و انتخاب اتاق دیگر"]
        B_Success["دریافت شناسه رزرو و مشاهده رسید در 'رزروهای من'"]
        B_End([پایان فرآیند رزرو قطعی])
    end

    subgraph System["پردازش و واکنش‌های سیستم (System Processing)"]
        S_Auth{"آیا کاربر احراز هویت شده است؟\n(Session Active?)"}
        S_Err401["خطای 401: هدایت موقت به صفحه لاگین"]
        S_Form{"اعتبارسنجی فیلدها با BookingForm"}
        S_Err400["خطای 400: داده‌های ناقص یا نامعتبر"]
        S_Atomic["آغاز تراکنش امن اتمیک\n(BEGIN transaction.atomic)"]
        S_LockCheck["استعلام ظرفیت با قفل‌گذاری همروندی دیتابیس\n(SELECT ... FOR UPDATE)"]
        S_CapCheck{"آیا در تک‌تک شب‌ها ظرفیت کافی است؟\n(reserved + requested <= total_rooms)"}
        S_Rollback["لغو کامل تراکنش (ROLLBACK) و آزادسازی منابع"]
        S_Err409["پاسخ 409 Conflict: تکمیل ظرفیت توسط درخواست همزمان دیگر"]
        S_Insert["درج رکورد رزرو در جدول Bookings با وضعیت confirmed"]
        S_HasDisc{"آیا از کد تخفیف استفاده شده؟"}
        S_IncDisc["افزایش اتمیک شمارنده کد تخفیف:\nused_count = used_count + 1"]
        S_Commit["کامیت قطعی تراکنش در PostgreSQL\n(COMMIT TRANSACTION)"]
        S_Resp201["پاسخ 201 Created و ارائه شناسه رزرو"]
    end

    B_Start --> B_Click
    B_Click --> S_Auth

    S_Auth -- "خیر" --> S_Err401
    S_Err401 --> B_Login
    B_Login --> B_Click

    S_Auth -- "بله" --> S_Form
    S_Form -- "خیر" --> S_Err400
    S_Err400 --> B_HandleConflict

    S_Form -- "بله" --> S_Atomic
    S_Atomic --> S_LockCheck
    S_LockCheck --> S_CapCheck

    S_CapCheck -- "خیر (نقض همزمانی / پر شدن)" --> S_Rollback
    S_Rollback --> S_Err409
    S_Err409 --> B_HandleConflict

    S_CapCheck -- "بله (ظرفیت تضمین شد)" --> S_Insert
    S_Insert --> S_HasDisc

    S_HasDisc -- "بله" --> S_IncDisc
    S_HasDisc -- "خیر" --> S_Commit
    S_IncDisc --> S_Commit

    S_Commit --> S_Resp201
    S_Resp201 --> B_Success
    B_Success --> B_End
```

---

## ۳. فرآیند لغو رزرو، اعتبارسنجی بازه زمانی، آزادسازی ظرفیت و بازگشت سهمیه
**Booking Cancellation & Resource Rollback Process**

### مشخصات فرآیند:
- **هدف (Goal):** چرخه عمر ابطال رزرو توسط مهمان، تضمین رعایت قوانین زمانی کنسلی (قبل از شروع سفر)، تغییر وضعیت به CANCELLED، بازگرداندن سهمیه کد تخفیف و بازگرداندن فوری ظرفیت به هتل.
- **نقش‌های درگیر (Actors):** کاربر مهمان (Guest)، سیستم (ویو لغو رزرو، اعتبارسنجی وضعیت، تراکنش PostgreSQL).
- **پیش‌شرط‌ها (Pre-conditions):**
  1. مهمان وارد حساب کاربری خود شده باشد.
  2. رزرو با وضعیت `confirmed` در حساب مهمان موجود باشد.
- **گام‌های اصلی (Main Flow):**
  1. مهمان وارد بخش «رزروهای من» شده و دکمه «لغو رزرو» را فشرده و پیام هشدار را تایید می‌کند.
  2. درخواست `POST /api/bookings/{id}/cancel/` به بک‌اند ارسال می‌شود.
  3. سیستم مالکیت رزرو را ارزیابی می‌کند (`booking.user == request.user`).
  4. سیستم وضعیت فعلی رزرو را بررسی می‌کند (`status == 'confirmed'`).
  5. سیستم شرط تاریخ را می‌سنجد: آیا تاریخ جاری قبل از تاریخ ورود است (`today < booking.check_in`)؟
  6. تراکنش پایگاه‌داده آغاز شده و وضعیت رزرو به `cancelled` تغییر می‌یابد.
  7. در صورت استفاده از کد تخفیف، شمارنده `used_count` کاهش یافته و سهمیه بازمی‌گردد.
  8. با خروج رکورد از دایره رزروهای معتبر، ظرفیت اتاق بلافاصله در ماتریس تقویم آزاد می‌شود.
  9. تراکنش کامیت شده و پیام تایید ابطال با وضعیت 200 OK نمایش می‌یابد.
- **جریان‌های استثنا و خطا (Alternative & Error Flows):**
  - **عدم انطباق مالکیت:** خطای 403 Forbidden در صورت تلاش برای لغو رزرو شخص دیگر.
  - **سپری شدن مهلت لغو:** در صورت اقدام در تاریخ ورود یا پس از آن (`today >= check_in`)، خطای 400 Bad Request صادر شده و لغو رد می‌شود.
  - **رزرو قبلاً لغو شده:** در صورت وضعیت نامعتبر، پیام خطای مناسب داده می‌شود.
- **پس‌شرط‌ها (Post-conditions):**
  - رزرو به عنوان باطله در سوابق حفظ شده، اتاق‌ها به چرخه رزرواسیون هتل بازمی‌گردند.

```mermaid
flowchart TD
    subgraph Guest["اقدامات کاربر مهمان (Guest Actions)"]
        C_Start([شروع: ورود به لیست 'رزروهای من'])
        C_Select["انتخاب رزرو فعال و کلیک روی دکمه 'لغو رزرو'"]
        C_Confirm{"تأیید اخطار لغو در پنجره دیالوگ؟"}
        C_Abort["انصراف و حفظ رزرو فعال"]
        C_Submit["ارسال درخواست لغو (POST /api/bookings/id/cancel/)"]
        C_ViewErr["مشاهده خطای سیستمی عدم امکان لغو"]
        C_Success["مشاهده برچسب 'لغو شده' و آزادسازی سوابق"]
        C_End([پایان فرآیند لغو])
    end

    subgraph System["پردازش و واکنش‌های سیستم (System Processing)"]
        S_CheckOwner{"آیا رزرو متعلق به کاربر جاری است؟\n(booking.user == request.user)"}
        S_Err403["خطای 403 Forbidden: دسترسی غیرمجاز"]
        S_CheckStatus{"وضعیت فعلی رزرو؟"}
        S_ErrNotConf["خطای 400: رزرو فعال نیست (پیش‌تر لغو شده)"]
        S_CheckDate{"آیا امروز قبل از تاریخ ورود است؟\n(today < booking.check_in)"}
        S_ErrDatePass["خطای 400: مهلت لغو سپری شده است\n(پس از شروع اقامت لغو امکان‌پذیر نیست)"]
        S_TxCancel["آغاز تراکنش لغو (transaction.atomic)"]
        S_UpdateStatus["تغییر وضعیت رزرو به cancelled"]
        S_HadDisc{"آیا از کد تخفیف استفاده شده بود؟"}
        S_RestoreDisc["کاهش شمارنده مصرف کد تخفیف (used_count - 1)"]
        S_CommitCancel["کامیت تراکنش و آزادسازی خودکار ظرفیت در تقویم"]
        S_Resp200["پاسخ 200 OK: رزرو با موفقیت باطل شد"]
    end

    C_Start --> C_Select
    C_Select --> C_Confirm

    C_Confirm -- "خیر (انصراف)" --> C_Abort
    C_Abort --> C_End

    C_Confirm -- "بله (تایید لغو)" --> C_Submit
    C_Submit --> S_CheckOwner

    S_CheckOwner -- "خیر" --> S_Err403
    S_Err403 --> C_ViewErr

    S_CheckOwner -- "بله" --> S_CheckStatus
    S_CheckStatus -- "غیر از confirmed" --> S_ErrNotConf
    S_ErrNotConf --> C_ViewErr

    S_CheckStatus -- "confirmed" --> S_CheckDate
    S_CheckDate -- "خیر (امروز >= ورود)" --> S_ErrDatePass
    S_ErrDatePass --> C_ViewErr

    S_CheckDate -- "بله (قبل از ورود)" --> S_TxCancel
    S_TxCancel --> S_UpdateStatus
    S_UpdateStatus --> S_HadDisc

    S_HadDisc -- "بله" --> S_RestoreDisc
    S_HadDisc -- "خیر" --> S_CommitCancel
    S_RestoreDisc --> S_CommitCancel

    S_CommitCancel --> S_Resp200
    S_Resp200 --> C_Success
    C_Success --> C_End
    C_ViewErr --> C_End
```

---

## ۴. فرآیند پایش ماتریس ظرفیت و تقویم وضعیت اتاق‌های پر و خالی
**Manager Room Availability Matrix & Occupancy Monitoring Process**

### مشخصات فرآیند:
- **هدف (Goal):** پایش متمرکز وضعیت اشغال هتل توسط هتلدار در قالب تقویم روزانه با محاسبه دقیق تعداد کل، پر و آزاد به ازای هر نوع اتاق.
- **نقش‌های درگیر (Actors):** مدیر هتل (Hotel Manager)، سیستم (ویو مدیریتی، گارد نقش، کوئری‌های تجمیعی پایگاه داده).
- **پیش‌شرط‌ها (Pre-conditions):**
  1. کاربر با نقش مدیر هتل (`HOTEL_MANAGER`) وارد سیستم شده باشد.
  2. هتل انتخابی متعلق به این مدیر باشد (`hotel.owner == request.user`).
- **گام‌های اصلی (Main Flow):**
  1. مدیر هتل از داشبورد مدیریتی، هتل مورد نظر و بازه تاریخی گزارش (مثلاً ۳۰ روز آینده) را انتخاب می‌کند.
  2. درخواست `GET /api/manager/hotels/{id}/availability/?date_from=...&date_to=...` ارسال می‌شود.
  3. سیستم نقش کاربر جاری را بررسی می‌کند.
  4. سیستم مالکیت مدیر بر هتل را تطبیق می‌دهد.
  5. بازه تاریخی اعتبارسنجی می‌شود (`date_to >= date_from`).
  6. سیستم کوئری تجمیعی را اجرا می‌کند:
     - استخراج انواع اتاق‌های فعال (`RoomTypes`) با موجودی کل هر کدام.
     - استخراج تمامی رزروهای تأییدشده (`confirmed`) فعال در آن بازه زمانی.
  7. سیستم ماتریس تقویمی را به ازای تک‌تک روزها محاسبه می‌کند:
     - `total_rooms` = ظرفیت اسمی اتاق
     - `booked_rooms` = مجموع اتاق‌های رزرو شده در آن تاریخ
     - `free_rooms` = `total_rooms - booked_rooms`
  8. ساختار داده تقویمی با وضعیت 200 OK ارسال شده و در فرانت‌اند به شکل جدول و تقویم رنگی (سبز: ظرفیت آزاد، قرمز: پر، نارنجی: رو به اتمام) به نمایش درمی‌آید.
- **جریان‌های استثنا و خطا (Alternative & Error Flows):**
  - **نقش نامعتبر:** در صورت کاربر غیرمدیر، خطای 403 صادر می‌شود.
  - **هتل غیر:** در صورت تلاش برای دسترسی به هتل سایر مدیران، خطای 403 یا 404 برگردانده می‌شود.
  - **بازه تاریخی نامعتبر:** در صورت `date_to < date_from`، خطای 400 Bad Request ارسال می‌گردد.
- **پس‌شرط‌ها (Post-conditions):**
  - ماتریس ظرفیت در اختیار هتلدار قرار گرفته و مبنای تصمیم‌گیری برای قیمت‌گذاری یا تعریف تخفیف می‌گردد.

```mermaid
flowchart TD
    subgraph Manager["اقدامات مدیر هتل (Manager Actions)"]
        M_Start([شروع: ورود به داشبورد مدیریت هتل])
        M_Select["انتخاب هتل و تعیین بازه تاریخی گزارش (date_from تا date_to)"]
        M_Submit["درخواست مشاهده تقویم موجودی (GET /api/manager/hotels/id/availability/)"]
        M_FixRange["اصلاح بازه تاریخی در فرم فیلتر"]
        M_ViewDeny["مشاهده پیام خطای عدم دسترسی"]
        M_RenderGrid["مشاهده ماتریس تقویمی:\nتفکیک روزانه اتاق‌های کل، رزرو شده و آزاد"]
        M_End([پایان فرآیند پایش])
    end

    subgraph System["پردازش و واکنش‌های سیستم (System Processing)"]
        S_Role{"آیا کاربر نقش مدیر هتل دارد؟\n(user.role == 'HOTEL_MANAGER')"}
        S_ErrRole403["خطای 403: دسترسی ویژه مدیران"]
        S_Owner{"آیا هتل متعلق به مدیر جاری است؟\n(hotel.owner == request.user)"}
        S_ErrOwner403["خطای 403 Forbidden: عدم دسترسی به داده هتل دیگران"]
        S_DateRange{"آیا بازه تاریخی معتبر است؟\n(date_to >= date_from)"}
        S_ErrRange400["خطای 400: بازه تاریخی نامعتبر"]
        S_FetchRooms["استعلام انواع اتاق فعال هتل و موجودی اسمی (total_rooms)"]
        S_FetchBookings["استعلام رزروهای تاییدشده (confirmed) فعال در بازه زمانی"]
        S_Aggregate["تجمیع روزانه در ماتریس تقویمی:\ntotal, booked, free = total - booked"]
        S_Resp200["ارسال ساختار داده ماتریسی با کد 200 OK"]
    end

    M_Start --> M_Select
    M_Select --> M_Submit
    M_Submit --> S_Role

    S_Role -- "خیر" --> S_ErrRole403
    S_ErrRole403 --> M_ViewDeny

    S_Role -- "بله" --> S_Owner
    S_Owner -- "خیر" --> S_ErrOwner403
    S_ErrOwner403 --> M_ViewDeny

    S_Owner -- "بله" --> S_DateRange
    S_DateRange -- "خیر" --> S_ErrRange400
    S_ErrRange400 --> M_FixRange
    M_FixRange --> M_Submit

    S_DateRange -- "بله" --> S_FetchRooms
    S_FetchRooms --> S_FetchBookings
    S_FetchBookings --> S_Aggregate
    S_Aggregate --> S_Resp200
    S_Resp200 --> M_RenderGrid
    M_RenderGrid --> M_End
    M_ViewDeny --> M_End
```

---

## ۵. فرآیند (امتیازی): ثبت و اعتبارسنجی نظر مهمان بر اساس سابقه اقامت قطعی
**Verified Stay Review & Rating Calculation Process**

### مشخصات فرآیند:
- **هدف (Goal):** جلوگیری از نظرات فیک و ارتقای اعتبار سامانه از طریق محدودسازی ثبت امتیاز و بازخورد تنها به مهمانانی که اقامت قطعی در هتل داشته و سفرشان به پایان رسیده است.
- **نقش‌های درگیر (Actors):** کاربر مهمان (Guest)، سیستم (ویو نظرات، ReviewForm، پایگاه داده PostgreSQL).
- **پیش‌شرط‌ها (Pre-conditions):**
  1. مهمان لاگین کرده باشد.
  2. کاربر دارای حداقل یک رزرو تأییدشده با تاریخ خروج در گذشته باشد (`Booking: status='confirmed' & check_out <= today`).
- **گام‌های اصلی (Main Flow):**
  1. مهمان فرم نظر و رتبه‌بندی (۱ تا ۵ ستاره) را پر کرده و ارسال می‌کند (`POST /api/reviews/`).
  2. سیستم سابقه اقامت مهمان در این هتل را در دیتابیس استعلام می‌کند.
  3. اعتبارسنجی فیلدها با `ReviewForm` صورت می‌گیرد.
  4. سیستم بررسی می‌کند آیا مهمان قبلاً برای این هتل نظری ثبت کرده است؟
  5. در صورت ثبت قبلی، نظر به‌روزرسانی (Update) شده و در غیر این صورت نظر جدید درج (Insert) می‌گردد (قاعده یک نظر به ازای هر مهمان در هر هتل).
  6. میانگین رتبه ستاره‌های هتل با دستور Aggregate در دیتابیس مجدداً محاسبه و به‌روزرسانی می‌شود.
  7. نظر ثبت‌شده همراه با میانگین جدید هتل برای عموم به نمایش درمی‌آید.
- **جریان‌های استثنا و خطا (Alternative & Error Flows):**
  - **عدم سابقه اقامت:** خطای 403 Forbidden با پیام «تنها مهمانانی که در این هتل اقامت داشته‌اند مجاز به ثبت نظر هستند».
  - **امتیاز نامعتبر:** خطای 400 Bad Request در صورت ثبت امتیاز خارج از ۱ تا ۵.
- **پس‌شرط‌ها (Post-conditions):**
  - نظر معتبر ثبت شده و میانگین رضایت هتل بر اساس بازخورد واقعی تغییر یافته است.

```mermaid
flowchart TD
    subgraph Guest["اقدامات کاربر مهمان (Guest Actions)"]
        R_Start([شروع: صفحه هتل پس از اتمام اقامت])
        R_Fill["تکمیل فرم: امتیاز (۱ تا ۵ ستاره) و متن بازخورد"]
        R_Submit["ارسال فرم نظر (POST /api/reviews/)"]
        R_ViewDeny["مشاهده خطای عدم اهلیت (عدم سابقه اقامت قطعی)"]
        R_Success["مشاهده نظر ثبت‌شده و به‌روزرسانی میانگین امتیاز هتل"]
        R_End([پایان فرآیند ثبت بازخورد])
    end

    subgraph System["پردازش و واکنش‌های سیستم (System Processing)"]
        S_AuthReview{"آیا کاربر لاگین است؟"}
        S_Err401Review["خطای 401: ورود به سیستم الزامی است"]
        S_CheckStay{"آیا کاربر سابقه اقامت قطعی در این هتل دارد؟\n(Booking: confirmed & check_out <= today)"}
        S_ErrNoStay["خطای 403 Forbidden:\nثبت نظر تنها منوط به تجربه اقامت قطعی در هتل است"]
        S_FormReview{"اعتبارسنجی فیلدها:\nامتیاز بین ۱ تا ۵ و متن معتبر"}
        S_Err400Review["خطای 400: امتیاز یا متن نامعتبر"]
        S_CheckPrior{"آیا کاربر قبلاً برای این هتل نظر ثبت کرده؟"}
        S_UpdateReview["به‌روزرسانی نظر قبلی مهمان (Update)"]
        S_InsertReview["درج نظر جدید در جدول reviews (Insert)"]
        S_Recalc["محاسبه مجدد میانگین امتیاز هتل با کوئری Aggregate"]
        S_Resp201["پاسخ 200/201 و بازگرداندن اطلاعات ثبت‌شده"]
    end

    R_Start --> R_Fill
    R_Fill --> R_Submit
    R_Submit --> S_AuthReview

    S_AuthReview -- "خیر" --> S_Err401Review
    S_Err401Review --> R_ViewDeny

    S_AuthReview -- "بله" --> S_CheckStay
    S_CheckStay -- "خیر (فاقد اقامت)" --> S_ErrNoStay
    S_ErrNoStay --> R_ViewDeny

    S_CheckStay -- "بله" --> S_FormReview
    S_FormReview -- "خیر" --> S_Err400Review
    S_Err400Review --> R_Fill

    S_FormReview -- "بله" --> S_CheckPrior
    S_CheckPrior -- "بله" --> S_UpdateReview
    S_CheckPrior -- "خیر" --> S_InsertReview

    S_UpdateReview --> S_Recalc
    S_InsertReview --> S_Recalc
    S_Recalc --> S_Resp201
    S_Resp201 --> R_Success
    R_Success --> R_End
    R_ViewDeny --> R_End
```

---

## ضمیمه فنی: دیاگرام‌های توالی (Sequence Diagrams)

### ۱. دیاگرام توالی: فرآیند ثبت رزرو اتاق توسط مهمان
```mermaid
sequenceDiagram
    autonumber
    actor Guest as مهمان (مرورگر)
    participant UI as React SPA (BookingView)
    participant MW as Django Middleware
    participant View as CreateBookingView
    participant Form as BookingForm
    participant Manager as BookingManager
    participant DB as PostgreSQL DB

    Guest->>UI: انتخاب تاریخ‌ها، نوع اتاق و وارد کردن کد تخفیف
    UI->>View: POST /api/bookings/quote/ (محاسبه قیمت)
    View-->>UI: 200 OK (مبلغ خالص، تخفیف، کل و وضعیت ظرفیت)
    Guest->>UI: کلیک روی دکمه "تأیید و ثبت رزرو"
    UI->>MW: POST /api/bookings/ [با Session Cookie و X-CSRFToken]
    MW->>MW: RequestLogMiddleware (ثبت لاگ ورودی درخواست)
    MW->>MW: SessionMiddleware (احراز هویت کاربر و تطبیق نشست)
    MW->>View: ارسال درخواست معتبر به CreateBookingView
    View->>Form: ارسال داده‌ها به BookingForm.is_valid()
    Form-->>View: داده‌های تمیز (Cleaned Data) معتبر است
    View->>Manager: فراخوانی create_booking_with_availability(...)
    activate Manager
    Manager->>DB: BEGIN TRANSACTION (انحصاری / Atomic)
    Manager->>DB: محاسبه تعداد رزروهای تداخل‌دار فعال در بازه زمانی
    DB-->>Manager: تعداد اتاق‌های رزرو شده
    alt ظرفیت آزاد < تعداد درخواستی
        Manager->>DB: ROLLBACK TRANSACTION
        Manager-->>View: خطای عدم موجودی (AvailabilityError)
        View-->>UI: 409 Conflict {"message": "ظرفیت اتاق تکمیل شده است"}
        UI-->>Guest: نمایش هشدار تکمیل ظرفیت
    else ظرفیت کافی است
        Manager->>DB: INSERT INTO bookings_booking (status='confirmed', ...)
        opt کد تخفیف معتبر استفاده شده
            Manager->>DB: UPDATE bookings_discountcode SET used_count = used_count + 1
        end
        Manager->>DB: COMMIT TRANSACTION
        Manager-->>View: شیء رزرو ایجاد شده
        deactivate Manager
        View-->>UI: 201 Created {"data": {"booking_id": 12, "status": "confirmed"}}
        UI-->>Guest: نمایش پیام موفقیت‌آمیز و رسید رزرو
    end
```

### ۲. دیاگرام توالی: مشاهده ماتریس اتاق‌های آزاد/رزرو شده توسط مدیر
```mermaid
sequenceDiagram
    autonumber
    actor Manager as مدیر هتل (مرورگر)
    participant UI as React SPA (ManagerAvailability)
    participant MW as Django Middleware
    participant View as ManagerAvailabilityView
    participant MgrLogic as HotelQuerySet / AvailabilityLogic
    participant DB as PostgreSQL DB

    Manager->>UI: انتخاب هتل و بازه زمانی گزارش (مثلاً ۷ یا ۳۰ روز آینده)
    UI->>MW: GET /api/manager/hotels/{id}/availability/?date_from=...&date_to=...
    MW->>MW: بررسی نشست، احراز هویت و بررسی نقش مدیر (role == 'manager')
    MW->>View: هدایت به ManagerAvailabilityView
    View->>DB: بررسی مالکیت هتل (hotel.owner == request.user)
    alt مدیر مالک هتل نیست
        View-->>UI: 403 Forbidden {"message": "دسترسی غیرمجاز به اطلاعات این هتل"}
        UI-->>Manager: نمایش خطای عدم دسترسی
    else مالکیت تأیید شد
        View->>MgrLogic: دریافت وضعیت دسترسی‌پذیری به ازای هر نوع اتاق و هر روز
        activate MgrLogic
        MgrLogic->>DB: SELECT اتاق‌های فعال هتل (RoomTypes)
        DB-->>MgrLogic: لیست انواع اتاق‌ها و موجودی اسمی (total_rooms)
        MgrLogic->>DB: SELECT رزروهای با وضعیت confirmed در بازه تاریخ مورد نظر
        DB-->>MgrLogic: لیست رزروهای فعال
        MgrLogic->>MgrLogic: تجمیع روزانه: total_rooms, booked_rooms, free_rooms
        MgrLogic-->>View: ساختار داده ماتریسی دسترسی‌پذیری
        deactivate MgrLogic
        View-->>UI: 200 OK {"data": {"room_types": [...]}}
        UI-->>Manager: رندر جدول و تقویم وضعیت اتاق‌ها با برچسب‌های رنگی (آزاد / تکمیل)
    end
```
