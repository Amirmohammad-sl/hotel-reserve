import { Link, Navigate, useLocation, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function RequireRole({ role, allowedRoles, children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500 font-medium">در حال بررسی نشست کاربری...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  const expectedRoles = allowedRoles || (role ? [role] : [])
  const hasAccess = expectedRoles.length === 0 || expectedRoles.includes(user.role)

  if (!hasAccess) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-red-200 shadow-xs text-center">
        <div className="w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto text-3xl mb-4">
          ⛔
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">دسترسی غیرمجاز (۴۰۳)</h2>
        <p className="text-sm text-gray-600 mb-6 leading-relaxed">
          حساب کاربری شما دارای نقش <span className="font-semibold text-gray-800">{user.role === 'guest' ? 'مهمان' : user.role}</span> است و اجازه دسترسی به این بخش را ندارد. این قسمت مخصوص مدیران هتل می‌باشد.
        </p>
        <Link
          to="/"
          className="inline-block py-2.5 px-6 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors"
        >
          بازگشت به صفحه اصلی
        </Link>
      </div>
    )
  }

  return children ? children : <Outlet />
}
