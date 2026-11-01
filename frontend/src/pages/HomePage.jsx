import { Link } from 'react-router-dom'
import HealthBadge from '../components/HealthBadge'

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero section */}
      <section className="text-center py-12 px-4 sm:px-6 lg:px-8 bg-linear-to-b from-blue-50 to-white rounded-3xl border border-blue-100 shadow-xs">
        <h1 className="text-3xl sm:text-5xl font-black text-gray-900 tracking-tight">
          رزرو آسان و سریع <span className="text-blue-600">هتل‌های سراسر ایران</span>
        </h1>
        <p className="mt-4 text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
          تجربه اقامتی دلنشین با بهترین قیمت، تنوع بالای اتاق‌ها و تخفیف‌های ویژه برای مهمانان گرامی.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link
            to="/hotels"
            className="px-6 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 shadow-xs transition-colors"
          >
            مشاهده و جستجوی هتل‌ها
          </Link>
          <Link
            to="/manager"
            className="px-6 py-3 rounded-xl bg-white text-gray-700 font-medium border border-gray-300 hover:bg-gray-50 transition-colors"
          >
            ورود به پنل هتل‌داران
          </Link>
        </div>

        {/* Health Check Badge */}
        <div className="mt-10 pt-8 border-t border-blue-100/70 flex justify-center">
          <HealthBadge />
        </div>
      </section>

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
