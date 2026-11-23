import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ApiError } from '../api/client'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [formData, setFormData] = useState({
    username_or_email: '',
    password: '',
    remember_me: false,
  })
  const [fieldErrors, setFieldErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Redirect if already logged in
  if (user) {
    const destination = location.state?.from?.pathname || (user.role === 'manager' ? '/manager' : '/')
    navigate(destination, { replace: true })
    return null
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
    // Clear error on this field once user types
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: undefined }))
    }
    if (generalError) {
      setGeneralError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFieldErrors({})
    setGeneralError('')

    // Client-side quick checks
    const errors = {}
    if (!formData.username_or_email.trim()) {
      errors.username_or_email = ['لطفاً نام کاربری یا ایمیل خود را وارد کنید.']
    }
    if (!formData.password) {
      errors.password = ['لطفاً کلمه عبور را وارد کنید.']
    }
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }

    setSubmitting(true)
    try {
      const loggedInUser = await login({
        username_or_email: formData.username_or_email.trim(),
        password: formData.password,
        remember_me: formData.remember_me,
      })

      const target = location.state?.from?.pathname || (loggedInUser.role === 'manager' ? '/manager' : '/')
      navigate(target, { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.errors && Object.keys(err.errors).length > 0) {
        setFieldErrors(err.errors)
        if (err.errors.__all__) {
          setGeneralError(err.errors.__all__.join(' '))
        }
      } else {
        setGeneralError(err.message || 'خطا در ورود به حساب کاربری.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-md mx-auto py-12 px-4 sm:px-0">
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xs">
        <h1 className="text-2xl font-bold text-gray-900 text-center">ورود به حساب کاربری</h1>
        <p className="text-sm text-gray-500 text-center mt-2">
          برای دسترسی به پنل و مشاهده رزروها وارد شوید
        </p>

        {generalError && (
          <div className="mt-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm flex items-start gap-2">
            <span className="text-base">⚠️</span>
            <span>{generalError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <div>
            <label
              htmlFor="username_or_email"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              نام کاربری یا ایمیل
            </label>
            <input
              id="username_or_email"
              name="username_or_email"
              type="text"
              autoComplete="username"
              required
              disabled={submitting}
              value={formData.username_or_email}
              onChange={handleChange}
              placeholder="مثال: ali یا ali@example.com"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.username_or_email
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.username_or_email && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.username_or_email.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              کلمه عبور
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              disabled={submitting}
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.password
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.password && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.password.join(' ')}
              </p>
            )}
          </div>

          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-600">
              <input
                type="checkbox"
                name="remember_me"
                checked={formData.remember_me}
                onChange={handleChange}
                disabled={submitting}
                className="w-4 h-4 rounded text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span>مرا به خاطر بسپار</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-xs"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>در حال ورود...</span>
              </>
            ) : (
              <span>ورود به حساب</span>
            )}
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
