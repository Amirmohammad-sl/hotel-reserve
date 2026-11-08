import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { resendVerificationApi } from '../api/auth'

export default function VerificationBanner() {
  const { user, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  if (!isAuthenticated || !user || user.email_verified) {
    return null
  }

  const handleResend = async () => {
    setLoading(true)
    setMessage('')
    setError('')
    try {
      const response = await resendVerificationApi()
      setMessage(response?.message || 'لینک فعال‌سازی جدید به ایمیل شما ارسال شد.')
    } catch (err) {
      setError(err?.message || 'خطا در ارسال مجدد ایمیل تایید. لطفاً دوباره تلاش کنید.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      role="alert"
      className="bg-amber-50 border-b border-amber-200 px-4 py-3 text-amber-900 transition-all duration-200"
    >
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-sm">
        <div className="flex items-center gap-2">
          <svg
            className="w-5 h-5 text-amber-600 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div>
            <span className="font-semibold">حساب کاربری شما تایید نشده است.</span>{' '}
            <span className="text-amber-800">
              برای رزرو هتل یا مدیریت اقامتگاه‌ها، لطفاً ایمیل خود را با لینکی که ارسال شده تایید کنید.
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          {message && <span className="text-emerald-700 text-xs font-medium">{message}</span>}
          {error && <span className="text-rose-700 text-xs font-medium">{error}</span>}
          <button
            type="button"
            onClick={handleResend}
            disabled={loading}
            className="inline-flex items-center justify-center px-3 py-1.5 text-xs font-medium text-amber-900 bg-amber-200 hover:bg-amber-300 disabled:opacity-50 rounded-md transition-colors"
          >
            {loading ? 'در حال ارسال...' : 'ارسال مجدد ایمیل تایید'}
          </button>
        </div>
      </div>
    </div>
  )
}
