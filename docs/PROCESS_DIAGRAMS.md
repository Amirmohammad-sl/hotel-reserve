# PROCESS DIAGRAMS (دیاگرام‌های فرآیندی سیستم رزرواسیون هتل)

این مستند شامل دیاگرام‌های جریان کلی سیستم، دیاگرام‌های جریان به تفکیک ماژول‌ها (اپلیکیشن‌های جنگو) و دیاگرام‌های توالی (Sequence Diagrams) منطبق بر نیازمندی‌های پروژه و گزارش درسی است.

---

## ۱. دیاگرام جریان کلی سیستم (Overall System Flow)

نمودار زیر تعامل دو نقش اصلی سامانه (**مدیر هتل / Hotel Manager** و **مهمان / Guest**) با لایه کاربری (React SPA)، لایه منطق بک‌اند (Django Views/Forms/Managers) و پایگاه داده (PostgreSQL) را نشان می‌دهد.

```mermaid
flowchart TD
    subgraph Users["کاربران سامانه"]
        Guest["مهمان (Guest)"]
        Manager["مدیر هتل (Hotel Manager)"]
    end

    subgraph Frontend["لایه فرانت‌اند (React SPA)"]
        UI_Auth["صفحات احراز هویت (ورود/ثبت‌نام)"]
        UI_Guest["صفحات مهمان (جستجو، جزئیات، استعلام قیمت، رزرو)"]
        UI_Manager["داشبورد مدیر (مدیریت هتل، اتاق‌ها، تخفیف‌ها، پایش رزروها)"]
    end

    subgraph Backend["لایه بک‌اند (Django Framework)"]
        MW["Middleware (لاگینگ، احراز هویت نشست و CSRF)"]
        App_Accounts["اپلیکیشن accounts (مدیریت کاربران و نقش‌ها)"]
        App_Hotels["اپلیکیشن hotels (هتل‌ها، انواع اتاق، امکانات)"]
        App_Bookings["اپلیکیشن bookings (استعلام، رزرو، ظرفیت، کدهای تخفیف)"]
        App_Reviews["اپلیکیشن reviews (ثبت و نمایش نظرات و امتیازها)"]
    end

    subgraph DB["پایگاه داده (PostgreSQL)"]
        DB_Tables[("جداول: Users, Hotels, RoomTypes, Bookings, Discounts, Reviews")]
    end

    Guest -->|ثبت‌نام / ورود| UI_Auth
    Manager -->|ثبت‌نام / ورود| UI_Auth
    Guest -->|جستجو و رزرو| UI_Guest
    Manager -->|تعریف هتل و مدیریت| UI_Manager

    UI_Auth -->|درخواست‌های احراز هویت| MW
    UI_Guest -->|درخواست‌های عمومی و رزرو| MW
    UI_Manager -->|درخواست‌های مدیریتی| MW

    MW --> App_Accounts
    MW --> App_Hotels
    MW --> App_Bookings
    MW --> App_Reviews

    App_Accounts --> DB_Tables
    App_Hotels --> DB_Tables
    App_Bookings --> DB_Tables
    App_Reviews --> DB_Tables
```

### 📝 توضیحات جریان کلی:
- **چه اتفاقی می‌افتد**: کاربران از طریق رابط تک‌صفحه‌ای (React) درخواست‌های خود را ارسال می‌کنند. این درخواست‌ها از لایه‌های اعتبارسنجی میانی (لاگ سیستم، کوکی Session و بررسی CSRF) عبور کرده و به اپلیکیشن متناظر در جنگو می‌رسند. در بک‌اند، داده‌ها با Django Forms بررسی و سپس از طریق Managers و ORM جنگو در پایگاه داده PostgreSQL ذخیره یا بازیابی می‌شوند.
- **آغازگر**: مهمان یا مدیر هتل از طریق مرورگر.

---

## ۲. دیاگرام‌های جریان به تفکیک ماژول‌ها (Per-App Process Flows)

### ۲.۱. ماژول حساب‌های کاربری (`accounts`)

فرآیند ثبت‌نام، تخصیص نقش، تأیید ایمیل و ورود به سامانه:

