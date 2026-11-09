import { useState, useEffect } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { getHotelDetailApi, getHotelRoomsApi } from '../api/hotels'
import BookingModal from '../components/BookingModal'
import EmptyState from '../components/common/EmptyState'

export default function HotelDetailPage() {
  const { id } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()

  const checkIn = searchParams.get('check_in') || ''
  const checkOut = searchParams.get('check_out') || ''
  const guests = parseInt(searchParams.get('guests') || '1', 10)

  const [hotel, setHotel] = useState(null)
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Booking modal state
  const [selectedRoom, setSelectedRoom] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Quick date change inputs on the page
  const [inInput, setInInput] = useState(checkIn)
  const [outInput, setOutInput] = useState(checkOut)
  const [guestsInput, setGuestsInput] = useState(guests)

  const todayStr = new Date().toISOString().split('T')[0]

  useEffect(() => {
    let ignore = false

    async function loadData() {
      try {
        const hotelData = await getHotelDetailApi(id)
        if (ignore) return
        setHotel(hotelData)

        // If dates are provided, get real-time availability for rooms
        const roomParams = {}
        if (checkIn) roomParams.check_in = checkIn
        if (checkOut) roomParams.check_out = checkOut
        if (guests) roomParams.guests = guests

        const roomsData = await getHotelRoomsApi(id, roomParams)
        if (ignore) return
        setRooms(Array.isArray(roomsData) ? roomsData : hotelData.room_types || [])
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

  const handleUpdateDates = (e) => {
    e.preventDefault()
    setLoading(true)
    const nextParams = new URLSearchParams(searchParams)
    if (inInput) nextParams.set('check_in', inInput)
    else nextParams.delete('check_in')

    if (outInput) nextParams.set('check_out', outInput)
    else nextParams.delete('check_out')

    if (guestsInput) nextParams.set('guests', String(guestsInput))
    else nextParams.delete('guests')

    setSearchParams(nextParams)
  }

  const handleOpenBooking = (room) => {
    setSelectedRoom(room)
    setIsModalOpen(true)
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4" />
        <div className="h-64 bg-gray-200 rounded-3xl" />
        <div className="h-32 bg-gray-200 rounded-2xl" />
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

  const starCount = hotel.star_rating || hotel.stars || 1

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

      {/* Hotel Banner & Info Card */}
      <div className="bg-white rounded-3xl border border-gray-200 overflow-hidden shadow-xs">
        <div className="relative h-60 sm:h-72 bg-linear-to-tr from-blue-800 via-indigo-700 to-sky-600 p-6 sm:p-8 flex flex-col justify-between text-white">
          <div className="flex items-center justify-between">
            <span className="bg-black/30 backdrop-blur-xs px-3 py-1 rounded-full text-xs font-semibold">
              📍 {hotel.city}
            </span>
            <div className="flex items-center gap-1 text-amber-300 text-base font-bold">
              {'★'.repeat(starCount)}
              <span className="text-xs text-white/90 mr-1.5">({starCount} ستاره)</span>
            </div>
          </div>

          <div>
            <h1 className="text-2xl sm:text-4xl font-black drop-shadow-sm">
              {hotel.name}
            </h1>
            <p className="mt-1 text-sm text-white/90 flex items-center gap-1">
              <span>{hotel.address}</span>
            </p>
          </div>
        </div>

        <div className="p-6 sm:p-8 space-y-4">
          <h2 className="text-sm font-bold text-gray-900">درباره این هتل</h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            {hotel.description || 'این هتل با ارائه برترین امکانات و کادری مجرب، آماده پذیرایی از شما عزیزان است.'}
          </p>
        </div>
      </div>

      {/* Dates Adjustment Bar */}
      <div className="bg-blue-50/70 border border-blue-100 rounded-2xl p-4 sm:p-5 shadow-xs">
        <form onSubmit={handleUpdateDates} className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
          <div>
            <label className="block text-[11px] font-bold text-gray-700 mb-1">
              تاریخ ورود
            </label>
            <input
              type="date"
              min={todayStr}
              value={inInput}
              onChange={(e) => setInInput(e.target.value)}
              className="w-full h-10 px-3 bg-white border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-[11px] font-bold text-gray-700 mb-1">
              تاریخ خروج
            </label>
            <input
              type="date"
              min={inInput || todayStr}
              value={outInput}
              onChange={(e) => setOutInput(e.target.value)}
              className="w-full h-10 px-3 bg-white border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-[11px] font-bold text-gray-700 mb-1">
              تعداد مهمانان
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={guestsInput}
              onChange={(e) => setGuestsInput(Math.max(1, parseInt(e.target.value, 10) || 1))}
              className="w-full h-10 px-3 bg-white border border-gray-300 rounded-xl text-xs text-center focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <button
              type="submit"
              className="w-full h-10 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              به‌روزرسانی ظرفیت
            </button>
          </div>
        </form>
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
            description="در حال حاضر هیچ نوع اتاقی برای این هتل تعریف یا فعال نشده است."
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
                            ? `${room.available_count} اتاق خالی`
                            : 'ظرفیت تکمیل'}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-gray-600 leading-relaxed">
                      {room.description || 'اتاقی دنج و مجهز به کلیه امکانات استاندارد هتلی.'}
                    </p>

                    {/* Room Amenities */}
                    {room.amenities && room.amenities.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {room.amenities.map((amenity) => (
                          <span
                            key={amenity.id || amenity.name}
                            className="text-[11px] px-2 py-0.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-100"
                          >
                            ✓ {amenity.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Room Pricing & Action */}
                  <div className="sm:border-r sm:border-gray-100 sm:pr-6 flex sm:flex-col justify-between items-end sm:justify-center gap-3 min-w-[160px]">
                    <div>
                      <span className="text-[11px] text-gray-400 block text-left sm:text-right">قیمت هر شب:</span>
                      <div className="text-lg font-black text-blue-600">
                        {Number(room.price_per_night).toLocaleString('fa-IR')}
                        <span className="text-xs font-normal text-gray-500 mr-1">تومان</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      disabled={!isAvailable}
                      onClick={() => handleOpenBooking(room)}
                      className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                        isAvailable
                          ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-xs'
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
      <BookingModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        hotel={hotel}
        roomType={selectedRoom}
        initialCheckIn={checkIn}
        initialCheckOut={checkOut}
        initialGuests={guests}
      />
    </div>
  )
}
