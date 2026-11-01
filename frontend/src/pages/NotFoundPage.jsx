import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="text-center py-16">
      <h1 className="text-6xl font-black text-gray-300">۴۰۴</h1>
      <h2 className="mt-4 text-2xl font-bold text-gray-900">صفحه مورد نظر یافت نشد</h2>
      <p className="mt-2 text-sm text-gray-500">
        آدرسی که وارد کرده‌اید وجود ندارد یا منتقل شده است.
      </p>
      <div className="mt-6">
        <Link
          to="/"
          className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          بازگشت به صفحه اصلی
        </Link>
      </div>
    </div>
  )
}
