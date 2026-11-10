import { useEffect, useState, useRef } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { verifyEmailApi, resendVerificationApi } from '../api/auth'
import { useAuth } from '../context/AuthContext'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const { user, isAuthenticated, isManager, refreshUser } = useAuth()

  const [status, setStatus] = useState(() => (token ? 'loading' : 'error'))
  const [errorMessage, setErrorMessage] = useState(() =>
    token
      ? ''
      : 'توکن تایید در آدرس یافت نشد. لطفاً از لینکی که به ایمیل شما ارسال شده استفاده کنید.'
  )
  const [resendStatus, setResendStatus] = useState({ loading: false, message: '', error: '' })

  const attemptedRef = useRef(false)

  useEffect(() => {
    if (!token || attemptedRef.current) return
    attemptedRef.current = true

    async function performVerification() {
      try {
        await verifyEmailApi({ token })
        setStatus('success')
        if (isAuthenticated) {
          try {
            await refreshUser()
          } catch {
            // Ignore refresh error if session expired
          }
        }
      } catch (err) {
        setStatus('error')
        setErrorMessage(
          err?.message ||
            'لینک تایید نامعتبر است یا منقضی شده است (مدت اعتبار لینک ۴۸ ساعت می‌باشد).'
        )
      }
    }

    performVerification()
  }, [token, isAuthenticated, refreshUser])

  const handleResend = async () => {
    setResendStatus({ loading: true, message: '', error: '' })
    try {
      const res = await resendVerificationApi()
      setResendStatus({
        loading: false,
        message: res?.message || 'لینک تایید جدید به ایمیل شما ارسال شد.',
        error: '',
      })
    } catch (err) {
      setResendStatus({
        loading: false,
        message: '',
        error: err?.message || 'خطا در ارسال مجدد ایمیل تایید.',
      })
    }
  }

  return (
    <div className="max-w-md mx-auto my-12 bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
      {status === 'loading' && (
        <div className="py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">در حال تایید آدرس ایمیل...</h2>
          <p className="text-gray-500 text-sm">لطفاً چند لحظه صبر کنید.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="py-4">
          <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">ایمیل با موفقیت تایید شد!</h2>
          <p className="text-gray-600 text-sm mb-6 leading-relaxed">
            حساب کاربری شما اکنون فعال است. شما می‌توانید با خیال آسوده به رزرو اقامتگاه یا مدیریت هتل‌ها بپردازید.
          </p>

          <div className="flex flex-col gap-2">
            {isAuthenticated ? (
              isManager ? (
                <Link
                  to="/manager"
                  className="w-full inline-flex justify-center items-center px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
                >
                  ورود به پنل مدیریت
                </Link>
              ) : (
                <Link
                  to="/hotels"
                  className="w-full inline-flex justify-center items-center px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
                >
                  مشاهده و رزرو هتل‌ها
                </Link>
              )
            ) : (
              <Link
                to="/login"
                className="w-full inline-flex justify-center items-center px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
              >
                ورود به حساب کاربری
              </Link>
            )}
            <Link
              to="/"
              className="w-full inline-flex justify-center items-center px-4 py-2 text-gray-600 hover:text-gray-900 text-sm font-medium transition"
            >
              بازگشت به صفحه اصلی
            </Link>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="py-4">
          <div className="w-14 h-14 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">تایید ایمیل ناموفق بود</h2>
          <p className="text-rose-600 text-sm mb-6 leading-relaxed bg-rose-50 p-3 rounded-lg border border-rose-100">
            {errorMessage}
          </p>

          {isAuthenticated && !user?.email_verified && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg text-right">
              <p className="text-xs text-gray-600 mb-3">
                می‌توانید درخواست ارسال یک لینک تایید جدید بدهید:
              </p>
              {resendStatus.message && (
                <p className="text-xs text-emerald-600 font-medium mb-2">{resendStatus.message}</p>
              )}
              {resendStatus.error && (
                <p className="text-xs text-rose-600 font-medium mb-2">{resendStatus.error}</p>
              )}
              <button
                type="button"
                onClick={handleResend}
                disabled={resendStatus.loading}
                className="w-full inline-flex justify-center items-center px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-medium rounded transition disabled:opacity-50"
              >
                {resendStatus.loading ? 'در حال ارسال...' : 'ارسال مجدد ایمیل تایید'}
              </button>
            </div>
          )}

          <div className="flex flex-col gap-2">
            {!isAuthenticated && (
              <Link
                to="/login"
                className="w-full inline-flex justify-center items-center px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
              >
                ورود به حساب کاربری
              </Link>
            )}
            <Link
              to="/"
              className="w-full inline-flex justify-center items-center px-4 py-2 text-gray-600 hover:text-gray-900 text-sm font-medium transition"
            >
              بازگشت به صفحه اصلی
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