```mermaid
flowchart TD
    Start([شروع]) --> Form[تکمیل فرم ثبت‌نام / ورود توسط کاربر]
    Form --> ActionType{نوع عملیات؟}

    ActionType -->|ثبت‌نام| RegForm["اعتبارسنجی فرم (UserRegisterForm)"]
    RegForm --> RegValid{اطلاعات معتبر است؟}
    RegValid -->|خیر| RegErrors[نمایش خطاهای فرم 400] --> Form
    RegValid -->|بله| CreateUser["ایجاد کاربر با نقش انتخابی (guest یا manager)"]
    CreateUser --> GenToken["تولید توکن تأیید ایمیل (TimestampSigner)"]
    GenToken --> SendMail["ارسال لینک تأیید به ایمیل کاربر"]
    SendMail --> SetSessionAuto["ورود اولیه و ایجاد Session"]

    ActionType -->|ورود| AuthForm["اعتبارسنجی اعتبارنامه‌ها (UserLoginForm)"]
    AuthForm --> AuthCheck{نام کاربری و رمز صحیح است؟}
    AuthCheck -->|خیر| AuthError[خطای ورود 401] --> Form
    AuthCheck -->|بله| SetSession["ایجاد نشست (Session Cookie) و کوکی CSRF"]

    SetSessionAuto --> CheckRole
    SetSession --> CheckRole{نقش کاربر چیست؟}

    CheckRole -->|guest| GuestDash[هدایت به صفحه اصلی / پنل مهمان]
    CheckRole -->|manager| ManagerDash[هدایت به داشبورد مدیریت هتل]

    GuestDash --> End([پایان])
    ManagerDash --> End
```

#### 📝 توضیحات ماژول `accounts`:
- **چه اتفاقی می‌افتد**: کاربر مشخصات خود را شامل نام کاربری، ایمیل، کلمه عبور و نقش (مهمان یا مدیر) وارد می‌کند. سیستم پس از اعتبارسنجی، حساب کاربری را ذخیره کرده و توکن امن تأیید ایمیل را ایجاد می‌نماید. در ورود موفق، کوکی‌های Session و CSRF تنظیم شده و کاربر بر اساس نقش به مسیر مناسب هدایت می‌شود.
- **آغازگر**: کاربر جدید یا موجود در سامانه.

---

### ۲.۲. ماژول هتل‌ها و اتاق‌ها (`hotels`)

فرآیند تعریف هتل و اتاق توسط مدیر هتل، در کنار فرآیند جستجو و مشاهده توسط مهمان:

```mermaid
flowchart TD
    subgraph ManagerFlow["فرآیند مدیر هتل (Manager)"]
        M_Start([ورود مدیر]) --> M_HotelForm["ثبت مشخصات هتل (نام، شهر، آدرس، ستاره، تصویر)"]
        M_HotelForm --> M_SaveHotel["ذخیره هتل با مالکیت کاربر جاری (owner = request.user)"]
        M_SaveHotel --> M_RoomForm["تعریف انواع اتاق (RoomType: عنوان، ظرفیت، قیمت، تعداد موجودی، امکانات)"]
        M_RoomForm --> M_SaveRoom["ذخیره نوع اتاق و اتصال به هتل"]
    end

    subgraph GuestFlow["فرآیند مهمان (Guest & Public)"]
        G_Start([ورود به سامانه]) --> G_Search["ورود پارامترهای جستجو: شهر، تاریخ ورود/خروج، تعداد نفرات"]
        G_Search --> G_Filter["کوئری فیلتر هتل‌ها و بررسی دسترسی‌پذیری اولیه"]
        G_Filter --> G_List["نمایش لیست هتل‌های دارای ظرفیت همراه با حداقل قیمت"]
        G_List --> G_Detail["انتخاب هتل و مشاهده جزئیات + انواع اتاق و امکانات"]
    end
```

#### 📝 توضیحات ماژول `hotels`:
- **چه اتفاقی می‌افتد**: مدیر هتل می‌تواند هتل‌های خود و انواع اتاق‌های زیرمجموعه (با مشخصاتی چون ظرفیت، امکانات رفاهی، موجودی کل اتاق‌ها و قیمت هر شب) را تعریف و ویرایش کند. از سوی دیگر، کاربران می‌توانند بر اساس شهر، بازه زمانی و ظرفیت مورد نیاز به جستجوی هتل‌ها بپردازند و جزئیات هر هتل و امکانات اتاق‌ها را مشاهده نمایند.
- **آغازگر**: مدیر هتل برای ایجاد داده؛ مهمان برای جستجو و مشاهده.

---

### ۲.۳. ماژول رزروها و تخفیف‌ها (`bookings`)

