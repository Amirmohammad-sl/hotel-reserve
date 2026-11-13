import { useState, useEffect, useCallback } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { getHotelDetailApi, getHotelRoomsApi } from '../api/hotels'
import BookingModal from '../components/BookingModal'
import EmptyState from '../components/common/EmptyState'
import PersianDatePicker from '../components/common/PersianDatePicker'
import { formatJalaliDate, getTodayIso } from '../utils/jalali'
import { getHotelImageUrl } from '../utils/imageUrl'

function isFilled(v) {
  return Boolean(v && String(v).trim())
}

export default function HotelDetailPage() {
  const { id } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()

  const checkIn = searchParams.get('check_in') || ''
  const checkOut = searchParams.get('check_out') || ''
  const guests = parseInt(searchParams.get('guests') || '1', 10)

  const [hotel, setHotel] = useState(null)
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [updatingAvailability, setUpdatingAvailability] = useState(false)
  const [error, setError] = useState(null)
  const [dateAlert, setDateAlert] = useState('')

  // Booking modal state
  const [selectedRoom, setSelectedRoom] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Quick date change inputs on the page
  const [inInput, setInInput] = useState(checkIn)
  const [outInput, setOutInput] = useState(checkOut)
  const [guestsInput, setGuestsInput] = useState(guests)

  const todayIso = getTodayIso()

  // Function to load room availability
  const loadRoomAvailability = useCallback(
    async (inDate, outDate, guestsCount, fallbackRooms = []) => {
      if (!inDate && !outDate) {
        // No dates specified: return default rooms without availability check
        setRooms(fallbackRooms)
        return
      }

      if (isFilled(inDate) ^ isFilled(outDate)) {
        // Only one date specified, keep existing rooms
        setRooms(fallbackRooms)
        return
      }

      try {
        setUpdatingAvailability(true)
        const roomParams = {
          check_in: inDate,
          check_out: outDate,
          guests: guestsCount || 1,
        }
        const roomsData = await getHotelRoomsApi(id, roomParams)
        setRooms(Array.isArray(roomsData) ? roomsData : fallbackRooms)
        setDateAlert('')
      } catch (err) {
        setDateAlert(err.message || 'خطا در استعلام ظرفیت اتاق‌ها')
      } finally {
        setUpdatingAvailability(false)
      }
    },
    [id]
  )

  // Initial load of hotel details
  useEffect(() => {
    let ignore = false

    async function loadData() {
      try {
        setLoading(true)
        const hotelData = await getHotelDetailApi(id)
        if (ignore) return
        setHotel(hotelData)

        const defaultRooms = hotelData.room_types || []
        if (checkIn && checkOut) {
          const roomParams = {
            check_in: checkIn,
            check_out: checkOut,
            guests: guests || 1,
          }
          try {
            const roomsData = await getHotelRoomsApi(id, roomParams)
            if (ignore) return
            setRooms(Array.isArray(roomsData) ? roomsData : defaultRooms)
          } catch (roomsErr) {
            if (ignore) return
            setRooms(defaultRooms)
            setDateAlert(roomsErr.message || 'خطا در بررسی ظرفیت')
          }
        } else {
          setRooms(defaultRooms)
        }
        setError(null)
      } catch (err) {
        if (!ignore) {
          setError(err.message || 'خطا در دریافت اطلاعات هتل')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    loadData()

    return () => {
      ignore = true
    }
  }, [id, checkIn, checkOut, guests])

  const handleUpdateDates = async (e) => {
    e.preventDefault()
    setDateAlert('')

    // Client-side validations
    if ((inInput && !outInput) || (!inInput && outInput)) {
      setDateAlert('لطفاً هر دو تاریخ ورود و خروج را مشخص کنید.')
      return
    }

    if (inInput && outInput && outInput <= inInput) {
      setDateAlert('تاریخ خروج باید بعد از تاریخ ورود باشد.')
      return
    }

    if (inInput && inInput < todayIso) {
      setDateAlert('تاریخ ورود نمی‌تواند قبل از امروز باشد.')
      return
    }

    // Update URL Search Params
    const nextParams = new URLSearchParams(searchParams)
    if (inInput) nextParams.set('check_in', inInput)
    else nextParams.delete('check_in')

    if (outInput) nextParams.set('check_out', outInput)
    else nextParams.delete('check_out')

    if (guestsInput) nextParams.set('guests', String(guestsInput))
    else nextParams.delete('guests')

    setSearchParams(nextParams)

    // Also fetch availability directly so it never hangs even if params didn't change
    await loadRoomAvailability(inInput, outInput, guestsInput, hotel?.room_types || [])
  }

  const handleOpenBooking = (room) => {
    setSelectedRoom(room)
    setIsModalOpen(true)
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4" />
        <div className="h-72 bg-gray-200 rounded-3xl" />
        <div className="h-28 bg-gray-200 rounded-2xl" />
        <div className="space-y-4">
          <div className="h-28 bg-gray-200 rounded-2xl" />
          <div className="h-28 bg-gray-200 rounded-2xl" />
        </div>
      </div>
    )
  }

  if (error || !hotel) {
    return (
      <div className="max-w-xl mx-auto py-12">
        <EmptyState
          icon="❌"
          title={error || 'هتل مورد نظر یافت نشد.'}
          description="ممکن است اطلاعات این هتل تغییر کرده باشد یا موقتاً در دسترس نباشد."
          action={
            <Link
              to="/hotels"
              className="inline-block px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              بازگشت به لیست هتل‌ها
            </Link>
          }
        />
      </div>
    )
  }

  const starCount = hotel.star_rating || 1

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Back button & Breadcrumb */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <Link
          to={`/hotels${searchParams.toString() ? `?${searchParams.toString()}` : ''}`}
          className="flex items-center gap-1.5 text-blue-600 hover:text-blue-800 font-semibold"
        >
          <span>→</span>
          <span>بازگشت به لیست هتل‌ها</span>
        </Link>
        <span>شناسه هتل: #{hotel.id}</span>
      </div>

      {/* Hotel Banner with Real Image & Overlay */}
      <div className="bg-white rounded-3xl border border-gray-200 overflow-hidden shadow-xs">
        <div className="relative h-64 sm:h-80 overflow-hidden bg-gray-900 flex flex-col justify-between p-6 sm:p-8 text-white">
          {hotel.image_url ? (
            <img
              src={getHotelImageUrl(hotel.image_url)}
              alt={hotel.name}
              className="absolute inset-0 w-full h-full object-cover opacity-80"
              onError={(e) => {
                // If real image fails, fallback gracefully
                e.target.style.display = 'none'
              }}
            />
          ) : null}

          {/* Gradient Overlay for high readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-gray-950/90 via-gray-900/50 to-black/30 pointer-events-none" />

          {/* Top Info Bar */}
          <div className="relative z-10 flex items-center justify-between">
            <span className="bg-black/50 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold border border-white/20">
              📍 {hotel.city}
            </span>
            <div className="flex items-center gap-1 text-amber-300 text-base font-bold bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
              {'★'.repeat(starCount)}
              <span className="text-xs text-white/90 mr-1.5">({starCount} ستاره)</span>
            </div>
          </div>

          {/* Bottom Title & Address */}
          <div className="relative z-10">
            <h1 className="text-2xl sm:text-4xl font-black drop-shadow-md">
              {hotel.name}
            </h1>
            <p className="mt-1.5 text-xs sm:text-sm text-gray-200 flex items-center gap-1">
              <span>{hotel.address}</span>
            </p>
          </div>
        </div>

        {/* Hotel Description Body */}
        <div className="p-6 sm:p-8 space-y-4">
          <h2 className="text-sm font-bold text-gray-900">درباره این هتل</h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            {hotel.description || 'این هتل با ارائه برترین امکانات و کادری مجرب، آماده پذیرایی از شما عزیزان است.'}
          </p>
        </div>
      </div>

      {/* Dates Adjustment Bar (Persian Calendar) */}
      <div className="bg-blue-50/70 border border-blue-100 rounded-2xl p-4 sm:p-5 shadow-xs space-y-3">
        <form onSubmit={handleUpdateDates} className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
          <div>
            <PersianDatePicker
              id="detail-check-in"
              label="تاریخ ورود (شمسی)"
              value={inInput}
              min={todayIso}
              onChange={(iso) => {
                setInInput(iso)
                setDateAlert('')
                if (outInput && iso && outInput <= iso) {
                  // Push outInput by 1 day
                  const d = new Date(iso)
                  d.setDate(d.getDate() + 1)
                  const pad = (n) => String(n).padStart(2, '0')
                  setOutInput(`${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`)
                }
              }}
              placeholder="انتخاب تاریخ ورود"
            />
          </div>

          <div>
            <PersianDatePicker
              id="detail-check-out"
              label="تاریخ خروج (شمسی)"
              value={outInput}
              min={inInput || todayIso}
              onChange={(iso) => {
                setOutInput(iso)
                setDateAlert('')
              }}
              placeholder="انتخاب تاریخ خروج"
            />
          </div>

          <div>
            <label htmlFor="detail-guests" className="block text-[11px] font-bold text-gray-700 mb-1">
              تعداد مهمانان
            </label>
            <input
              id="detail-guests"
              type="number"
              min="1"
              max="20"
              value={guestsInput}
              onChange={(e) => setGuestsInput(Math.max(1, parseInt(e.target.value, 10) || 1))}
              className="w-full h-10 px-3 bg-white border border-gray-300 rounded-xl text-xs text-center focus:ring-2 focus:ring-blue-500 shadow-2xs"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={updatingAvailability}
              className="w-full h-10 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center justify-center gap-2 shadow-xs"
            >
              {updatingAvailability ? (
                <>
                  <span className="h-3.5 w-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  <span>در حال بررسی...</span>
                </>
              ) : (
                <span>به‌روزرسانی ظرفیت</span>
              )}
            </button>
          </div>
        </form>

        {/* Inline Date Alert */}
        {dateAlert && (
          <div className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-xl flex items-center gap-2">
            <span>⚠️</span>
            <span>{dateAlert}</span>
          </div>
        )}

        {/* Selected Date Summary */}
        {checkIn && checkOut && (
          <div className="text-xs text-blue-700 flex items-center gap-1.5 pt-1">
            <span>📅 اقامت انتخاب‌شده:</span>
            <span className="font-bold">{formatJalaliDate(checkIn, 'long')}</span>
            <span>تا</span>
            <span className="font-bold">{formatJalaliDate(checkOut, 'long')}</span>
            <span className="text-blue-500">({guests} مسافر)</span>
          </div>
        )}
      </div>

      {/* Room Types Listing */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-gray-900">انواع اتاق‌های این هتل</h2>
          <span className="text-xs text-gray-500">
            {rooms.length} نوع اتاق تعریف شده
          </span>
        </div>

        {rooms.length === 0 ? (
          <EmptyState
            icon="🛏️"
            title="هیچ نوع اتاقی یافت نشد"
            description="در حال حاضر هیچ نوع اتاقی برای این هتل با شرایط انتخابی موجود یا فعال نیست."
          />
        ) : (
          <div className="grid gap-4">
            {rooms.map((room) => {
              const isAvailable = room.available_count === undefined || room.available_count > 0

              return (
                <div
                  key={room.id}
                  className="bg-white rounded-2xl border border-gray-200 p-5 sm:p-6 shadow-xs hover:border-blue-200 transition-all flex flex-col sm:flex-row justify-between gap-4"
                >
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-base font-bold text-gray-900">
                        {room.title}
                      </h3>
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700 font-medium">
                        👥 ظرفیت: {room.capacity} نفر
                      </span>
                      {room.available_count !== undefined && (
                        <span
                          className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                            room.available_count > 0
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-red-50 text-red-700 border border-red-200'
                          }`}
                        >
                          {room.available_count > 0
                            ? `${room.available_count} اتاق آماده رزرو`
                            : 'ظرفیت تکمیل'}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-gray-600 leading-relaxed">
                      {room.description || 'اتاق مجهز و استاندارد با تمامی امکانات رفاهی.'}
                    </p>

                    {/* Room Amenities Badges */}
                    {room.amenities && room.amenities.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {room.amenities.map((a) => (
                          <span
                            key={a.id || a.name}
                            className="text-[11px] bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-md border border-blue-100"
                          >
                            ✓ {a.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Price & Book Action */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between border-t sm:border-t-0 pt-3 sm:pt-0 sm:border-r sm:pr-6 border-gray-100 min-w-[150px] shrink-0">
                    <div className="text-right">
                      <span className="text-[11px] text-gray-500 block">قیمت هر شب:</span>
                      <div className="text-base sm:text-lg font-black text-blue-600">
                        {Number(room.price_per_night).toLocaleString('fa-IR')}
                        <span className="text-xs font-normal text-gray-500 mr-1">تومان</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      disabled={!isAvailable}
                      onClick={() => handleOpenBooking(room)}
                      className={`mt-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer ${
                        isAvailable
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {isAvailable ? 'رزرو این اتاق' : 'ظرفیت تکمیل'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Booking Modal */}
      {selectedRoom && (
        <BookingModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setSelectedRoom(null)
          }}
          hotel={hotel}
          roomType={selectedRoom}
          initialCheckIn={checkIn || inInput}
          initialCheckOut={checkOut || outInput}
          initialGuests={guests || guestsInput}
        />
      )}
    </div>
  )
}
