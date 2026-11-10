import { useState, useEffect } from 'react'
import { getManagerHotelsApi, deleteManagerHotelApi } from '../../api/manager'
import HotelModal from './HotelModal'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import EmptyState from '../../components/common/EmptyState'

export default function HotelListTab({ onSelectHotelForTab, onHotelsChange }) {
  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reloadTrigger, setReloadTrigger] = useState(0)

  const [modalOpen, setModalOpen] = useState(false)
  const [selectedHotel, setSelectedHotel] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    let isMounted = true

    async function loadHotels() {
      try {
        const data = await getManagerHotelsApi()
        if (isMounted) {
          const list = Array.isArray(data) ? data : []
          setHotels(list)
          if (onHotelsChange) {
            onHotelsChange(list)
          }
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'خطا در بارگذاری لیست هتل‌ها.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadHotels()

    return () => {
      isMounted = false
    }
  }, [reloadTrigger, onHotelsChange])

  function handleRefetch() {
    setLoading(true)
    setError(null)
    setReloadTrigger((prev) => prev + 1)
  }

  function handleOpenCreate() {
    setSelectedHotel(null)
    setModalOpen(true)
  }

  function handleOpenEdit(hotel) {
    setSelectedHotel(hotel)
    setModalOpen(true)
  }

  async function handleDelete(hotel) {
    const confirmed = window.confirm(
      `آیا از حذف هتل «${hotel.name}» اطمینان دارید؟ تمام انواع اتاق‌ها، رزروها و کدهای تخفیف مربوط به آن حذف خواهند شد.`
    )
    if (!confirmed) return

    setDeletingId(hotel.id)
    try {
      await deleteManagerHotelApi(hotel.id)
      setHotels((prev) => {
        const updated = prev.filter((h) => h.id !== hotel.id)
        if (onHotelsChange) {
          onHotelsChange(updated)
        }
        return updated
      })
    } catch (err) {
      alert(err.message || 'خطا در حذف هتل.')
    } finally {
      setDeletingId(null)
    }
  }

  function handleSaved(savedHotel) {
    setHotels((prev) => {
      const exists = prev.some((h) => h.id === savedHotel.id)
      const updated = exists
        ? prev.map((h) => (h.id === savedHotel.id ? savedHotel : h))
        : [savedHotel, ...prev]
      if (onHotelsChange) {
        onHotelsChange(updated)
      }
      return updated
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">هتل‌های من</h2>
          <p className="text-sm text-gray-500 mt-1">
            مشاهده، ثبت و مدیریت هتل‌های تحت مدیریت شما
          </p>
        </div>
        <button
          type="button"
          onClick={handleOpenCreate}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm text-sm font-medium transition"
        >
          <span>➕</span>
          <span>افزودن هتل جدید</span>
        </button>
      </div>

      {loading && (
        <LoadingSpinner message="در حال دریافت لیست هتل‌ها..." />
      )}

      {error && !loading && (
        <ErrorMessage message={error} onRetry={handleRefetch} />
      )}

      {!loading && !error && hotels.length === 0 && (
        <EmptyState
          icon="🏨"
          title="هنوز هتلی ثبت نکرده‌اید"
          description="برای شروع پذیرش مهمان و تعریف اتاق‌ها، ابتدا با زدن دکمه زیر مشخصات اولین هتل خود را وارد نمایید."
          action={
            <button
              type="button"
              onClick={handleOpenCreate}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span>➕</span>
              <span>ثبت اولین هتل</span>
            </button>
          }
        />
      )}

      {!loading && !error && hotels.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {hotels.map((hotel) => (
            <div
              key={hotel.id}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition"
            >
              <div>
                {hotel.image_url ? (
                  <div className="h-44 w-full bg-gray-100 overflow-hidden">
                    <img
                      src={hotel.image_url}
                      alt={hotel.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  </div>
                ) : (
                  <div className="h-28 w-full bg-gradient-to-r from-blue-50 to-indigo-50 flex items-center justify-center text-4xl">
                    🏨
                  </div>
                )}

                <div className="p-5">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="font-bold text-gray-900 text-lg">{hotel.name}</h3>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        hotel.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {hotel.is_active ? 'فعال' : 'غیرفعال'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                    <span className="text-amber-500 font-bold">
                      {'⭐'.repeat(hotel.star_rating || 1)}
                    </span>
                    <span>•</span>
                    <span>{hotel.city}</span>
                  </div>

                  <p className="text-xs text-gray-600 line-clamp-2 mb-3">
                    {hotel.address}
                  </p>

                  {hotel.description && (
                    <p className="text-xs text-gray-400 line-clamp-2 mb-3">
                      {hotel.description}
                    </p>
                  )}
                </div>
              </div>

              <div className="p-5 pt-0 border-t border-gray-100 mt-2 space-y-3">
                <div className="grid grid-cols-2 gap-2 pt-3">
                  <button
                    type="button"
                    onClick={() => onSelectHotelForTab(hotel.id, 'rooms')}
                    className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg text-xs font-semibold transition text-center"
                  >
                    🚪 اتاق‌ها
                  </button>
                  <button
                    type="button"
                    onClick={() => onSelectHotelForTab(hotel.id, 'bookings')}
                    className="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded-lg text-xs font-semibold transition text-center"
                  >
                    📋 رزروها
                  </button>
                  <button
                    type="button"
                    onClick={() => onSelectHotelForTab(hotel.id, 'availability')}
                    className="px-3 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded-lg text-xs font-semibold transition text-center"
                  >
                    📊 تقویم ظرفیت
                  </button>
                  <button
                    type="button"
                    onClick={() => onSelectHotelForTab(hotel.id, 'discounts')}
                    className="px-3 py-1.5 bg-amber-50 text-amber-700 hover:bg-amber-100 rounded-lg text-xs font-semibold transition text-center"
                  >
                    🏷️ کدهای تخفیف
                  </button>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-50">
                  <button
                    type="button"
                    onClick={() => handleOpenEdit(hotel)}
                    className="px-3 py-1 text-xs text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded transition"
                  >
                    ویرایش هتل
                  </button>
                  <button
                    type="button"
                    disabled={deletingId === hotel.id}
                    onClick={() => handleDelete(hotel)}
                    className="px-3 py-1 text-xs text-red-600 hover:bg-red-50 rounded disabled:opacity-50 transition"
                  >
                    {deletingId === hotel.id ? 'در حال حذف...' : 'حذف هتل'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <HotelModal
          key={selectedHotel ? `edit-${selectedHotel.id}` : 'create'}
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          hotel={selectedHotel}
          onSaved={handleSaved}
        />
      )}
    </div>
  )
}