فرآیند استعلام قیمت، اعتبارسنجی کد تخفیف، ثبت رزرو قطعی با بررسی همزمانی، و لغو رزرو:

```mermaid
flowchart TD
    Start([شروع فرآیند رزرو]) --> SelectRoom["انتخاب نوع اتاق و بازه اقامت (check_in, check_out)"]
    SelectRoom --> QuoteReq["درخواست استعلام قیمت (POST /api/bookings/quote/)"]
    QuoteReq --> HasDiscount{آیا کد تخفیف وارد شده؟}

    HasDiscount -->|بله| ValidateCode["بررسی کد تخفیف (فعال بودن، تاریخ اعتبار، سقف استفاده، هتل مرتبط)"]
    ValidateCode --> CalcPrice["محاسبه قیمت: (تعداد شب * قیمت) - مبلغ تخفیف"]
    HasDiscount -->|خیر| CalcPrice

    CalcPrice --> ShowQuote["نمایش پیش‌فاکتور شفاف به مهمان"]
    ShowQuote --> ConfirmBooking["تأیید نهایی رزرو توسط مهمان (POST /api/bookings/)"]

    ConfirmBooking --> AtomicTrans["آغاز تراکنش امن اتمیک (transaction.atomic)"]
    AtomicTrans --> LockCheck["بررسی موجودی در بازه زمانی:\n(موجودی کل - مجموع اتاق‌های رزرو شده فعال) >= تعداد درخواستی"]

    LockCheck --> Available{ظرفیت کافی است؟}
    Available -->|خیر| Rollback["بروز خطای 409 (عدم ظرفیت) و انصراف از رزرو"] --> End([پایان])
    Available -->|بله| CreateBooking["ثبت سند رزرو با وضعیت confirmed"]
    CreateBooking --> IncDiscount["افزایش شمارنده استفاده کد تخفیف (used_count + 1)"]
    IncDiscount --> Commit["ثبت نهایی تراکنش (Commit) و ارسال شناسه رزرو به کاربر"]

    Commit --> GuestMine["مشاهده رزرو در لیست 'رزروهای من'"]

    GuestMine --> CancelCheck{درخواست لغو رزرو توسط مهمان؟}
    CancelCheck -->|بله| CanCancel{تاریخ ورود در آینده است؟}
    CanCancel -->|بله| DoCancel["تغییر وضعیت به cancelled، بازگرداندن سهمیه کد تخفیف و آزادسازی ظرفیت"]
    CanCancel -->|خیر| ErrCancel["خطا: پس از تاریخ ورود امکان لغو وجود ندارد"]
    CancelCheck -->|خیر| End
    DoCancel --> End
    ErrCancel --> End
```

#### 📝 توضیحات ماژول `bookings`:
- **چه اتفاقی می‌افتد**: مهمان ابتدا پیش‌فاکتور رزرو را مشاهده و در صورت تمایل کد تخفیف اعمال می‌کند. پس از تأیید نهایی، بک‌اند در قالب یک تراکنش اتمیک بررسی می‌کند که در تک‌تک شب‌های اقامت، اتاق آزاد کافی وجود داشته باشد. پس از ثبت موفق، وضعیت رزرو `confirmed` شده و کد تخفیف به‌روزرسانی می‌شود. در صورت لغو پیش از موعد، ظرفیت مجدداً آزاد می‌گردد.
- **آغازگر**: مهمان هتل.

---

### ۲.۴. ماژول نظرات و امتیازدهی (`reviews` - بخش امتیازی)

فرآیند ثبت نظر و امتیاز توسط مهمانان و نمایش در صفحه هتل:

```mermaid
flowchart TD
    Start([شروع]) --> GuestReview["مهمان فرم نظر و امتیاز (1 تا 5) را تکمیل می‌کند"]
    GuestReview --> CheckStay{آیا کاربر در این هتل اقامت داشته؟}
    CheckStay -->|خیر| Deny["خطای دسترسی 403: ثبت نظر فقط برای مهمانان مقیم مجاز است"]
    CheckStay -->|بله| CheckDuplicate{آیا قبلاً برای این هتل نظر ثبت کرده؟}
    CheckDuplicate -->|بله| UpdateReview["به‌روزرسانی نظر قبلی کاربر"]
    CheckDuplicate -->|خیر| InsertReview["ثبت نظر جدید در جدول reviews"]

    UpdateReview --> RecalcRating["محاسبه مجدد میانگین ستاره/امتیاز هتل"]
    InsertReview --> RecalcRating
    RecalcRating --> Display["نمایش در صفحه جزئیات هتل برای عموم کاربران"] --> End([پایان])
    Deny --> End
```

