import { useState } from 'react'
import {
  createManagerDiscountApi,
  updateManagerDiscountApi,
} from '../../api/manager'
import { ApiError } from '../../api/client'

function formatDate(d) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function DiscountModal({
  isOpen,
  onClose,
  hotelId,
  discount,
  onSaved,
}) {
  const isEditing = Boolean(discount)

  const [formData, setFormData] = useState(() => {
    const today = new Date()
    const nextMonth = new Date()
    nextMonth.setDate(today.getDate() + 30)

    return {
      code: discount?.code || '',
      percent: discount?.percent ?? 10,
      valid_from: discount?.valid_from
        ? discount.valid_from.slice(0, 10)
        : formatDate(today),
      valid_to: discount?.valid_to
        ? discount.valid_to.slice(0, 10)
        : formatDate(nextMonth),
      max_uses: discount?.max_uses ?? '',
      is_active: discount?.is_active ?? true,
    }
  })

  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (!isOpen) return null

  function handleChange(e) {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox'
          ? checked
          : name === 'code'
            ? value.toUpperCase().trim()
            : value,
    }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }))
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setErrors({})
    setGeneralError(null)

    const payload = {
      code: formData.code.trim().toUpperCase(),
      percent: Number(formData.percent),
      valid_from: formData.valid_from,
      valid_to: formData.valid_to,
      is_active: formData.is_active,
    }
    if (formData.max_uses !== '' && formData.max_uses !== null) {
      payload.max_uses = Number(formData.max_uses)
    }

    try {
      let saved
      if (isEditing) {
        saved = await updateManagerDiscountApi(discount.id, payload)
      } else {
        saved = await createManagerDiscountApi(hotelId, payload)
      }
      onSaved(saved)
      onClose()
    } catch (err) {
      if (err instanceof ApiError) {
        setGeneralError(err.message)
        if (err.errors) {
          setErrors(err.errors)
        }
      } else {
        setGeneralError('خطایی در ذخیره کد تخفیف رخ داد.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto p-6 text-right">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            {isEditing ? 'ویرایش کد تخفیف' : 'ایجاد کد تخفیف جدید'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {generalError && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm border border-red-200">
            {generalError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                کد تخفیف <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="code"
                value={formData.code}
                onChange={handleChange}
                placeholder="مثال: NOROOZ1403"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg uppercase tracking-wider font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                dir="ltr"
              />
              {errors.code && (
                <p className="text-xs text-red-600 mt-1">{errors.code.join(' ')}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                درصد تخفیف (%) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="percent"
                min="1"
                max="100"
                value={formData.percent}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              {errors.percent && (
                <p className="text-xs text-red-600 mt-1">{errors.percent.join(' ')}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تاریخ شروع اعتبار <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="valid_from"
                value={formData.valid_from}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.valid_from && (
                <p className="text-xs text-red-600 mt-1">{errors.valid_from.join(' ')}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تاریخ پایان اعتبار <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="valid_to"
                value={formData.valid_to}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.valid_to && (
                <p className="text-xs text-red-600 mt-1">{errors.valid_to.join(' ')}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              سقف تعداد استفاده (اختیاری)
            </label>
            <input
              type="number"
              name="max_uses"
              min="1"
              value={formData.max_uses}
              onChange={handleChange}
              placeholder="مثال: ۱۰۰ (خالی یعنی نامحدود)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.max_uses && (
              <p className="text-xs text-red-600 mt-1">{errors.max_uses.join(' ')}</p>
            )}
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="discount_is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <label
              htmlFor="discount_is_active"
              className="text-sm font-medium text-gray-700 cursor-pointer"
            >
              کد تخفیف فعال و قابل استفاده باشد
            </label>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm disabled:opacity-50 transition"
            >
              {submitting ? 'در حال ثبت...' : isEditing ? 'ذخیره تغییرات' : 'ثبت کد تخفیف'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


