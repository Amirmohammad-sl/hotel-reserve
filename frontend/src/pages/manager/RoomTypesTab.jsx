import { useState, useEffect } from 'react'
import {
  getManagerRoomTypesApi,
  deleteManagerRoomTypeApi,
} from '../../api/manager'
import RoomTypeModal from './RoomTypeModal'

export default function RoomTypesTab({
  hotels,
  selectedHotelId,
  onHotelChange,
}) {
  const [roomTypes, setRoomTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [reloadTrigger, setReloadTrigger] = useState(0)

  const [modalOpen, setModalOpen] = useState(false)
  const [editingRoomType, setEditingRoomType] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    if (!selectedHotelId) {
      return
    }

    let isMounted = true

    async function loadRoomTypes() {
      try {
        const data = await getManagerRoomTypesApi(selectedHotelId)
        if (isMounted) {
          setRoomTypes(Array.isArray(data) ? data : [])
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'خطا در بارگذاری لیست انواع اتاق.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadRoomTypes()

    return () => {
      isMounted = false
    }
  }, [selectedHotelId, reloadTrigger])

  function handleRefetch() {
    setLoading(true)
    setError(null)
    setReloadTrigger((prev) => prev + 1)
  }

  function handleOpenCreate() {
    setEditingRoomType(null)
    setModalOpen(true)
  }

  function handleOpenEdit(rt) {
    setEditingRoomType(rt)
    setModalOpen(true)
  }

  async function handleDelete(rt) {
    const confirmed = window.confirm(
      `آیا از حذف نوع اتاق «${rt.title}» اطمینان دارید؟`
    )
    if (!confirmed) return

    setDeletingId(rt.id)
    try {
      await deleteManagerRoomTypeApi(rt.id)
      setRoomTypes((prev) => prev.filter((item) => item.id !== rt.id))
    } catch (err) {
      alert(err.message || 'خطا در حذف نوع اتاق.')
    } finally {
      setDeletingId(null)
    }
  }

  function handleSaved(savedRt) {
    setRoomTypes((prev) => {
      const exists = prev.some((item) => item.id === savedRt.id)
      if (exists) {
        return prev.map((item) => (item.id === savedRt.id ? savedRt : item))
      }
      return [...prev, savedRt]
    })
  }

  if (hotels.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
        <div className="text-4xl mb-3">🏨</div>
        <h3 className="text-lg font-semibold text-gray-800">ابتدا یک هتل ثبت کنید</h3>
        <p className="text-sm text-gray-500 mt-1">
          برای تعریف نوع اتاق، باید حداقل یک هتل در سیستم ثبت شده باشد.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">مدیریت انواع اتاق‌ها</h2>
          <p className="text-sm text-gray-500 mt-1">
            تعریف ظرفیت، قیمت هر شب، تعداد و امکانات اتاق‌ها
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-gray-600 whitespace-nowrap">
              انتخاب هتل:
            </label>
            <select
              value={selectedHotelId || ''}
              onChange={(e) => onHotelChange(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-xl bg-white text-sm font-medium text-gray-800 outline-none focus:ring-2 focus:ring-blue-500"
            >
              {hotels.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.name} ({h.city})
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={handleOpenCreate}
            disabled={!selectedHotelId}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm text-sm font-medium disabled:opacity-50 transition"
          >
            <span>➕</span>
            <span>افزودن نوع اتاق</span>
          </button>
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
          <p className="mt-3 text-sm text-gray-500">در حال بارگذاری انواع اتاق...</p>
        </div>
      )}

      {error && !loading && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center justify-between">
          <span>{error}</span>
          <button
            type="button"
            onClick={handleRefetch}
            className="text-sm underline font-medium hover:text-red-900"
          >
            تلاش مجدد
          </button>
        </div>
      )}

      {!loading && !error && roomTypes.length === 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
          <div className="text-4xl mb-3">🚪</div>
          <h3 className="text-lg font-semibold text-gray-800">
            هنوز نوع اتاقی برای این هتل تعریف نشده است
          </h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto mt-2">
            با کلیک روی دکمه «افزودن نوع اتاق»، اتاق‌های هتل خود (مانند یک‌تخته، دوتخته، سوئیت و ...) را ثبت کنید.
          </p>
          <button
            type="button"
            onClick={handleOpenCreate}
            className="mt-5 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition"
          >
            <span>➕</span>
            <span>تعریف اولین نوع اتاق</span>
          </button>
        </div>
      )}

      {!loading && !error && roomTypes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {roomTypes.map((rt) => (
            <div
              key={rt.id}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 flex flex-col justify-between hover:shadow-md transition"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <h3 className="font-bold text-gray-900 text-base">{rt.title}</h3>
                  <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg">
                    {rt.quantity} واحد
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3 bg-gray-50 p-2.5 rounded-xl">
                  <div>
                    <span className="text-gray-400">ظرفیت: </span>
                    <span className="font-medium text-gray-800">{rt.capacity} نفر</span>
                  </div>
                  <div>
                    <span className="text-gray-400">قیمت هر شب: </span>
                    <span className="font-bold text-gray-900">
                      {Number(rt.price_per_night).toLocaleString('fa-IR')} تومان
                    </span>
                  </div>
                </div>

                {rt.description && (
                  <p className="text-xs text-gray-500 line-clamp-2 mb-3">
                    {rt.description}
                  </p>
                )}

                {Array.isArray(rt.amenities) && rt.amenities.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {rt.amenities.map((am) => (
                      <span
                        key={typeof am === 'object' ? am.id : am}
                        className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100"
                      >
                        {typeof am === 'object' ? am.name : `امکان #${am}`}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-gray-100 mt-2">
                <button
                  type="button"
                  onClick={() => handleOpenEdit(rt)}
                  className="px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition"
                >
                  ویرایش
                </button>
                <button
                  type="button"
                  disabled={deletingId === rt.id}
                  onClick={() => handleDelete(rt)}
                  className="px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded-lg font-medium disabled:opacity-50 transition"
                >
                  {deletingId === rt.id ? 'در حال حذف...' : 'حذف'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <RoomTypeModal
          key={editingRoomType ? `edit-${editingRoomType.id}` : 'create'}
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          hotelId={selectedHotelId}
          roomType={editingRoomType}
          onSaved={handleSaved}
        />
      )}
    </div>
  )
}


