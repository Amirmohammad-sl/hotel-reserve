import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCitiesApi } from '../api/hotels'

export default function SearchForm({
  initialValues = {},
  onSearch = null,
  compact = false,
  className = '',
}) {
  const navigate = useNavigate()
  const [cities, setCities] = useState([])
  const [loadingCities, setLoadingCities] = useState(true)

  const [city, setCity] = useState(initialValues.city || '')
  const [checkIn, setCheckIn] = useState(initialValues.check_in || '')
  const [checkOut, setCheckOut] = useState(initialValues.check_out || '')
  const [guests, setGuests] = useState(initialValues.guests || 1)
  const [dateError, setDateError] = useState('')


  useEffect(() => {
    let isMounted = true
    async function loadCities() {
      try {
        const data = await getCitiesApi()
        if (isMounted && Array.isArray(data)) {
          setCities(data)
        }
      } catch {
        // Fallback or ignore
      } finally {
        if (isMounted) setLoadingCities(false)
      }
    }
    loadCities()
    return () => {
      isMounted = false
    }
  }, [])

  const todayStr = new Date().toISOString().split('T')[0]

  const handleCheckInChange = (e) => {
    const newIn = e.target.value
    setCheckIn(newIn)
    setDateError('')
    if (checkOut && newIn && checkOut <= newIn) {
      // Auto-set checkOut to next day
      const d = new Date(newIn)
      d.setDate(d.getDate() + 1)
      setCheckOut(d.toISOString().split('T')[0])
    }
  }

  const handleCheckOutChange = (e) => {
    const newOut = e.target.value
    setCheckOut(newOut)
    setDateError('')
    if (checkIn && newOut && newOut <= checkIn) {
      setDateError('تاریخ خروج باید بعد از تاریخ ورود باشد.')
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (checkIn && checkOut && checkOut <= checkIn) {
      setDateError('تاریخ خروج باید بعد از تاریخ ورود باشد.')
      return
    }

    const searchParams = {
      city: city.trim(),
      check_in: checkIn,
      check_out: checkOut,
      guests: Number(guests) > 0 ? Number(guests) : 1,
    }

    if (onSearch) {
      onSearch(searchParams)
    } else {
      const query = new URLSearchParams()
      if (searchParams.city) query.set('city', searchParams.city)
      if (searchParams.check_in) query.set('check_in', searchParams.check_in)
      if (searchParams.check_out) query.set('check_out', searchParams.check_out)
      if (searchParams.guests) query.set('guests', String(searchParams.guests))
      navigate(`/hotels?${query.toString()}`)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-6 transition-all ${className}`}
    >
      <div className={`grid gap-4 ${compact ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-5' : 'grid-cols-1 md:grid-cols-4'}`}>
        {/* City selection */}
        <div>
          <label htmlFor="search-city" className="block text-xs font-semibold text-gray-700 mb-1">
            مقصد یا شهر
          </label>
          <div className="relative">
            <select
              id="search-city"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all appearance-none cursor-pointer"
            >
              <option value="">همه شهرها</option>
              {cities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
              {!cities.includes(city) && city && (
                <option value={city}>{city}</option>
              )}
            </select>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          {loadingCities && (
            <span className="text-[10px] text-gray-400 mt-0.5 block">در حال دریافت لیست شهرها...</span>
          )}
        </div>

        {/* Check-in date */}
        <div>
          <label htmlFor="search-check-in" className="block text-xs font-semibold text-gray-700 mb-1">
            تاریخ ورود
          </label>
          <input
            id="search-check-in"
            type="date"
            min={todayStr}
            value={checkIn}
            onChange={handleCheckInChange}
            className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all cursor-pointer"
          />
        </div>

        {/* Check-out date */}
        <div>
          <label htmlFor="search-check-out" className="block text-xs font-semibold text-gray-700 mb-1">
            تاریخ خروج
          </label>
          <input
            id="search-check-out"
            type="date"
            min={checkIn || todayStr}
            value={checkOut}
            onChange={handleCheckOutChange}
            className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all cursor-pointer"
          />
        </div>

        {/* Guests count */}
        <div>
          <label htmlFor="search-guests" className="block text-xs font-semibold text-gray-700 mb-1">
            تعداد مهمانان
          </label>
          <div className="flex items-center">
            <input
              id="search-guests"
              type="number"
              min="1"
              max="20"
              value={guests}
              onChange={(e) => setGuests(Math.max(1, parseInt(e.target.value, 10) || 1))}
              className="w-full h-11 px-3 bg-gray-50 border border-gray-300 rounded-xl text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        {/* Submit button (if compact, placed in grid; otherwise full width on mobile or inline) */}
        {compact && (
          <div className="flex items-end">
            <button
              type="submit"
              className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-sm shadow-xs transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>جستجو</span>
            </button>
          </div>
        )}
      </div>

      {dateError && (
        <div className="mt-2 text-xs text-red-600 font-medium">
          {dateError}
        </div>
      )}

      {!compact && (
        <div className="mt-4 pt-3 border-t border-gray-100 flex justify-end">
          <button
            type="submit"
            className="w-full sm:w-auto px-8 h-12 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>جستجوی هتل‌ها</span>
          </button>
        </div>
      )}
    </form>
  )
}
