import { Link } from 'react-router-dom'

export default function ManagerPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">پنل مدیریت هتل‌ها</h1>
          <p className="text-sm text-gray-500 mt-1">
            تعریف هتل‌ها، نوع اتاق‌ها، تعیین ظرفیت و کدهای تخفیف
          </p>
        </div>
        <Link
          to="/"
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          بازگشت به خانه
        </Link>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center">
        <div className="text-4xl mb-3">📊</div>
        <h2 className="text-lg font-semibold text-gray-800">بخش مدیریت هتل‌ها و رزروها</h2>
        <p className="text-sm text-gray-500 max-w-md mx-auto mt-2">
          امکانات CRUD هتل‌ها، اتاق‌ها و مشاهده گزارش تقویم ظرفیت هتل در فاز ۲ پیاده‌سازی خواهد شد.
        </p>
      </div>
    </div>
  )
}
