import { useState } from 'react'
import { createManagerHotelApi, updateManagerHotelApi } from '../../api/manager'
import { ApiError } from '../../api/client'

export default function HotelModal({ isOpen, onClose, hotel, onSaved }) {
  const isEditing = Boolean(hotel)

  const [formData, setFormData] = useState(() => ({
    name: hotel?.name || '',
    city: hotel?.city || '',
    address: hotel?.address || '',
    description: hotel?.description || '',
    star_rating: hotel?.star_rating ?? 3,
    image_url: hotel?.image_url || '',
    is_active: hotel?.is_active ?? true,
  }))

  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (!isOpen) return null

  function handleChange(e) {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
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
      name: formData.name.trim(),
      city: formData.city.trim(),
      address: formData.address.trim(),
      description: formData.description.trim(),
      star_rating: Number(formData.star_rating),
      image_url: formData.image_url.trim(),
      is_active: formData.is_active,
    }

    try {
      let savedHotel
      if (isEditing) {
        savedHotel = await updateManagerHotelApi(hotel.id, payload)
      } else {
        savedHotel = await createManagerHotelApi(payload)
      }
      onSaved(savedHotel)
      onClose()
    } catch (err) {
      if (err instanceof ApiError) {
        setGeneralError(err.message)
        if (err.errors) {
          setErrors(err.errors)
        }
      } else {
        setGeneralError('خطایی در برقراری ارتباط رخ داد.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="hotel-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 text-right">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
          <h2 id="hotel-modal-title" className="text-xl font-bold text-gray-900">
            {isEditing ? 'ویرایش اطلاعات هتل' : 'ثبت هتل جدید'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="بستن"
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1"
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نام هتل <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="مثال: هتل اسپیناس پالاس"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.name && (
              <p className="text-xs text-red-600 mt-1">{errors.name.join(' ')}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                شهر <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                placeholder="مثال: تهران"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              {errors.city && (
                <p className="text-xs text-red-600 mt-1">{errors.city.join(' ')}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تعداد ستاره <span className="text-red-500">*</span>
              </label>
              <select
                name="star_rating"
                value={formData.star_rating}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white"
              >
                <option value={1}>۱ ستاره ⭐</option>
                <option value={2}>۲ ستاره ⭐⭐</option>
                <option value={3}>۳ ستاره ⭐⭐⭐</option>
                <option value={4}>۴ ستاره ⭐⭐⭐⭐</option>
                <option value={5}>۵ ستاره ⭐⭐⭐⭐⭐</option>
              </select>
              {errors.star_rating && (
                <p className="text-xs text-red-600 mt-1">{errors.star_rating.join(' ')}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              آدرس دقیق <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="مثال: سعادت‌آباد، میدان بهرود، خیابان ۳۳"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.address && (
              <p className="text-xs text-red-600 mt-1">{errors.address.join(' ')}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              توضیحات هتل
            </label>
            <textarea
              name="description"
              rows={3}
              value={formData.description}
              onChange={handleChange}
              placeholder="توضیحاتی درباره موقعیت، ویژگی‌ها و خدمات هتل..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.description && (
              <p className="text-xs text-red-600 mt-1">{errors.description.join(' ')}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              آدرس تصویر (URL)
            </label>
            <input
              type="url"
              name="image_url"
              value={formData.image_url}
              onChange={handleChange}
              placeholder="https://example.com/hotel.jpg"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              dir="ltr"
            />
            {errors.image_url && (
              <p className="text-xs text-red-600 mt-1">{errors.image_url.join(' ')}</p>
            )}
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="hotel_is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <label htmlFor="hotel_is_active" className="text-sm font-medium text-gray-700 cursor-pointer">
              هتل فعال و قابل مشاهده در جستجو باشد
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
              {submitting ? 'در حال ثبت...' : isEditing ? 'ذخیره تغییرات' : 'ثبت هتل'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


