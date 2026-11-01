import { Link } from 'react-router-dom'

export default function LoginPage() {
  return (
    <div className="max-w-md mx-auto py-12">
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xs">
        <h1 className="text-2xl font-bold text-gray-900 text-center">ورود به حساب کاربری</h1>
        <p className="text-sm text-gray-500 text-center mt-2">
          برای دسترسی به پنل و مشاهده رزروها وارد شوید
        </p>

        <form onSubmit={(e) => e.preventDefault()} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نام کاربری یا ایمیل
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
              کلمه عبور
            </label>
            <input
              type="password"
              disabled
              placeholder="••••••••"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            />
          </div>

          <button
            type="button"
            disabled
            className="w-full py-2.5 px-4 rounded-lg bg-blue-300 text-white font-medium text-sm cursor-not-allowed"
          >
            ورود (در حال توسعه)
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          حساب کاربری ندارید؟{' '}
          <Link to="/register" className="text-blue-600 hover:text-blue-800 font-medium">
            ثبت‌نام کنید
          </Link>
        </p>
      </div>
    </div>
  )
}
