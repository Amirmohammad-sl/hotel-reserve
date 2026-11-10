import { useState, useEffect } from 'react'
import {
  getManagerDiscountsApi,
  deleteManagerDiscountApi,
} from '../../api/manager'
import DiscountModal from './DiscountModal'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import EmptyState from '../../components/common/EmptyState'

export default function DiscountsTab({
  hotels,
  selectedHotelId,
  onHotelChange,
}) {
  const [discounts, setDiscounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [reloadTrigger, setReloadTrigger] = useState(0)

  const [modalOpen, setModalOpen] = useState(false)
  const [editingDiscount, setEditingDiscount] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    if (!selectedHotelId) {
      return
    }

    let isMounted = true

    async function loadDiscounts() {
      try {
        const data = await getManagerDiscountsApi(selectedHotelId)
        if (isMounted) {
          setDiscounts(Array.isArray(data) ? data : [])
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'خطا در دریافت لیست کدهای تخفیف.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadDiscounts()

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
    setEditingDiscount(null)
    setModalOpen(true)
  }

  function handleOpenEdit(dc) {
    setEditingDiscount(dc)
    setModalOpen(true)
  }

  async function handleDelete(dc) {
    const confirmed = window.confirm(
      `آیا از حذف کد تخفیف «${dc.code}» اطمینان دارید؟`
    )
    if (!confirmed) return

    setDeletingId(dc.id)
    try {
      await deleteManagerDiscountApi(dc.id)
      setDiscounts((prev) => prev.filter((item) => item.id !== dc.id))
    } catch (err) {
      alert(err.message || 'خطا در حذف کد تخفیف.')
    } finally {
      setDeletingId(null)
    }
  }

  function handleSaved(savedDc) {
    setDiscounts((prev) => {
      const exists = prev.some((item) => item.id === savedDc.id)
      if (exists) {
        return prev.map((item) => (item.id === savedDc.id ? savedDc : item))
      }
      return [savedDc, ...prev]
    })
  }

  if (hotels.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
        <div className="text-4xl mb-3">🏨</div>
        <h3 className="text-lg font-semibold text-gray-800">ابتدا یک هتل ثبت کنید</h3>
        <p className="text-sm text-gray-500 mt-1">
          برای تعریف کدهای تخفیف، باید حداقل یک هتل در سیستم ثبت شده باشد.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">کدهای تخفیف هتل</h2>
          <p className="text-sm text-gray-500 mt-1">
            تعریف و مدیریت بن‌های تخفیف درصدی و بازه اعتبار زمانی
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
            <span>افزودن کد تخفیف</span>
          </button>
        </div>
      </div>

      {loading && (
        <LoadingSpinner message="در حال دریافت کدهای تخفیف..." />
      )}

      {error && !loading && (
        <ErrorMessage message={error} onRetry={handleRefetch} />
      )}

      {!loading && !error && discounts.length === 0 && (
        <EmptyState
          icon="🏷️"
          title="هنوز کد تخفیفی برای این هتل تعریف نشده است"
          description="می‌توانید کدهای تخفیف جذاب با درصد مشخص و سقف تعداد استفاده برای تشویق مهمانان به رزرو ایجاد کنید."
          action={
            <button
              type="button"
              onClick={handleOpenCreate}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span>➕</span>
              <span>ایجاد اولین کد تخفیف</span>
            </button>
          }
        />
      )}

      {!loading && !error && discounts.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-right text-xs">
              <thead className="bg-gray-50 text-gray-600 border-b border-gray-200">
                <tr>
                  <th className="p-3.5 font-semibold">کد تخفیف</th>
                  <th className="p-3.5 font-semibold text-center">درصد تخفیف</th>
                  <th className="p-3.5 font-semibold">بازه اعتبار</th>
                  <th className="p-3.5 font-semibold text-center">میزان استفاده</th>
                  <th className="p-3.5 font-semibold text-center">وضعیت</th>
                  <th className="p-3.5 font-semibold text-left">عملیات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {discounts.map((dc) => (
                  <tr key={dc.id} className="hover:bg-gray-50/75 transition">
                    <td className="p-3.5 font-mono font-bold text-gray-900 tracking-wider">
                      {dc.code}
                    </td>
                    <td className="p-3.5 text-center">
                      <span className="inline-block px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold text-xs border border-emerald-100">
                        {dc.percent}٪
                      </span>
                    </td>
                    <td className="p-3.5 text-gray-600">
                      {dc.valid_from ? dc.valid_from.slice(0, 10) : '–'} تا{' '}
                      {dc.valid_to ? dc.valid_to.slice(0, 10) : '–'}
                    </td>
                    <td className="p-3.5 text-center font-medium">
                      <span className="text-gray-900">{dc.used_count || 0}</span>
                      <span className="text-gray-400"> / </span>
                      <span className="text-gray-600">
                        {dc.max_uses ? dc.max_uses : 'نامحدود'}
                      </span>
                    </td>
                    <td className="p-3.5 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                          dc.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {dc.is_active ? 'فعال' : 'غیرفعال'}
                      </span>
                    </td>
                    <td className="p-3.5 text-left">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => handleOpenEdit(dc)}
                          className="px-2.5 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded font-medium transition"
                        >
                          ویرایش
                        </button>
                        <button
                          type="button"
                          disabled={deletingId === dc.id}
                          onClick={() => handleDelete(dc)}
                          className="px-2.5 py-1 text-xs text-red-600 hover:bg-red-50 rounded font-medium disabled:opacity-50 transition"
                        >
                          {deletingId === dc.id ? '...' : 'حذف'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modalOpen && (
        <DiscountModal
          key={editingDiscount ? `edit-${editingDiscount.id}` : 'create'}
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          hotelId={selectedHotelId}
          discount={editingDiscount}
          onSaved={handleSaved}
        />
      )}
    </div>
  )
}


