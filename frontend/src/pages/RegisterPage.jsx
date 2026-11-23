import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ApiError } from '../api/client'

export default function RegisterPage() {
  const { register, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    role: 'guest',
    phone: '',
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
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
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

    const errors = {}
    if (!formData.username.trim()) {
      errors.username = ['لطفاً نام کاربری را وارد کنید.']
    }
    if (!formData.email.trim()) {
      errors.email = ['لطفاً آدرس ایمیل را وارد کنید.']
    }
    if (!formData.password) {
      errors.password = ['لطفاً کلمه عبور را وارد کنید.']
    }
    if (!formData.password2) {
      errors.password2 = ['لطفاً تکرار کلمه عبور را وارد کنید.']
    } else if (formData.password !== formData.password2) {
      errors.password2 = ['تکرار کلمه عبور با کلمه عبور اصلی مطابقت ندارد.']
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }

    setSubmitting(true)
    try {
      const registeredUser = await register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        password2: formData.password2,
        role: formData.role,
        phone: formData.phone.trim() || undefined,
      })

      const target = location.state?.from?.pathname || (registeredUser?.role === 'manager' ? '/manager' : '/')
      navigate(target, { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.errors && Object.keys(err.errors).length > 0) {
        setFieldErrors(err.errors)
        if (err.errors.__all__) {
          setGeneralError(err.errors.__all__.join(' '))
        }
      } else {
        setGeneralError(err.message || 'خطا در ثبت‌نام حساب کاربری.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-md mx-auto py-12 px-4 sm:px-0">
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xs">
        <h1 className="text-2xl font-bold text-gray-900 text-center">ایجاد حساب کاربری</h1>
        <p className="text-sm text-gray-500 text-center mt-2">
          ثبت‌نام به عنوان مهمان یا مدیر هتل
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
              htmlFor="username"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              نام کاربری <span className="text-red-500">*</span>
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              disabled={submitting}
              value={formData.username}
              onChange={handleChange}
              placeholder="مثال: ali_reza"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.username
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.username && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.username.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              ایمیل <span className="text-red-500">*</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              disabled={submitting}
              value={formData.email}
              onChange={handleChange}
              placeholder="user@example.com"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.email
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.email && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.email.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="role"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              نوع حساب کاربری <span className="text-red-500">*</span>
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              disabled={submitting}
              className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:border-blue-600 focus:outline-hidden"
            >
              <option value="guest">مهمان (رزرو اتاق و مشاهده هتل‌ها)</option>
              <option value="manager">مدیر هتل (مدیریت هتل، اتاق‌ها و تخفیف‌ها)</option>
            </select>
            {fieldErrors.role && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.role.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="phone"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              شماره تلفن همراه <span className="text-xs text-gray-400">(اختیاری)</span>
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              disabled={submitting}
              value={formData.phone}
              onChange={handleChange}
              placeholder="۰۹۱۲۳۴۵۶۷۸۹"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.phone
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.phone && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.phone.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              کلمه عبور <span className="text-red-500">*</span>
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              disabled={submitting}
              value={formData.password}
              onChange={handleChange}
              placeholder="حداقل ۸ کاراکتر"
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

          <div>
            <label
              htmlFor="password2"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              تکرار کلمه عبور <span className="text-red-500">*</span>
            </label>
            <input
              id="password2"
              name="password2"
              type="password"
              autoComplete="new-password"
              required
              disabled={submitting}
              value={formData.password2}
              onChange={handleChange}
              placeholder="••••••••"
              className={`w-full px-3.5 py-2.5 border rounded-lg text-sm transition-colors focus:outline-hidden ${
                fieldErrors.password2
                  ? 'border-red-500 focus:border-red-600 bg-red-50/20'
                  : 'border-gray-300 focus:border-blue-600'
              }`}
            />
            {fieldErrors.password2 && (
              <p className="text-xs text-red-600 mt-1 font-medium">
                {fieldErrors.password2.join(' ')}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-xs"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>در حال ایجاد حساب...</span>
              </>
            ) : (
              <span>ثبت‌نام در سامانه</span>
            )}
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
