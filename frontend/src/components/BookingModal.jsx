import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getBookingQuoteApi, validateDiscountApi, createBookingApi } from '../api/bookings'

export default function BookingModal({
  hotel,
  roomType,
  initialCheckIn = '',
  initialCheckOut = '',
  initialGuests = 1,
  isOpen,
  onClose,
}) {
  const navigate = useNavigate()
  const { user, isGuest } = useAuth()

  const [checkIn, setCheckIn] = useState(initialCheckIn)
  const [checkOut, setCheckOut] = useState(initialCheckOut)
  const [roomsCount, setRoomsCount] = useState(1)
  const [guestsCount, setGuestsCount] = useState(initialGuests || 1)
  const [discountCode, setDiscountCode] = useState('')
  const [appliedDiscount, setAppliedDiscount] = useState('')

  const [quote, setQuote] = useState(null)
  const [quoteLoading, setQuoteLoading] = useState(false)
  const [quoteError, setQuoteError] = useState('')

  const [discountStatus, setDiscountStatus] = useState(null)
  const [validatingDiscount, setValidatingDiscount] = useState(false)

  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

  const todayStr = new Date().toISOString().split('T')[0]

  const maxCapacity = (roomType?.capacity || 1) * roomsCount
  const capacityExceeded = guestsCount > maxCapacity

  // Quote effect: runs whenever booking inputs or applied discount code change
  useEffect(() => {
    if (!isOpen || !isGuest || !roomType?.id || !checkIn || !checkOut || checkOut <= checkIn || capacityExceeded) {
      return
    }

    let ignore = false

    getBookingQuoteApi({
      room_type: roomType.id,
      check_in: checkIn,
      check_out: checkOut,
      rooms_count: roomsCount,
      guests_count: guestsCount,
      discount_code: appliedDiscount.trim() || undefined,
    })
      .then((data) => {
        if (!ignore) {
          setQuote(data)
          setQuoteError('')
          setQuoteLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          setQuote(null)
          setQuoteError(err.message || 'خطا در محاسبه قیمت و بررسی ظرفیت')
          setQuoteLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [isOpen, isGuest, roomType, checkIn, checkOut, roomsCount, guestsCount, appliedDiscount, capacityExceeded])

  if (!isOpen || !roomType) return null

  const handleValidateDiscount = async () => {
    const code = discountCode.trim()
    if (!code) {
      setDiscountStatus({ valid: false, message: 'لطفاً کد تخفیف را وارد کنید.' })
      setAppliedDiscount('')
      return
    }

    setValidatingDiscount(true)
    setDiscountStatus(null)
    try {
      const res = await validateDiscountApi({
        hotel: hotel?.id || roomType.hotel_id,
        code,
      })
      setDiscountStatus(res)
      if (res?.valid) {
        setQuoteLoading(true)
        setAppliedDiscount(code)
      } else {
        setAppliedDiscount('')
      }
    } catch (err) {
      setDiscountStatus({ valid: false, message: err.message || 'کد تخفیف نامعتبر است.' })
      setAppliedDiscount('')
    } finally {
      setValidatingDiscount(false)
    }
  }

  const handleBookingSubmit = async (e) => {
    e.preventDefault()
    setSubmitError('')

    if (!checkIn || !checkOut) {
      setSubmitError('لطفاً تاریخ ورود و خروج را مشخص کنید.')
      return
    }

    if (checkOut <= checkIn) {
      setSubmitError('تاریخ خروج باید پس از تاریخ ورود باشد.')
      return
    }

    if (capacityExceeded) {
      setSubmitError(`تعداد مسافران نمی‌تواند بیش از ظرفیت اتاق‌ها (${maxCapacity} نفر) باشد.`)
      return
    }

    setSubmitting(true)
    try {
      await createBookingApi({
        room_type: roomType.id,
        check_in: checkIn,
        check_out: checkOut,
        rooms_count: roomsCount,
        guests_count: guestsCount,
        discount_code: appliedDiscount.trim() || undefined,
      })
      onClose()
      navigate('/my-bookings', { state: { bookingSuccess: true } })
    } catch (err) {
      if (err.status === 409) {
        setSubmitError('متأسفانه ظرفیت این نوع اتاق برای تاریخ‌های انتخابی تکمیل شده است.')
      } else {
        setSubmitError(err.message || 'خطا در ثبت رزرو. لطفاً مجدداً تلاش کنید.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="relative bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl border border-gray-100 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-gray-100">
          <div>
            <span className="text-xs text-blue-600 font-bold block mb-1">
              {hotel?.name} (📍 {hotel?.city})
            </span>
            <h2 className="text-xl font-black text-gray-900">
              رزرو {roomType.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors cursor-pointer"
            aria-label="بستن"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content depending on Auth */}
        {!user ? (
          <div className="py-8 text-center space-y-4">
            <div className="text-4xl">🔐</div>
            <h3 className="text-base font-bold text-gray-800">
              برای ثبت رزرو ابتدا وارد سیستم شوید
            </h3>
            <p className="text-xs text-gray-500 max-w-sm mx-auto">
              برای مشاهده پیش‌فاکتور، اعمال کد تخفیف و نهایی کردن رزرو، نیاز به ورود به حساب کاربری مهمان دارید.
            </p>
            <div className="pt-2 flex justify-center gap-3">
              <Link
                to="/login"
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors"
              >
                ورود به حساب کاربری
              </Link>
              <Link
                to="/register"
                className="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-medium transition-colors"
              >
                ثبت‌نام جدید
              </Link>
            </div>
          </div>
        ) : !isGuest ? (
          <div className="py-8 text-center space-y-3">
            <div className="text-4xl">⚠️</div>
            <h3 className="text-base font-bold text-gray-800">
              امکان رزرو فقط برای کاربران با نقش مهمان
            </h3>
            <p className="text-xs text-gray-500 max-w-sm mx-auto">
              نقش فعلی شما «مدیر هتل» است. برای ثبت رزرو، لطفاً با یک حساب مهمان وارد شوید.
            </p>
          </div>
        ) : (
          <form onSubmit={handleBookingSubmit} className="mt-5 space-y-5">
            {/* Dates Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  تاریخ ورود
                </label>
                <input
                  type="date"
                  min={todayStr}
                  value={checkIn}
                  onChange={(e) => {
                    setQuoteLoading(true)
                    setCheckIn(e.target.value)
                  }}
                  required
                  className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  تاریخ خروج
                </label>
                <input
                  type="date"
                  min={checkIn || todayStr}
                  value={checkOut}
                  onChange={(e) => {
                    setQuoteLoading(true)
                    setCheckOut(e.target.value)
                  }}
                  required
                  className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white"
                />
              </div>
            </div>

            {/* Counts Row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  تعداد اتاق
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={roomsCount}
                  onChange={(e) => {
                    setQuoteLoading(true)
                    setRoomsCount(Math.max(1, parseInt(e.target.value, 10) || 1))
                  }}
                  className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center font-bold"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  تعداد مسافران
                </label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={guestsCount}
                  onChange={(e) => {
                    setQuoteLoading(true)
                    setGuestsCount(Math.max(1, parseInt(e.target.value, 10) || 1))
                  }}
                  className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center font-bold"
                />
              </div>
            </div>

            {capacityExceeded && (
              <p className="text-xs text-red-600 font-medium">
                ظرفیت هر اتاق {roomType.capacity} نفر است. برای {guestsCount} مسافر باید حداقل {Math.ceil(guestsCount / roomType.capacity)} اتاق انتخاب کنید.
              </p>
            )}

            {/* Discount Code Input */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                کد تخفیف (اختیاری)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="مثال: SUMMER20"
                  value={discountCode}
                  onChange={(e) => {
                    setDiscountCode(e.target.value)
                    setDiscountStatus(null)
                  }}
                  className="flex-1 h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs uppercase focus:ring-2 focus:ring-blue-500 focus:bg-white font-mono"
                />
                <button
                  type="button"
                  onClick={handleValidateDiscount}
                  disabled={validatingDiscount || !discountCode.trim()}
                  className="px-4 h-11 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-bold transition-colors disabled:opacity-50 cursor-pointer"
                >
                  {validatingDiscount ? 'بررسی...' : 'اعمال تخفیف'}
                </button>
              </div>
              {discountStatus && (
                <p className={`mt-1 text-xs font-medium ${discountStatus.valid ? 'text-emerald-600' : 'text-red-600'}`}>
                  {discountStatus.valid
                    ? `✓ کد تخفیف معتبر است (${discountStatus.percent}% تخفیف اعمال شد)`
                    : `✗ ${discountStatus.message}`}
                </p>
              )}
            </div>

            {/* Price Quote Breakdown */}
            <div className="bg-blue-50/60 rounded-2xl p-4 border border-blue-100 space-y-2 text-xs">
              <div className="flex items-center justify-between text-gray-600">
                <span>قیمت پایه هر شب:</span>
                <span className="font-semibold text-gray-900">
                  {Number(roomType.price_per_night).toLocaleString('fa-IR')} تومان
                </span>
              </div>

              {quoteLoading ? (
                <div className="py-2 text-center text-blue-600 font-medium animate-pulse">
                  در حال محاسبه قیمت و استعلام ظرفیت...
                </div>
              ) : quote ? (
                <>
                  <div className="flex items-center justify-between text-gray-600">
                    <span>مدت اقامت:</span>
                    <span className="font-semibold text-gray-900">
                      {quote.nights} شب ({roomsCount} اتاق)
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-gray-600">
                    <span>مبلغ کل:</span>
                    <span className="font-semibold text-gray-900">
                      {Number(quote.subtotal).toLocaleString('fa-IR')} تومان
                    </span>
                  </div>
                  {quote.discount_amount > 0 && (
                    <div className="flex items-center justify-between text-emerald-600 font-medium">
                      <span>تخفیف اعمال‌شده:</span>
                      <span>
                        - {Number(quote.discount_amount).toLocaleString('fa-IR')} تومان
                      </span>
                    </div>
                  )}
                  <div className="pt-2 border-t border-blue-200/60 flex items-center justify-between text-sm font-black text-blue-900">
                    <span>مبلغ قابل پرداخت:</span>
                    <span className="text-base text-blue-600">
                      {Number(quote.total_price).toLocaleString('fa-IR')} تومان
                    </span>
                  </div>
                </>
              ) : (
                <div className="text-gray-400 text-center py-1">
                  {quoteError || 'لطفاً تاریخ ورود و خروج معتبر انتخاب کنید.'}
                </div>
              )}
            </div>

            {/* Error alerts */}
            {submitError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium text-center">
                {submitError}
              </div>
            )}

            {/* Action buttons */}
            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 h-12 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-bold transition-colors cursor-pointer"
              >
                انصراف
              </button>
              <button
                type="submit"
                disabled={submitting || quoteLoading || !quote || capacityExceeded}
                className="flex-2 h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {submitting ? 'در حال ثبت نهایی...' : 'تأیید و ثبت رزرو'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
