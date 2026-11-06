import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { getMyBookingsApi, cancelBookingApi } from '../api/bookings'

export default function MyBookingsPage() {
  const location = useLocation()
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Status message (e.g. from redirect after new booking or after cancel)
  const [successBanner, setSuccessBanner] = useState(
    location.state?.bookingSuccess ? 'رزرو شما با موفقیت ثبت و تأیید شد!' : ''
  )

  // Filter tab: 'all' | 'confirmed' | 'cancelled'
  const [filterTab, setFilterTab] = useState('all')

  // Cancel action state
  const [cancellingId, setCancellingId] = useState(null)
  const [confirmCancelBooking, setConfirmCancelBooking] = useState(null)
  const [cancelError, setCancelError] = useState('')

  const todayStr = new Date().toISOString().split('T')[0]

  useEffect(() => {
    let ignore = false

    getMyBookingsApi()
      .then((data) => {
        if (!ignore) {
          setBookings(Array.isArray(data) ? data : [])
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message || 'خطا در بارگذاری لیست رزروها')
          setLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [])

  const handleCancelBooking = async () => {
    if (!confirmCancelBooking) return

    setCancellingId(confirmCancelBooking.id)
    setCancelError('')

    try {
      const updated = await cancelBookingApi(confirmCancelBooking.id)
      setBookings((prev) =>
        prev.map((b) => (b.id === confirmCancelBooking.id ? updated : b))
      )
      setSuccessBanner(`رزرو شماره #${confirmCancelBooking.id} با موفقیت لغو شد و ظرفیت اتاق آزاد گردید.`)
      setConfirmCancelBooking(null)
    } catch (err) {
      setCancelError(err.message || 'خطا در لغو رزرو. ممکن است تاریخ ورود فرارسیده باشد.')
    } finally {
      setCancellingId(null)
    }
  }

  const filteredBookings = bookings.filter((b) => {
    if (filterTab === 'confirmed') return b.status === 'confirmed'
    if (filterTab === 'cancelled') return b.status === 'cancelled'
    return true
  })

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Page Title & Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-black text-gray-900">رزروهای من</h1>
          <p className="text-xs text-gray-500 mt-1">
            مشاهده سوابق رزرو، وضعیت اقامت و امکان لغو رزروهای آینده
          </p>
        </div>
        <Link
          to="/hotels"
          className="self-start sm:self-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors shadow-xs"
        >
          + رزرو جدید
        </Link>
      </div>

      {/* Success banner */}
      {successBanner && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-xs font-medium flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>✓</span>
            <span>{successBanner}</span>
          </div>
          <button
            type="button"
            onClick={() => setSuccessBanner('')}
            className="text-emerald-700 hover:text-emerald-900 cursor-pointer text-sm"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
        <button
          type="button"
          onClick={() => setFilterTab('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
            filterTab === 'all'
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          همه ({bookings.length})
        </button>
        <button
          type="button"
          onClick={() => setFilterTab('confirmed')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
            filterTab === 'confirmed'
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          تأیید شده ({bookings.filter((b) => b.status === 'confirmed').length})
        </button>
        <button
          type="button"
          onClick={() => setFilterTab('cancelled')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
            filterTab === 'cancelled'
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          لغو شده ({bookings.filter((b) => b.status === 'cancelled').length})
        </button>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 p-6 animate-pulse space-y-3">
              <div className="h-5 bg-gray-200 rounded w-1/3" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
              <div className="h-4 bg-gray-200 rounded w-1/4" />
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700 text-xs font-medium space-y-3">
          <p>{error}</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredBookings.length === 0 && (
        <div className="bg-white rounded-3xl border border-gray-200 p-12 text-center space-y-4">
          <div className="text-5xl">📑</div>
          <h3 className="text-base font-bold text-gray-800">
            {filterTab === 'all'
              ? 'شما هنوز هیچ رزروی ثبت نکرده‌اید.'
              : 'رزروی در این بخش یافت نشد.'}
          </h3>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            می‌توانید هتل‌های سراسر ایران را جستجو کرده و با بهترین قیمت اقامت خود را رزرو کنید.
          </p>
          <Link
            to="/hotels"
            className="inline-block px-5 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold shadow-xs hover:bg-blue-700 transition-colors"
          >
            مشاهده و جستجوی هتل‌ها
          </Link>
        </div>
      )}

      {/* Bookings List */}
      {!loading && !error && filteredBookings.length > 0 && (
        <div className="space-y-4">
          {filteredBookings.map((b) => {
            const isConfirmed = b.status === 'confirmed'
            const canCancel = isConfirmed && b.check_in > todayStr
            const hotelName = b.room_type?.hotel?.name || 'هتل'
            const hotelCity = b.room_type?.hotel?.city || ''
            const roomTitle = b.room_type?.title || 'اتاق'

            return (
              <div
                key={b.id}
                className="bg-white rounded-2xl border border-gray-200 p-5 sm:p-6 shadow-xs hover:border-gray-300 transition-all flex flex-col md:flex-row justify-between gap-6"
              >
                {/* Left/Main Column */}
                <div className="space-y-3 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-mono font-bold text-gray-500">
                      #{b.id}
                    </span>
                    <h3 className="text-base font-black text-gray-900">
                      {hotelName} {hotelCity && `(📍 ${hotelCity})`}
                    </h3>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                        isConfirmed
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-gray-100 text-gray-500 border border-gray-200'
                      }`}
                    >
                      {isConfirmed ? '✓ تایید شده' : '✕ لغو شده'}
                    </span>
                  </div>

                  <div className="text-xs text-gray-600 space-y-1">
                    <p>
                      <strong>نوع اتاق:</strong> {roomTitle} ({b.rooms_count} اتاق، {b.guests_count} مسافر)
                    </p>
                    <p>
                      <strong>بازه اقامت:</strong> از {b.check_in} تا {b.check_out} ({b.nights} شب)
                    </p>
                    {b.created_at && (
                      <p className="text-[11px] text-gray-400">
                        تاریخ ثبت رزرو: {new Date(b.created_at).toLocaleDateString('fa-IR')}
                      </p>
                    )}
                    {b.cancelled_at && (
                      <p className="text-[11px] text-red-500">
                        تاریخ لغو رزرو: {new Date(b.cancelled_at).toLocaleDateString('fa-IR')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Right Column: Financials & Action */}
                <div className="md:border-r md:border-gray-100 md:pr-6 flex md:flex-col justify-between items-end md:justify-center gap-3 min-w-[200px]">
                  <div className="text-left md:text-right">
                    <span className="text-[11px] text-gray-400 block">مبلغ کل پرداختی:</span>
                    <div className="text-base font-black text-blue-600">
                      {Number(b.total_price).toLocaleString('fa-IR')}
                      <span className="text-xs font-normal text-gray-500 mr-1">تومان</span>
                    </div>
                    {b.discount_amount > 0 && (
                      <span className="text-[11px] text-emerald-600 block">
                        (شامل {Number(b.discount_amount).toLocaleString('fa-IR')} تومان تخفیف کد {b.discount_code})
                      </span>
                    )}
                  </div>

                  {canCancel ? (
                    <button
                      type="button"
                      onClick={() => {
                        setCancelError('')
                        setConfirmCancelBooking(b)
                      }}
                      className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-bold transition-colors cursor-pointer"
                    >
                      لغو این رزرو
                    </button>
                  ) : isConfirmed ? (
                    <span className="text-[11px] text-gray-400">
                      غیرقابل لغو (اقامت آغاز شده)
                    </span>
                  ) : null}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Confirmation Modal for Cancel */}
      {confirmCancelBooking && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-gray-100 space-y-4">
            <div className="text-center space-y-2">
              <div className="text-4xl text-amber-500">⚠️</div>
              <h3 className="text-base font-bold text-gray-900">
                آیا از لغو رزرو اطمینان دارید؟
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                رزرو شماره #{confirmCancelBooking.id} در {confirmCancelBooking.room_type?.hotel?.name} لغو خواهد شد و اتاق‌های مربوطه بلافاصله برای سایر مهمانان آزاد می‌شوند.
              </p>
            </div>

            {cancelError && (
              <p className="text-xs text-red-600 font-medium text-center">
                {cancelError}
              </p>
            )}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setConfirmCancelBooking(null)}
                className="flex-1 h-11 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-bold transition-colors cursor-pointer"
              >
                انصراف
              </button>
              <button
                type="button"
                disabled={Boolean(cancellingId)}
                onClick={handleCancelBooking}
                className="flex-1 h-11 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold transition-colors disabled:opacity-50 cursor-pointer"
              >
                {cancellingId ? 'در حال لغو...' : 'بله، لغو شود'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