#### 📝 توضیحات ماژول `reviews`:
- **چه اتفاقی می‌افتد**: تنها کاربرانی که اقامت تأیید شده در هتل داشته‌اند می‌توانند امتیاز و متن نظر خود را ثبت کنند. پس از ثبت، میانگین امتیاز هتل به‌روزرسانی شده و در صفحه عمومی هتل نمایش داده می‌شود.
- **آغازگر**: مهمان هتل پس از انجام اقامت.

---

## ۳. دیاگرام‌های توالی (Sequence Diagrams)

### ۳.۱. دیاگرام توالی: فرآیند رزرو اتاق توسط مهمان (Guest Books a Room)

این دیاگرام توالی دقیق ارسال درخواست، اعتبارسنجی‌ها، بررسی ظرفیت و ثبت نهایی در بک‌اند را به تصویر می‌کشد:

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
    Guest->>UI: کلیک روی دکمه "تأیید و پرداخت/ثبت رزرو"
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

#### 📝 توضیحات توالی رزرو اتاق:
1. کاربر پس از انتخاب اتاق و بازه زمانی، پیش‌فاکتور را دریافت می‌کند.
2. با فشردن دکمه ثبت رزرو، فرانت‌اند ری‌اکت درخواست `POST` را با هدر `X-CSRFToken` و کوکی نشست کاربر به بک‌اند ارسال می‌کند.
3. میدل‌ور جنگو مشخصات درخواست را لاگ کرده و احراز هویت نشست را تأیید می‌کند.
4. فرم جنگو فیلدها و شروط پایه (بزرگتر بودن تاریخ خروج از ورود، تناسب نفرات با ظرفیت) را می‌سنجد.
5. لایه Manager در یک تراکنش امن پایگاه داده، ظرفیت باقی‌مانده را استعلام می‌کند. اگر رزروهای همپوشان مانع ظرفیت شوند تراکنش بازگردانده شده و خطای `409 Conflict` بازمی‌گردد؛ در غیر این صورت، سند رزرو صادر و تراکنش کامیت می‌شود.

---

### ۳.۲. دیاگرام توالی: مشاهده وضعیت و اتاق‌های آزاد/رزرو شده توسط مدیر (Manager Views Booked & Free Rooms)

این دیاگرام نحوه استعلام و آماده‌سازی ماتریس تقویمی اتاق‌ها را توسط مدیر هتل نمایش می‌دهد:

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
        DB-->>MgrLogic: لیست انواع اتاق‌ها و موجودی اسمی (quantity)
        MgrLogic->>DB: SELECT رزروهای با وضعیت confirmed در بازه تاریخ مورد نظر
        DB-->>MgrLogic: لیست رزروهای فعال
        MgrLogic->>MgrLogic: تجمیع روزانه: total_quantity, booked_count, free_count
        MgrLogic-->>View: ساختار داده ماتریسی دسترسی‌پذیری
        deactivate MgrLogic
        View-->>UI: 200 OK {"data": {"room_types": [...]}}
        UI-->>Manager: رندر جدول و تقویم وضعیت اتاق‌ها با برچسب‌های رنگی (آزاد / تکمیل)
    end
```

#### 📝 توضیحات توالی مشاهده دسترسی‌پذیری توسط مدیر:
1. مدیر هتل با تعیین شناسه هتل و بازه تاریخی مورد نظر خود، درخواست دریافت تقویم وضعیت اتاق‌ها را ثبت می‌کند.
2. سیستم بررسی می‌کند که آیا کاربر جاری مالک هتل انتخابی است یا خیر (جلوگیری از دسترسی مدیران دیگر به داده‌های هتل رقیب).
3. منطق کوئری بک‌اند، انواع اتاق‌ها و رزروهای فعال بازه زمانی را از دیتابیس واکشی کرده و به ازای هر روز اقامت، تعداد کل موجودی، تعداد رزرو شده و تعداد اتاق‌های آزاد را به دقت تجمیع می‌کند.
4. فرانت‌اند این ساختار ماتریسی را به شکل تقویم یا جدولی شفاف و رنگی (نشانگر روزهای پر و خالی) به مدیر نمایش می‌دهد.
