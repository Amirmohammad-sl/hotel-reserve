import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import SearchForm from '../components/SearchForm'
import HealthBadge from '../components/HealthBadge'
import { getRecentHotelsApi } from '../api/hotels'

export default function HomePage() {
  const [recentHotels, setRecentHotels] = useState([])

  useEffect(() => {
    let isMounted = true
    async function loadRecentHotels() {
      try {
        const data = await getRecentHotelsApi()
        if (isMounted && Array.isArray(data)) {
          setRecentHotels(data)
        }
      } catch {
        // Ignore errors silently for recent hotels section
      }
    }
    loadRecentHotels()
    return () => {
      isMounted = false
    }
  }, [])

  return (
    <div className="space-y-12">
      {/* Hero section with embedded search */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-linear-to-b from-blue-50 to-white rounded-3xl border border-blue-100 shadow-xs">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-3xl sm:text-5xl font-black text-gray-900 tracking-tight">
            رزرو آسان و سریع <span className="text-blue-600">هتل‌های سراسر ایران</span>
          </h1>
          <p className="mt-4 text-base sm:text-lg text-gray-600">
            تجربه اقامتی دلنشین با بهترین قیمت، تنوع بالای اتاق‌ها و تخفیف‌های ویژه برای مهمانان گرامی.
          </p>
        </div>

        {/* Prominent Search Bar */}
        <div className="mt-8 max-w-4xl mx-auto">
          <SearchForm />
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link
            to="/hotels"
            className="px-6 py-2.5 rounded-xl bg-white text-gray-700 font-medium border border-gray-300 hover:bg-gray-50 shadow-xs transition-colors text-sm"
          >
            مشاهده تمام هتل‌ها
          </Link>
          <Link
            to="/manager"
            className="px-6 py-2.5 rounded-xl bg-white text-gray-700 font-medium border border-gray-300 hover:bg-gray-50 shadow-xs transition-colors text-sm"
          >
            ورود به پنل هتل‌داران
          </Link>
        </div>

        {/* Health Check Badge */}
        <div className="mt-10 pt-8 border-t border-blue-100/70 flex justify-center">
          <HealthBadge />
        </div>
      </section>

      {/* Recently Viewed Hotels Block */}
      {recentHotels.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between border-b border-gray-200 pb-3">
            <div>
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <span>🕒</span> هتل‌های اخیراً مشاهده‌شده
              </h2>
              <p className="text-xs sm:text-sm text-gray-500 mt-1">
                دسترسی سریع به هتل‌هایی که اخیراً بررسی کرده‌اید
              </p>
            </div>
            <span className="text-xs bg-blue-50 text-blue-700 font-medium px-2.5 py-1 rounded-full border border-blue-200">
              {recentHotels.length} هتل اخیر
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {recentHotels.map((hotel) => (
              <Link
                key={hotel.id}
                to={`/hotels/${hotel.id}`}
                className="group block bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-md hover:border-blue-300 transition-all"
              >
                <div className="h-40 bg-gray-100 overflow-hidden relative">
                  {hotel.image_url ? (
                    <img
                      src={hotel.image_url}
                      alt={hotel.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 bg-gray-50">
                      <span className="text-3xl">🏨</span>
                    </div>
                  )}
                  <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-xs px-2 py-0.5 rounded-lg text-xs font-semibold text-gray-800 shadow-xs">
                    ★ {hotel.star_rating} ستاره
                  </div>
                </div>
                <div className="p-4 space-y-2">
                  <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                    {hotel.name}
                  </h3>
                  <p className="text-xs text-gray-500 flex items-center gap-1">
                    <span>📍</span> {hotel.city}
                  </p>
                  {hotel.min_price && (
                    <p className="text-xs text-gray-700 pt-1 border-t border-gray-100 flex items-baseline justify-between">
                      <span className="text-gray-500">شروع قیمت از:</span>
                      <span className="font-bold text-blue-600 text-sm">
                        {Number(hotel.min_price).toLocaleString('fa-IR')}{' '}
                        <span className="text-[10px] text-gray-500 font-normal">تومان</span>
                      </span>
                    </p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Feature cards teaser */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-xs">
          <div className="text-3xl mb-3">🔍</div>
          <h2 className="text-lg font-bold text-gray-900">جستجوی هوشمند</h2>
          <p className="mt-2 text-sm text-gray-600">
            فیلتر بر اساس شهر، تاریخ اقامت، تعداد نفرات و محدوده قیمت برای یافتن بهترین گزینه.
          </p>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-xs">
          <div className="text-3xl mb-3">🏷️</div>
          <h2 className="text-lg font-bold text-gray-900">کدهای تخفیف</h2>
          <p className="mt-2 text-sm text-gray-600">
            امکان اعمال کدهای تخفیف تعریف‌شده توسط هتل‌داران روی صورت‌حساب رزرو.
          </p>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-xs">
          <div className="text-3xl mb-3">🏨</div>
          <h2 className="text-lg font-bold text-gray-900">پنل اختصاصی هتل‌داران</h2>
          <p className="mt-2 text-sm text-gray-600">
            مدیریت هتل، انواع اتاق، ظرفیت‌ها و مشاهده تاریخچه رزروها به صورت یکپارچه.
          </p>
        </div>
      </section>
    </div>
  )
}
