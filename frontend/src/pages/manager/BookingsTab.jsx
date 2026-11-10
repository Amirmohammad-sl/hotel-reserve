import { useState, useEffect } from 'react'
import { getManagerBookingsApi } from '../../api/manager'

export default function BookingsTab({
  hotels,
  selectedHotelId,
  onHotelChange,
}) {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [reloadTrigger, setReloadTrigger] = useState(0)

  const [statusFilter, setStatusFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  useEffect(() => {
    if (!selectedHotelId) {
      return
    }

    let isMounted = true

    async function loadBookings() {
      try {
        const data = await getManagerBookingsApi(selectedHotelId, {
          status: statusFilter || undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
        })
        if (isMounted) {
          setBookings(Array.isArray(data) ? data : [])
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'خطا در بارگذاری لیست رزروها.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadBookings()

    return () => {
      isMounted = false
    }
  }, [selectedHotelId, statusFilter, dateFrom, dateTo, reloadTrigger])

  function handleFilterSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setReloadTrigger((prev) => prev + 1)
  }

  function handleClearFilters() {
    setStatusFilter('')
    setDateFrom('')
    setDateTo('')
    setLoading(true)
    setError(null)
    setReloadTrigger((prev) => prev + 1)
  }

  if (hotels.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
        <div className="text-4xl mb-3">🏨</div>
        <h3 className="text-lg font-semibold text-gray-800">ابتدا یک هتل ثبت کنید</h3>
        <p className="text-sm text-gray-500 mt-1">
          برای مشاهده رزروها، باید حداقل یک هتل در سیستم ثبت شده باشد.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">رزروهای هتل</h2>
          <p className="text-sm text-gray-500 mt-1">
            مشاهده و فیلتر کردن تمامی رزروهای ثبت‌شده توسط مهمانان
          </p>
        </div>

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
      </div>

      {/* Filter Bar */}
      <form
        onSubmit={handleFilterSubmit}
        className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex flex-wrap items-center gap-4"
      >
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-gray-600">وضعیت:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-xs outline-none bg-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">همه وضعیت‌ها</option>
            <option value="confirmed">تایید شده</option>
            <option value="cancelled">لغو شده</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-gray-600">از تاریخ:</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-gray-600">تا تاریخ:</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 mr-auto">
          {(statusFilter || dateFrom || dateTo) && (
            <button
              type="button"
              onClick={handleClearFilters}
              className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
            >
              پاک‌کردن فیلترها
            </button>
          )}
          <button
            type="submit"
            className="px-4 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition"
          >
            اعمال فیلتر
          </button>
        </div>
      </form>

      {loading && (
        <div className="py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
          <p className="mt-3 text-sm text-gray-500">در حال بارگذاری اطلاعات رزروها...</p>
        </div>
      )}

      {error && !loading && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center justify-between">
          <span>{error}</span>
          <button
            type="button"
            onClick={handleFilterSubmit}
            className="text-sm underline font-medium hover:text-red-900"
          >
            تلاش مجدد
          </button>
        </div>
      )}

      {!loading && !error && bookings.length === 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
          <div className="text-4xl mb-3">📋</div>
          <h3 className="text-lg font-semibold text-gray-800">
            رزروی برای این هتل یافت نشد
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {statusFilter || dateFrom || dateTo
              ? 'با فیلترهای مشخص‌شده هیچ نتیجه‌ای یافت نشد. می‌توانید فیلترها را تغییر دهید.'
              : 'هنوز هیچ رزروی برای این هتل توسط مهمانان ثبت نشده است.'}
          </p>
        </div>
      )}

      {!loading && !error && bookings.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-right text-xs">
              <thead className="bg-gray-50 text-gray-600 border-b border-gray-200">
                <tr>
                  <th className="p-3.5 font-semibold">شناسه</th>
                  <th className="p-3.5 font-semibold">مهمان</th>
                  <th className="p-3.5 font-semibold">نوع اتاق</th>
                  <th className="p-3.5 font-semibold">تاریخ اقامت</th>
                  <th className="p-3.5 font-semibold text-center">اتاق / نفر</th>
                  <th className="p-3.5 font-semibold">مبلغ کل</th>
                  <th className="p-3.5 font-semibold text-center">وضعیت</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-gray-50/75 transition">
                    <td className="p-3.5 font-mono text-gray-500 font-semibold">
                      #{b.id}
                    </td>
                    <td className="p-3.5">
                      <div className="font-semibold text-gray-900">
                        {b.guest?.first_name || b.guest?.last_name
                          ? `${b.guest.first_name} ${b.guest.last_name}`.trim()
                          : b.guest?.username || 'کاربر مهمان'}
                      </div>
                      <div className="text-[11px] text-gray-400" dir="ltr">
                        {b.guest?.email || '–'}
                      </div>
                    </td>
                    <td className="p-3.5 font-medium text-gray-900">
                      {b.room_type?.title || '–'}
                    </td>
                    <td className="p-3.5">
                      <div className="font-medium text-gray-800">
                        {b.check_in} تا {b.check_out}
                      </div>
                      <div className="text-[11px] text-gray-400">
                        {b.nights} شب اقامت
                      </div>
                    </td>
                    <td className="p-3.5 text-center">
                      <span className="font-medium text-gray-800">{b.rooms_count} اتاق</span>
                      <span className="text-gray-400"> / </span>
                      <span className="text-gray-600">{b.guests_count} نفر</span>
                    </td>
                    <td className="p-3.5">
                      <div className="font-bold text-gray-900">
                        {Number(b.total_price).toLocaleString('fa-IR')} تومان
                      </div>
                      {b.discount_amount > 0 && (
                        <div className="text-[11px] text-emerald-600">
                          تخفیف: {Number(b.discount_amount).toLocaleString('fa-IR')} (
                          {b.discount_code})
                        </div>
                      )}
                    </td>
                    <td className="p-3.5 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                          b.status === 'confirmed'
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                            : 'bg-rose-100 text-rose-800 border border-rose-200'
                        }`}
                      >
                        {b.status === 'confirmed' ? 'تایید شده' : 'لغو شده'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}


