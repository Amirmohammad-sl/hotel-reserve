import { useState, useEffect } from 'react'
import { getManagerAvailabilityApi } from '../../api/manager'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import EmptyState from '../../components/common/EmptyState'

function formatDate(d) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function AvailabilityTab({
  hotels,
  selectedHotelId,
  onHotelChange,
}) {
  const [dateFrom, setDateFrom] = useState(() => {
    const today = new Date()
    return formatDate(today)
  })
  const [dateTo, setDateTo] = useState(() => {
    const nextWeek = new Date()
    nextWeek.setDate(nextWeek.getDate() + 7)
    return formatDate(nextWeek)
  })

  const [availability, setAvailability] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [reloadTrigger, setReloadTrigger] = useState(0)

  useEffect(() => {
    if (!selectedHotelId) {
      return
    }
    if (!dateFrom || !dateTo) {
      return
    }
    if (dateTo <= dateFrom) {
      return
    }

    let isMounted = true

    async function loadAvailability() {
      try {
        const data = await getManagerAvailabilityApi(selectedHotelId, dateFrom, dateTo)
        if (isMounted) {
          setAvailability(Array.isArray(data) ? data : [])
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'خطا در بارگذاری تقویم ظرفیت هتل.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadAvailability()

    return () => {
      isMounted = false
    }
  }, [selectedHotelId, dateFrom, dateTo, reloadTrigger])

  function handleSubmit(e) {
    e.preventDefault()
    if (!dateFrom || !dateTo) {
      setError('لطفاً هر دو تاریخ شروع و پایان را انتخاب نمایید.')
      return
    }
    if (dateTo <= dateFrom) {
      setError('تاریخ پایان باید حتماً بعد از تاریخ شروع باشد.')
      return
    }
    setLoading(true)
    setError(null)
    setReloadTrigger((prev) => prev + 1)
  }

  function handleSetDays(days) {
    const start = new Date()
    const end = new Date()
    end.setDate(start.getDate() + days)
    setDateFrom(formatDate(start))
    setDateTo(formatDate(end))
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
          برای مشاهده تقویم ظرفیت، باید حداقل یک هتل در سیستم ثبت شده باشد.
        </p>
      </div>
    )
  }

  // Extract distinct dates from the first room type's daily_availability if exists
  const datesList =
    availability.length > 0 && availability[0].daily_availability
      ? availability[0].daily_availability.map((item) => item.date)
      : []

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">تقویم موجودی و ظرفیت روزانه</h2>
          <p className="text-sm text-gray-500 mt-1">
            بررسی تعداد کل اتاق‌ها، تعداد رزرو شده و ظرفیت آزاد به تفکیک روز
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

      {/* Date controls */}
      <form
        onSubmit={handleSubmit}
        className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex flex-wrap items-center gap-4 text-xs"
      >
        <div className="flex items-center gap-2">
          <label className="font-medium text-gray-700">از تاریخ:</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="font-medium text-gray-700">تا تاریخ:</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => handleSetDays(7)}
            className="px-2.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            ۷ روز آینده
          </button>
          <button
            type="button"
            onClick={() => handleSetDays(14)}
            className="px-2.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            ۱۴ روز آینده
          </button>
          <button
            type="button"
            onClick={() => handleSetDays(30)}
            className="px-2.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            ۳۰ روز آینده
          </button>
        </div>

        <div className="mr-auto">
          <button
            type="submit"
            className="px-4 py-1.5 font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition"
          >
            به‌روزرسانی جدول
          </button>
        </div>
      </form>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-600 px-1">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-emerald-100 border border-emerald-300 inline-block" />
          <span>ظرفیت آزاد و مناسب</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-amber-100 border border-amber-300 inline-block" />
          <span>ظرفیت محدود (≤ ۲ اتاق)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded bg-rose-100 border border-rose-300 inline-block" />
          <span>تکمیل ظرفیت (۰ آزاد)</span>
        </div>
      </div>

      {loading && (
        <LoadingSpinner message="در حال محاسبه و آماده‌سازی تقویم ظرفیت..." />
      )}

      {error && !loading && (
        <ErrorMessage message={error} onRetry={handleSubmit} />
      )}

      {!loading && !error && availability.length === 0 && (
        <EmptyState
          icon="📊"
          title="هیچ نوع اتاقی برای این هتل یافت نشد"
          description="برای مشاهده تقویم موجودی، ابتدا در تب «اتاق‌ها» نوع اتاق‌های هتل را تعریف نمایید."
        />
      )}

      {!loading && !error && availability.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-right text-xs">
              <thead className="bg-gray-50 text-gray-700 border-b border-gray-200">
                <tr>
                  <th className="p-3.5 font-bold min-w-[160px] sticky right-0 bg-gray-50 z-10 border-l border-gray-200">
                    نوع اتاق (کل موجودی)
                  </th>
                  {datesList.map((dt) => {
                    const d = new Date(`${dt}T12:00:00`)
                    const dayName = d.toLocaleDateString('fa-IR', { weekday: 'short' })
                    return (
                      <th
                        key={dt}
                        className="p-3 text-center min-w-[85px] border-l border-gray-100 last:border-l-0"
                      >
                        <div className="text-[10px] text-gray-400 font-normal">{dayName}</div>
                        <div className="font-semibold text-gray-800">{dt.slice(5)}</div>
                      </th>
                    )
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {availability.map((rt) => (
                  <tr key={rt.room_type_id} className="hover:bg-gray-50/50">
                    <td className="p-3.5 sticky right-0 bg-white font-semibold text-gray-900 border-l border-gray-200 z-10">
                      <div>{rt.room_type_title}</div>
                      <div className="text-[11px] text-gray-400 font-normal">
                        مجموع فیزیکی: {rt.total_quantity} اتاق
                      </div>
                    </td>
                    {rt.daily_availability?.map((day) => {
                      const isFull = day.free === 0
                      const isLow = day.free > 0 && day.free <= 2
                      const cellBg = isFull
                        ? 'bg-rose-50 text-rose-800 border-rose-200'
                        : isLow
                          ? 'bg-amber-50 text-amber-800 border-amber-200'
                          : 'bg-emerald-50 text-emerald-800 border-emerald-200'

                      return (
                        <td
                          key={day.date}
                          className="p-2 text-center border-l border-gray-100 last:border-l-0"
                        >
                          <div
                            className={`p-1.5 rounded-lg border text-center transition ${cellBg}`}
                          >
                            <div className="font-bold text-xs">
                              {day.free} <span className="font-normal text-[10px]">آزاد</span>
                            </div>
                            <div className="text-[10px] opacity-75">
                              {day.reserved} رزرو
                            </div>
                          </div>
                        </td>
                      )
                    })}
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


