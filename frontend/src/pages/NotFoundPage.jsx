import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="max-w-xl mx-auto py-16 px-4 text-center">
      <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-blue-50 text-blue-600 mb-6 shadow-inner">
        <span className="text-5xl select-none" aria-hidden="true">
          🗺️
        </span>
      </div>
      <div className="inline-block px-3 py-1 rounded-full bg-red-100 text-red-700 text-xs font-bold mb-3">
        خطای ۴۰۴
      </div>
      <h1 className="text-2xl sm:text-3xl font-black text-gray-900 mb-3">
        صفحه مورد نظر یافت نشد
      </h1>
      <p className="text-sm text-gray-600 leading-relaxed mb-8 max-w-md mx-auto">
        آدرسی که وارد کرده‌اید وجود ندارد، تغییر نام داده یا موقتاً در دسترس نیست. برای ادامه می‌توانید از پیوندهای زیر استفاده نمایید.
      </p>
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
        <Link
          to="/"
          className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          بازگشت به صفحه اصلی
        </Link>
        <Link
          to="/hotels"
          className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-white hover:bg-gray-100 text-gray-700 border border-gray-300 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          جستجو و رزرو هتل‌ها
        </Link>
      </div>
    </div>
  )
}
