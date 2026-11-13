"""Management command to populate test demo data for the hotel reservation system.

Requirements:
- Idempotent: running multiple times does not create duplicates.
- Supports --reset option to wipe demo records and recreate from scratch.
- Seeds 2 managers, 5 guests.
- Seeds >= 6 hotels in >= 3 cities.
- Seeds 2-4 room types each with amenities.
- Seeds discount codes.
- Seeds ~20 bookings (past, current, future, cancelled).
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking, DiscountCode
from apps.hotels.models import Amenity, Hotel, RoomType


DEMO_MANAGERS = [
    {
        "username": "manager1",
        "email": "manager1@hotel.com",
        "password": "Manager123!",
        "first_name": "علیرضا",
        "last_name": "رضایی",
        "phone": "09121111111",
        "role": User.Role.MANAGER,
    },
    {
        "username": "manager2",
        "email": "manager2@hotel.com",
        "password": "Manager123!",
        "first_name": "سارا",
        "last_name": "احمدی",
        "phone": "09132222222",
        "role": User.Role.MANAGER,
    },
]

DEMO_GUESTS = [
    {
        "username": "guest1",
        "email": "guest1@test.com",
        "password": "Guest123!",
        "first_name": "علی",
        "last_name": "محمدی",
        "phone": "09123333333",
        "role": User.Role.GUEST,
    },
    {
        "username": "guest2",
        "email": "guest2@test.com",
        "password": "Guest123!",
        "first_name": "مریم",
        "last_name": "کریمی",
        "phone": "09124444444",
        "role": User.Role.GUEST,
    },
    {
        "username": "guest3",
        "email": "guest3@test.com",
        "password": "Guest123!",
        "first_name": "رضا",
        "last_name": "حسینی",
        "phone": "09125555555",
        "role": User.Role.GUEST,
    },
    {
        "username": "guest4",
        "email": "guest4@test.com",
        "password": "Guest123!",
        "first_name": "زهرا",
        "last_name": "موسوی",
        "phone": "09126666666",
        "role": User.Role.GUEST,
    },
    {
        "username": "guest5",
        "email": "guest5@test.com",
        "password": "Guest123!",
        "first_name": "امیر",
        "last_name": "صادقی",
        "phone": "09127777777",
        "role": User.Role.GUEST,
    },
]

DEMO_AMENITIES = [
    {"name": "WiFi", "description": "اینترنت پرسرعت بی‌سیم رایگان در اتاق و لابی"},
    {"name": "Breakfast", "description": "صبحانه بوفه سلف‌سرویس گرم و سرد رایگان"},
    {"name": "Pool", "description": "استخر سرپوشیده، سونا، جکوزی و اسپا"},
    {"name": "Parking", "description": "پارکینگ اختصاصی و مسقف رایگان برای میهمانان"},
    {"name": "Gym", "description": "سالن بدنسازی مجهز با مربی اختصاصی"},
    {"name": "Room Service", "description": "خدمات اتاق و روم‌سرویس ۲۴ ساعته"},
    {"name": "Air Conditioning", "description": "سیستم تهویه مطبوع هوشمند فن‌کوئل"},
]

DEMO_HOTELS = [
    # Manager 1 hotels (Tehran, Isfahan, Mashhad, Tabriz)
    {
        "owner_username": "manager1",
        "name": "هتل اسپیناس پالاس",
        "city": "تهران",
        "address": "تهران، سعادت‌آباد، میدان بهرود، خیابان عابدی، کوچه ۳۳",
        "description": "هتل پنج ستاره لوکس با نمایی بی‌نظیر از شهر تهران و رشته‌کوه البرز.",
        "star_rating": 5,
        "latitude": 35.789100,
        "longitude": 51.365300,
        "image_url": "/hotels/espinas-palace.jpg",
        "room_types": [
            {
                "title": "اتاق یک‌تخته استاندارد",
                "description": "اتاق دنج و مجهز برای اقامت انفرادی کاری و توریستی.",
                "capacity": 1,
                "price_per_night": 2200000,
                "quantity": 6,
                "amenities": ["WiFi", "Breakfast", "Air Conditioning"],
            },
            {
                "title": "اتاق دوتخته دلوکس",
                "description": "اتاق بزرگ با تخت کینگ دونفره و نمای رو به شهر.",
                "capacity": 2,
                "price_per_night": 4200000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Pool", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت پرزیدنتال",
                "description": "سوئیت مجلل با اتاق خواب مستر، سالن نشیمن و جکوزی اختصاصی.",
                "capacity": 4,
                "price_per_night": 8900000,
                "quantity": 3,
                "amenities": ["WiFi", "Breakfast", "Pool", "Parking", "Gym", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "ESPINAS20",
                "percent": 20,
                "valid_from_offset": -30,
                "valid_to_offset": 120,
                "max_uses": 50,
            },
            {
                "code": "VIP10",
                "percent": 10,
                "valid_from_offset": -60,
                "valid_to_offset": 180,
                "max_uses": 100,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل پارسیان آزادی",
        "city": "تهران",
        "address": "تهران، تقاطع بزرگراه چمران و یادگار امام",
        "description": "از مدرن‌ترین و با سابقه‌ترین هتل‌های پنج ستاره بین‌المللی در شمال تهران.",
        "star_rating": 5,
        "latitude": 35.792500,
        "longitude": 51.388200,
        "image_url": "/hotels/parsian-azadi.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته توئین استاندارد",
                "description": "دو تخت یک‌نفره با امکانات مدرن و دسترسی سریع به بزرگراه‌ها.",
                "capacity": 2,
                "price_per_night": 3600000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
            {
                "title": "سوئیت جونیور",
                "description": "سوئیت آرامش‌بخش مناسب سفرهای خانوادگی و کاری طولانی‌مدت.",
                "capacity": 3,
                "price_per_night": 5800000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "AZADI15",
                "percent": 15,
                "valid_from_offset": -20,
                "valid_to_offset": 90,
                "max_uses": 30,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل بین‌المللی اسپیناس بلوار",
        "city": "تهران",
        "address": "تهران، بلوار کشاورز، بین خیابان فلسطین و نادری، پلاک ۱۲۶",
        "description": "نخستین هتل پنج ستاره نوساز پایتخت در قلب فرهنگی و تجاری بلوار کشاورز.",
        "star_rating": 5,
        "latitude": 35.708300,
        "longitude": 51.401400,
        "image_url": "/hotels/espinas-blvd.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به بلوار",
                "description": "چشم‌انداز خاطره‌انگیز درختان کهنسال بلوار کشاورز با تجهیزات مدرن.",
                "capacity": 2,
                "price_per_night": 3900000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Pool", "Air Conditioning"],
            },
            {
                "title": "سوئیت خانوادگی اسپیناس",
                "description": "فضای بزرگ و آرامش‌بخش خانوادگی با امکانات ویژه پذیرایی.",
                "capacity": 4,
                "price_per_night": 6500000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Pool", "Parking", "Gym", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "BLVD15",
                "percent": 15,
                "valid_from_offset": -15,
                "valid_to_offset": 90,
                "max_uses": 40,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل عباسی",
        "city": "اصفهان",
        "address": "اصفهان، خیابان چهارباغ عباسی، خیابان آمادگاه",
        "description": "کهن‌ترین مهمانسرای جهان با معماری بی‌نظیر دوران صفوی و حیاط مرکزی رویایی.",
        "star_rating": 5,
        "latitude": 32.651400,
        "longitude": 51.670200,
        "image_url": "/hotels/abbasi.jpg",
        "room_types": [
            {
                "title": "اتاق سنتی رو به باغ",
                "description": "اتاق اصیل ایرانی با گچ‌بری چشم‌نواز و منظره باغ تاریخی عباسی.",
                "capacity": 2,
                "price_per_night": 5100000,
                "quantity": 12,
                "amenities": ["WiFi", "Breakfast", "Room Service", "Air Conditioning"],
            },
            {
                "title": "اتاق یک‌تخته چشم‌انداز پردیس",
                "description": "اقامتی دلنشین در دل تاریخ هنر و معماری اصفهان.",
                "capacity": 1,
                "price_per_night": 2800000,
                "quantity": 5,
                "amenities": ["WiFi", "Breakfast", "Air Conditioning"],
            },
            {
                "title": "سوئیت صفوی",
                "description": "سوئیت فاخر با نقاشی‌های تذهیب، منبت‌کاری و مبلمان دست‌ساز سنتی.",
                "capacity": 4,
                "price_per_night": 9500000,
                "quantity": 2,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "ISFAHAN25",
                "percent": 25,
                "valid_from_offset": -15,
                "valid_to_offset": 60,
                "max_uses": 40,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل بین‌المللی کوثر",
        "city": "اصفهان",
        "address": "اصفهان، بلوار ملت، روبه‌روی سی‌وسه‌پل",
        "description": "هتل پنج ستاره در جوار زاینده‌رود و سی‌وسه‌پل با امکانات رفاهی ممتاز.",
        "star_rating": 5,
        "latitude": 32.637100,
        "longitude": 51.666900,
        "image_url": "/hotels/kowsar-isfahan.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته رو به زاینده‌رود",
                "description": "نمای تماشایی زاینده‌رود و پل تاریخی با بالکن اختصاصی.",
                "capacity": 2,
                "price_per_night": 4400000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Air Conditioning"],
            },
            {
                "title": "اتاق خانوادگی چهارنفره",
                "description": "دو تخت دونفره و فضای جادار برای سفرهای خانوادگی.",
                "capacity": 4,
                "price_per_night": 6200000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "KOWSAR10",
                "percent": 10,
                "valid_from_offset": -30,
                "valid_to_offset": 90,
                "max_uses": 60,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل سنتی قصر منشی",
        "city": "اصفهان",
        "address": "اصفهان، خیابان نشاط، کوچه قصر منشی",
        "description": "کاخ قاجاری بازسازی‌شده و ثبت آثار ملی با فضایی تاریخی، حوض‌خانه و سفره‌خانه سنتی.",
        "star_rating": 4,
        "latitude": 32.654000,
        "longitude": 51.685000,
        "image_url": "/hotels/ghasre-monshi.jpg",
        "room_types": [
            {
                "title": "اتاق شاه‌نشین دو تخته",
                "description": "شیشه‌های رنگی قجری، گچ‌بری اصیل و حس شکوه تاریخی دوران قاجار.",
                "capacity": 2,
                "price_per_night": 3800000,
                "quantity": 6,
                "amenities": ["WiFi", "Breakfast", "Room Service", "Air Conditioning"],
            },
            {
                "title": "اتاق حوض‌خانه سه تخته",
                "description": "دسترسی مستقیم به حیاط سنتی و صدای دلنشین فواره آب.",
                "capacity": 3,
                "price_per_night": 4900000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "MONSHI15",
                "percent": 15,
                "valid_from_offset": -10,
                "valid_to_offset": 90,
                "max_uses": 30,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل مجلل درویشی",
        "city": "مشهد",
        "address": "مشهد، خیابان امام رضا (ع)، بین امام رضا ۲۴ و ۲۶",
        "description": "بلندترین هتل آتریوم شرق کشور با معماری باشکوه، رستوران‌های ملل و امکانات VIP.",
        "star_rating": 5,
        "latitude": 36.277800,
        "longitude": 59.619200,
        "image_url": "/hotels/darvishi.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته امپریال",
                "description": "دکوراسیون سلطنتی مدرن با جکوزی اختصاصی و دسترسی نزدیک به حرم مطهر.",
                "capacity": 2,
                "price_per_night": 5600000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت دوبلکس پرزیدنت",
                "description": "سوئیت دو طبقه لوکس با چشم‌انداز بارگاه منور رضوی و خدمات تشریفات.",
                "capacity": 4,
                "price_per_night": 11000000,
                "quantity": 2,
                "amenities": ["WiFi", "Breakfast", "Pool", "Parking", "Gym", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "MASHHAD20",
                "percent": 20,
                "valid_from_offset": -20,
                "valid_to_offset": 120,
                "max_uses": 50,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل بین‌المللی پارس مشهد",
        "city": "مشهد",
        "address": "مشهد، بلوار وکیل‌آباد، تقاطع بلوار شهید صیاد شیرازی",
        "description": "هتل پنج ستاره در منطقه خوش آب‌وهوای غرب مشهد با محوطه سرسبز وسیع و سالن‌های همایش.",
        "star_rating": 5,
        "latitude": 36.331200,
        "longitude": 59.497500,
        "image_url": "/hotels/pars-mashhad.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته لوکس باغ",
                "description": "منظره دریاچه و فضای سبز هتل با امکانات کامل رفاهی.",
                "capacity": 2,
                "price_per_night": 4100000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Parking", "Air Conditioning"],
            },
            {
                "title": "سوئیت رویال سه نفره",
                "description": "محیطی دلباز با اتاق نشیمن مستقل و پارکینگ اختصاصی.",
                "capacity": 3,
                "price_per_night": 6200000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "PARS15",
                "percent": 15,
                "valid_from_offset": -10,
                "valid_to_offset": 80,
                "max_uses": 35,
            },
        ],
    },
    {
        "owner_username": "manager1",
        "name": "هتل صخره‌ای لاله کندوان",
        "city": "تبریز",
        "address": "آذربایجان شرقی، اسکو، روستای تاریخی کندوان",
        "description": "سومین هتل صخره‌ای جهان در دل کوهستان سهند با اتاق‌های تراشیده‌شده در سنگ طبیعی.",
        "star_rating": 5,
        "latitude": 37.794400,
        "longitude": 46.244700,
        "image_url": "/hotels/laleh-kandovan.jpg",
        "room_types": [
            {
                "title": "اتاق صخره‌ای دوتخته با جکوزی",
                "description": "تجربه اقامت غارنشینی مدرن با آب لوله‌کشی معدنی و جکوزی طبیعی صخره‌ای.",
                "capacity": 2,
                "price_per_night": 4800000,
                "quantity": 6,
                "amenities": ["WiFi", "Breakfast", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت امپریال کران",
                "description": "بزرگ‌ترین سوئیت صخره‌ای مجموعه با چشم‌انداز دره و رودخانه کندوان.",
                "capacity": 4,
                "price_per_night": 7900000,
                "quantity": 2,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "KANDOVAN20",
                "percent": 20,
                "valid_from_offset": -30,
                "valid_to_offset": 100,
                "max_uses": 30,
            },
        ],
    },

    # Manager 2 hotels (Shiraz, Yazd, Kish, Ramsar)
    {
        "owner_username": "manager2",
        "name": "هتل بزرگ چمران",
        "city": "شیراز",
        "address": "شیراز، بلوار شهید چمران",
        "description": "مرتفع‌ترین هتل شیراز واقع در منطقه خوش آب‌وهوای قصرالدشت با چشم‌انداز ۳۶۰ درجه.",
        "star_rating": 5,
        "latitude": 29.663100,
        "longitude": 52.488300,
        "image_url": "/hotels/chamran-shiraz.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته دلوکس قصرالدشت",
                "description": "نمایی خیره‌کننده از باغات سرسبز قصرالدشت در طبقات فوقانی هتل.",
                "capacity": 2,
                "price_per_night": 3900000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Room Service", "Air Conditioning"],
            },
            {
                "title": "اتاق یک‌تخته کینگ",
                "description": "تخت سایز کینگ مناسب اقامت‌های راحت و آسوده.",
                "capacity": 1,
                "price_per_night": 2400000,
                "quantity": 6,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
            {
                "title": "سوئیت رویال",
                "description": "مبلمان ایتالیایی، میز کار مجهز و سرویس چای و قهوه رایگان.",
                "capacity": 3,
                "price_per_night": 6800000,
                "quantity": 3,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "SHIRAZ20",
                "percent": 20,
                "valid_from_offset": -20,
                "valid_to_offset": 100,
                "max_uses": 50,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل هما شیراز",
        "city": "شیراز",
        "address": "شیراز، خیابان مشکین‌فام، جنب بوستان آزادی",
        "description": "هتل پنج ستاره بین‌المللی در جوار پارک آزادی با باغ ایرانی باطراوت و دسترسی عالی.",
        "star_rating": 5,
        "latitude": 29.629500,
        "longitude": 52.540100,
        "image_url": "/hotels/homa-shiraz.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته رو به بوستان",
                "description": "هوای مطبوع و منظره سرسبز پارک آزادی با آرامش کم‌نظیر.",
                "capacity": 2,
                "price_per_night": 4200000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت یک‌خوابه هما",
                "description": "سالن نشیمن مجزا، مبلمان راحتی و چشم‌انداز تپه‌های شمالی شیراز.",
                "capacity": 3,
                "price_per_night": 6900000,
                "quantity": 3,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "HOMA15",
                "percent": 15,
                "valid_from_offset": -10,
                "valid_to_offset": 90,
                "max_uses": 35,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل الیزه شیراز",
        "city": "شیراز",
        "address": "شیراز، معالی‌آباد، کوی پزشکان، پلاک ۲۰",
        "description": "هتل بوتیک آرام و مدرن در منطقه معالی‌آباد شیراز با خدمات شخصی‌سازی‌شده و کادر حرفه‌ای.",
        "star_rating": 4,
        "latitude": 29.682000,
        "longitude": 52.469000,
        "image_url": "/hotels/elysee-shiraz.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته کامفورت",
                "description": "طراحی مدرن و ارگونومیک همراه با منوی بالشت و عایق صوتی پیشرفته.",
                "capacity": 2,
                "price_per_night": 3300000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Pool", "Air Conditioning"],
            },
            {
                "title": "سوئیت کینگ الیزه",
                "description": "اقامتی شیک و بی‌دغدغه برای سفرهای کاری و خانوادگی.",
                "capacity": 3,
                "price_per_night": 5100000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Parking", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "ELYSEE10",
                "percent": 10,
                "valid_from_offset": -20,
                "valid_to_offset": 75,
                "max_uses": 40,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل داد یزد",
        "city": "یزد",
        "address": "یزد، خیابان دهم فروردین، پلاک ۲۱۴",
        "description": "یادگاری تاریخی از سال ۱۳۰۷ خورشیدی با معماری اصیل کویری و بادگیرهای مشهور.",
        "star_rating": 4,
        "latitude": 31.884500,
        "longitude": 54.372100,
        "image_url": "/hotels/dad-yazd.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به حیاط مرکزی",
                "description": "حوض فیروزه‌ای و کاهگل خنک در مرکز شهر بادگیرها.",
                "capacity": 2,
                "price_per_night": 3100000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Air Conditioning"],
            },
            {
                "title": "اتاق سه‌تخته خانوادگی داد",
                "description": "فضای دلباز سنتی برای سفر خاطره‌انگیز کویری خانواده‌ها.",
                "capacity": 3,
                "price_per_night": 4300000,
                "quantity": 5,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "YAZD10",
                "percent": 10,
                "valid_from_offset": -40,
                "valid_to_offset": 120,
                "max_uses": 45,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل پارسیان صفائیه یزد",
        "city": "یزد",
        "address": "یزد، صفائیه، میدان اطلسی، خیابان تیمسار فلاحی",
        "description": "تلفیقی هنرمندانه از معماری سنتی و هتل‌داری مدرن در منطقه‌ای خوش آب‌وهوا از شهر جهانی یزد.",
        "star_rating": 5,
        "latitude": 31.848000,
        "longitude": 54.361000,
        "image_url": "/hotels/safaiyeh-yazd.jpg",
        "room_types": [
            {
                "title": "اتاق دوتخته هتل جدید صفائیه",
                "description": "تجهیزات مدرن پنج ستاره با چشم‌انداز باغ و معماری خشت و آجر.",
                "capacity": 2,
                "price_per_night": 3700000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
            {
                "title": "اتاق سنتی فاز باغ",
                "description": "اقامتی نوستالژیک در خانه‌های باغی با ایوان اختصاصی.",
                "capacity": 3,
                "price_per_night": 5200000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "SAFA15",
                "percent": 15,
                "valid_from_offset": -15,
                "valid_to_offset": 90,
                "max_uses": 35,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل باغ مشیرالممالک",
        "city": "یزد",
        "address": "یزد، خیابان انقلاب، بلوار مشیرالممالک",
        "description": "نخستین هتل باغ ایرانی با ثبت در فهرست آثار ملی، نهر جاری، فواره‌ها و درختان کهنسال.",
        "star_rating": 4,
        "latitude": 31.905000,
        "longitude": 54.341000,
        "image_url": "/hotels/moshir-yazd.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به باغ",
                "description": "پنجره‌های مشبک چوبی رو به جویبار و طراوت باغ کویری.",
                "capacity": 2,
                "price_per_night": 3200000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
            {
                "title": "اتاق سه تخته سنتی",
                "description": "طاق و تویزه‌های اصیل ایرانی با آرامش عمیق کویری.",
                "capacity": 3,
                "price_per_night": 4600000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "MOSHIR10",
                "percent": 10,
                "valid_from_offset": -20,
                "valid_to_offset": 80,
                "max_uses": 30,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل دریایی ترنج کیش",
        "city": "کیش",
        "address": "جزیره کیش، جاده جهان، بعد از میدان جاسک",
        "description": "نخستین هتل روی آب خاورمیانه با طراحی بته‌جقه بر روی آب‌های نیلگون خلیج فارس و کف شیشه‌ای اتاق‌ها.",
        "star_rating": 5,
        "latitude": 26.541200,
        "longitude": 53.948100,
        "image_url": "/hotels/toranj-kish.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به غروب خلیج فارس",
                "description": "کف شیشه‌ای برای تماشای ماهیان دریایی و بالکن اختصاصی با منظره غروب رویایی.",
                "capacity": 2,
                "price_per_night": 6800000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Gym", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت رویال امپریال دریایی",
                "description": "سوئیت وسیع روی آب با امکانات فوق‌لوکس و تشریفات اختصاصی فرودگاهی.",
                "capacity": 4,
                "price_per_night": 13500000,
                "quantity": 3,
                "amenities": ["WiFi", "Breakfast", "Gym", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "TORANJ20",
                "percent": 20,
                "valid_from_offset": -20,
                "valid_to_offset": 90,
                "max_uses": 40,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل بزرگ داریوش کیش",
        "city": "کیش",
        "address": "جزیره کیش، میدان داریوش",
        "description": "هتل مجلل پنج ستاره الهام‌گرفته از تخت جمشید و تاریخ باستان با نمایی خیره‌کننده از ساحل مرجان.",
        "star_rating": 5,
        "latitude": 26.533000,
        "longitude": 54.025000,
        "image_url": "/hotels/dariush-kish.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به دریا",
                "description": "چشم‌انداز بیکران آب‌های زلال خلیج فارس و ستون‌های باشکوه هخامنشی.",
                "capacity": 2,
                "price_per_night": 5900000,
                "quantity": 10,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Room Service", "Air Conditioning"],
            },
            {
                "title": "سوئیت آتوسا رو به باغ",
                "description": "سوئیت لوکس با طراحی هخامنشی و دسترسی مستقیم به محوطه نخلستان.",
                "capacity": 3,
                "price_per_night": 8800000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Pool", "Gym", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "DARIUSH15",
                "percent": 15,
                "valid_from_offset": -15,
                "valid_to_offset": 90,
                "max_uses": 50,
            },
        ],
    },
    {
        "owner_username": "manager2",
        "name": "هتل قدیم و جدید رامسر",
        "city": "رامسر",
        "address": "مازندران، رامسر، انتهای بلوار معلم (کازینو سابق)",
        "description": "نگین تاریخی شمال ایران در دامنه جنگل‌های البرز و مشرف به دریای خزر با آبگرم‌های معدنی.",
        "star_rating": 4,
        "latitude": 36.908000,
        "longitude": 50.665000,
        "image_url": "/hotels/ramsar-hotel.jpg",
        "room_types": [
            {
                "title": "اتاق دو تخته رو به جنگل و کوه",
                "description": "هوای پاکیزه جنگل‌های هیرکانی با بالکن مشرف به چشم‌انداز سبز مازندران.",
                "capacity": 2,
                "price_per_night": 3400000,
                "quantity": 8,
                "amenities": ["WiFi", "Breakfast", "Parking", "Air Conditioning"],
            },
            {
                "title": "سوئیت چهار نفره هتل جدید",
                "description": "فضای دلباز مناسب خانواده‌ها با دسترسی آسان به استخر و چشمه‌های آبگرم معدنی.",
                "capacity": 4,
                "price_per_night": 5800000,
                "quantity": 4,
                "amenities": ["WiFi", "Breakfast", "Pool", "Parking", "Room Service", "Air Conditioning"],
            },
        ],
        "discounts": [
            {
                "code": "RAMSAR15",
                "percent": 15,
                "valid_from_offset": -20,
                "valid_to_offset": 80,
                "max_uses": 35,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Populate database with idempotent demo data for course defense (users, hotels, discounts, bookings)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo records and seed fresh data.",
        )

    def handle(self, *args, **options):
        reset = options.get("reset", False)

        with transaction.atomic():
            if reset:
                self.stdout.write(self.style.WARNING("Reset requested: cleaning up demo records..."))
                self._cleanup_demo_data()

            self.stdout.write("Seeding demo data...")
            users_map = self._seed_users()
            amenities_map = self._seed_amenities()
            hotels_map, room_types_list, discounts_map = self._seed_hotels_and_rooms(users_map, amenities_map)
            bookings_count = self._seed_bookings(users_map, room_types_list, discounts_map)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded demo data: "
                f"{len(DEMO_MANAGERS)} managers, {len(DEMO_GUESTS)} guests, "
                f"{len(hotels_map)} hotels across {len(set(h['city'] for h in DEMO_HOTELS))} cities, "
                f"{len(room_types_list)} room types, {bookings_count} bookings."
            )
        )

    def _cleanup_demo_data(self):
        """Wipe records created by demo usernames and hotel names."""
        all_demo_usernames = [u["username"] for u in DEMO_MANAGERS + DEMO_GUESTS]
        hotel_names = [h["name"] for h in DEMO_HOTELS]

        # Bookings made by demo guests or for demo hotels
        Booking.objects.filter(guest__username__in=all_demo_usernames).delete()
        Booking.objects.filter(room_type__hotel__name__in=hotel_names).delete()

        # Discount codes for demo hotels
        DiscountCode.objects.filter(hotel__name__in=hotel_names).delete()

        # Room types for demo hotels
        RoomType.objects.filter(hotel__name__in=hotel_names).delete()

        # Demo hotels
        Hotel.objects.filter(name__in=hotel_names).delete()

        # Demo users
        User.objects.filter(username__in=all_demo_usernames).delete()

        self.stdout.write("  Existing demo records removed.")

    def _seed_users(self):
        """Seed managers and guests idempotently."""
        users_map = {}
        for data in DEMO_MANAGERS + DEMO_GUESTS:
            user = User.objects.filter(username=data["username"]).first()
            if not user:
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data["phone"],
                    role=data["role"],
                    email_verified=True,
                )
            else:
                # Update role and verified status if pre-existing
                user.role = data["role"]
                user.email_verified = True
                user.set_password(data["password"])
                user.save()
            users_map[data["username"]] = user
        return users_map

    def _seed_amenities(self):
        """Seed core amenities idempotently."""
        amenities_map = {}
        for data in DEMO_AMENITIES:
            amenity, _ = Amenity.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]},
            )
            amenities_map[data["name"]] = amenity
        return amenities_map

    def _seed_hotels_and_rooms(self, users_map, amenities_map):
        """Seed hotels, room types, and discount codes idempotently."""
        today = date.today()
        hotels_map = {}
        room_types_list = []
        discounts_map = {}

        for h_data in DEMO_HOTELS:
            owner = users_map[h_data["owner_username"]]
            hotel, created = Hotel.objects.get_or_create(
                name=h_data["name"],
                defaults={
                    "owner": owner,
                    "city": h_data["city"],
                    "address": h_data["address"],
                    "description": h_data["description"],
                    "star_rating": h_data["star_rating"],
                    "latitude": h_data["latitude"],
                    "longitude": h_data["longitude"],
                    "image_url": h_data["image_url"],
                    "is_active": True,
                },
            )
            hotels_map[hotel.name] = hotel

            # Room types
            for rt_data in h_data["room_types"]:
                rt, rt_created = RoomType.objects.get_or_create(
                    hotel=hotel,
                    title=rt_data["title"],
                    defaults={
                        "description": rt_data["description"],
                        "capacity": rt_data["capacity"],
                        "price_per_night": rt_data["price_per_night"],
                        "quantity": rt_data["quantity"],
                    },
                )
                if rt_created or not rt.amenities.exists():
                    rt_amenities = [amenities_map[a_name] for a_name in rt_data["amenities"] if a_name in amenities_map]
                    rt.amenities.set(rt_amenities)
                room_types_list.append(rt)

            # Discount codes
            for d_data in h_data.get("discounts", []):
                valid_from = today + timedelta(days=d_data["valid_from_offset"])
                valid_to = today + timedelta(days=d_data["valid_to_offset"])
                code_str = d_data["code"].upper()
                discount, _ = DiscountCode.objects.get_or_create(
                    hotel=hotel,
                    code=code_str,
                    defaults={
                        "percent": d_data["percent"],
                        "valid_from": valid_from,
                        "valid_to": valid_to,
                        "max_uses": d_data.get("max_uses", 50),
                        "used_count": 0,
                        "is_active": True,
                    },
                )
                discounts_map[(hotel.id, code_str)] = discount

        return hotels_map, room_types_list, discounts_map

    def _seed_bookings(self, users_map, room_types_list, discounts_map):
        """Seed ~20 bookings across past, current, future, and cancelled states."""
        today = date.today()
        now = timezone.now()
        guests = [users_map[f"guest{i}"] for i in range(1, 6)]

        # Specific booking scenarios ensuring distinct check-in/out dates and states
        booking_plans = [
            # Past bookings (completed)
            {"guest_idx": 0, "rt_idx": 0, "in_off": -25, "out_off": -22, "rooms": 1, "guests": 1, "status": Booking.Status.CONFIRMED, "discount_code": "ESPINAS20"},
            {"guest_idx": 1, "rt_idx": 1, "in_off": -20, "out_off": -18, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": None},
            {"guest_idx": 2, "rt_idx": 3, "in_off": -18, "out_off": -14, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "AZADI15"},
            {"guest_idx": 3, "rt_idx": 5, "in_off": -15, "out_off": -12, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "ISFAHAN25"},
            {"guest_idx": 4, "rt_idx": 8, "in_off": -14, "out_off": -10, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "KOWSAR10"},
            {"guest_idx": 0, "rt_idx": 10, "in_off": -10, "out_off": -7, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "SHIRAZ20"},
            {"guest_idx": 1, "rt_idx": 13, "in_off": -8, "out_off": -5, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "ZAND15"},

            # Current bookings (currently staying)
            {"guest_idx": 2, "rt_idx": 1, "in_off": -2, "out_off": 2, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "ESPINAS20"},
            {"guest_idx": 3, "rt_idx": 4, "in_off": -1, "out_off": 3, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": None},
            {"guest_idx": 4, "rt_idx": 6, "in_off": -3, "out_off": 1, "rooms": 1, "guests": 1, "status": Booking.Status.CONFIRMED, "discount_code": None},
            {"guest_idx": 0, "rt_idx": 11, "in_off": -2, "out_off": 3, "rooms": 1, "guests": 1, "status": Booking.Status.CONFIRMED, "discount_code": "SHIRAZ20"},
            {"guest_idx": 1, "rt_idx": 15, "in_off": -1, "out_off": 4, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "YAZD10"},

            # Future bookings (confirmed upcoming)
            {"guest_idx": 2, "rt_idx": 2, "in_off": 5, "out_off": 8, "rooms": 1, "guests": 3, "status": Booking.Status.CONFIRMED, "discount_code": "VIP10"},
            {"guest_idx": 3, "rt_idx": 7, "in_off": 7, "out_off": 11, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "ISFAHAN25"},
            {"guest_idx": 4, "rt_idx": 9, "in_off": 10, "out_off": 14, "rooms": 1, "guests": 3, "status": Booking.Status.CONFIRMED, "discount_code": None},
            {"guest_idx": 0, "rt_idx": 12, "in_off": 14, "out_off": 17, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "SHIRAZ20"},
            {"guest_idx": 1, "rt_idx": 14, "in_off": 15, "out_off": 18, "rooms": 1, "guests": 2, "status": Booking.Status.CONFIRMED, "discount_code": "ZAND15"},

            # Cancelled bookings
            {"guest_idx": 2, "rt_idx": 0, "in_off": 3, "out_off": 6, "rooms": 1, "guests": 1, "status": Booking.Status.CANCELLED, "discount_code": "ESPINAS20"},
            {"guest_idx": 3, "rt_idx": 3, "in_off": -5, "out_off": -2, "rooms": 1, "guests": 2, "status": Booking.Status.CANCELLED, "discount_code": None},
            {"guest_idx": 4, "rt_idx": 5, "in_off": 12, "out_off": 15, "rooms": 1, "guests": 2, "status": Booking.Status.CANCELLED, "discount_code": "ISFAHAN25"},
            {"guest_idx": 0, "rt_idx": 16, "in_off": 20, "out_off": 24, "rooms": 1, "guests": 2, "status": Booking.Status.CANCELLED, "discount_code": "YAZD10"},
        ]

        created_count = 0
        for plan in booking_plans:
            guest = guests[plan["guest_idx"] % len(guests)]
            room_type = room_types_list[plan["rt_idx"] % len(room_types_list)]
            check_in = today + timedelta(days=plan["in_off"])
            check_out = today + timedelta(days=plan["out_off"])
            nights = (check_out - check_in).days

            # Check if booking already exists (idempotency)
            existing = Booking.objects.filter(
                guest=guest,
                room_type=room_type,
                check_in=check_in,
                check_out=check_out,
            ).first()

            if existing:
                continue

            subtotal = nights * plan["rooms"] * room_type.price_per_night

            discount_obj = None
            discount_amount = 0
            if plan["discount_code"]:
                discount_key = (room_type.hotel_id, plan["discount_code"].upper())
                discount_obj = discounts_map.get(discount_key)
                if discount_obj:
                    discount_amount = int(subtotal * discount_obj.percent / 100)
                    if plan["status"] == Booking.Status.CONFIRMED:
                        discount_obj.used_count += 1
                        discount_obj.save(update_fields=["used_count"])

            total_price = max(0, subtotal - discount_amount)
            cancelled_at = now - timedelta(days=1) if plan["status"] == Booking.Status.CANCELLED else None

            Booking.objects.create(
                guest=guest,
                room_type=room_type,
                check_in=check_in,
                check_out=check_out,
                rooms_count=plan["rooms"],
                guests_count=plan["guests"],
                nights=nights,
                price_per_night_snapshot=room_type.price_per_night,
                subtotal=subtotal,
                discount_code=discount_obj,
                discount_amount=discount_amount,
                total_price=total_price,
                status=plan["status"],
                cancelled_at=cancelled_at,
            )
            created_count += 1

        total_demo_bookings = Booking.objects.filter(
            guest__username__in=[u["username"] for u in DEMO_GUESTS]
        ).count()
        return total_demo_bookings
