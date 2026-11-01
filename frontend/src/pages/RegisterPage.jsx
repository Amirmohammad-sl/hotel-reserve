import { Link } from 'react-router-dom'

export default function RegisterPage() {
  return (
    <div className="max-w-md mx-auto py-12">
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xs">
        <h1 className="text-2xl font-bold text-gray-900 text-center">ایجاد حساب کاربری</h1>
        <p className="text-sm text-gray-500 text-center mt-2">
          ثبت‌نام به عنوان مهمان یا مدیر هتل
        </p>

        <form onSubmit={(e) => e.preventDefault()} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نام کاربری
            </label>
            <input
              type="text"
              disabled
              placeholder="در فاز ۲ پیاده‌سازی خواهد شد"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ایمیل
            </label>
            <input
              type="email"
              disabled
              placeholder="user@example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            />
          </div>

          <button
            type="button"
            disabled
            className="w-full py-2.5 px-4 rounded-lg bg-blue-300 text-white font-medium text-sm cursor-not-allowed"
          >
            ثبت‌نام (در حال توسعه)
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          قبلاً ثبت‌نام کرده‌اید؟{' '}
          <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
            وارد شوید
          </Link>
        </p>
      </div>
    </div>
  )
}
