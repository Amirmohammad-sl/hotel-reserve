import { useState, useEffect } from 'react'
import {
  createManagerRoomTypeApi,
  updateManagerRoomTypeApi,
  getAmenitiesApi,
} from '../../api/manager'
import { ApiError } from '../../api/client'

export default function RoomTypeModal({
  isOpen,
  onClose,
  hotelId,
  roomType,
  onSaved,
}) {
  const isEditing = Boolean(roomType)

  const [formData, setFormData] = useState(() => ({
    title: roomType?.title || '',
    description: roomType?.description || '',
    capacity: roomType?.capacity ?? 2,
    price_per_night: roomType?.price_per_night ?? 1000000,
    quantity: roomType?.quantity ?? 1,
    amenities: Array.isArray(roomType?.amenities)
      ? roomType.amenities.map((a) => (typeof a === 'object' ? a.id : a))
      : [],
  }))

  const [allAmenities, setAllAmenities] = useState([])
  const [loadingAmenities, setLoadingAmenities] = useState(true)
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let isMounted = true

    async function loadAmenities() {
      try {
        const data = await getAmenitiesApi()
        if (isMounted) {
          setAllAmenities(Array.isArray(data) ? data : [])
        }
      } catch {
        // Fallback silently if amenities fail to fetch
      } finally {
        if (isMounted) {
          setLoadingAmenities(false)
        }
      }
    }

    loadAmenities()

    return () => {
      isMounted = false
    }
  }, [])

  if (!isOpen) return null

  function handleChange(e) {
    const { name, value, type } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }))
    }
  }

  function handleAmenityToggle(amenityId) {
    setFormData((prev) => {
      const exists = prev.amenities.includes(amenityId)
      const newAmenities = exists
        ? prev.amenities.filter((id) => id !== amenityId)
        : [...prev.amenities, amenityId]
      return { ...prev, amenities: newAmenities }
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setErrors({})
    setGeneralError(null)

    const payload = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      capacity: Number(formData.capacity),
      price_per_night: Number(formData.price_per_night),
      quantity: Number(formData.quantity),
      amenities: formData.amenities,
    }

    try {
      let saved
      if (isEditing) {
        saved = await updateManagerRoomTypeApi(roomType.id, payload)
      } else {
        saved = await createManagerRoomTypeApi(hotelId, payload)
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
        setGeneralError('خطایی در ذخیره اطلاعات نوع اتاق رخ داد.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="room-type-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 text-right">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
          <h2 id="room-type-modal-title" className="text-xl font-bold text-gray-900">
            {isEditing ? 'ویرایش نوع اتاق' : 'افزودن نوع اتاق جدید'}
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
              عنوان نوع اتاق <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="مثال: اتاق دابل استاندارد یا سوئیت رویال"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.title && (
              <p className="text-xs text-red-600 mt-1">{errors.title.join(' ')}</p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ظرفیت (نفر) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="capacity"
                min="1"
                value={formData.capacity}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              {errors.capacity && (
                <p className="text-xs text-red-600 mt-1">{errors.capacity.join(' ')}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تعداد فیزیکی <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="quantity"
                min="1"
                value={formData.quantity}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              {errors.quantity && (
                <p className="text-xs text-red-600 mt-1">{errors.quantity.join(' ')}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                قیمت هر شب (تومان) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="price_per_night"
                min="0"
                step="10000"
                value={formData.price_per_night}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              {errors.price_per_night && (
                <p className="text-xs text-red-600 mt-1">
                  {errors.price_per_night.join(' ')}
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              توضیحات اتاق
            </label>
            <textarea
              name="description"
              rows={2}
              value={formData.description}
              onChange={handleChange}
              placeholder="توضیحاتی در مورد تخت‌ها، ویو، متراژ و شرایط..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
            {errors.description && (
              <p className="text-xs text-red-600 mt-1">
                {errors.description.join(' ')}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              امکانات اتاق (Amenities)
            </label>
            {loadingAmenities ? (
              <p className="text-xs text-gray-400">در حال بارگذاری امکانات...</p>
            ) : allAmenities.length === 0 ? (
              <p className="text-xs text-gray-400">امکاناتی در سیستم تعریف نشده است.</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 border border-gray-200 rounded-lg p-3 max-h-36 overflow-y-auto">
                {allAmenities.map((amenity) => {
                  const checked = formData.amenities.includes(amenity.id)
                  return (
                    <label
                      key={amenity.id}
                      className={`flex items-center gap-2 p-1.5 rounded cursor-pointer text-xs transition ${
                        checked ? 'bg-blue-50 text-blue-800' : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => handleAmenityToggle(amenity.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="truncate">{amenity.name}</span>
                    </label>
                  )
                })}
              </div>
            )}
            {errors.amenities && (
              <p className="text-xs text-red-600 mt-1">{errors.amenities.join(' ')}</p>
            )}
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
              {submitting ? 'در حال ثبت...' : isEditing ? 'ذخیره تغییرات' : 'ثبت نوع اتاق'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


