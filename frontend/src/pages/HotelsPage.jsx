import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getHotelsApi } from '../api/hotels'
import SearchForm from '../components/SearchForm'

export default function HotelsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const cityParam = searchParams.get('city') || ''
  const checkInParam = searchParams.get('check_in') || ''
  const checkOutParam = searchParams.get('check_out') || ''
  const guestsParam = searchParams.get('guests') || '1'
  const minPriceParam = searchParams.get('min_price') || ''
  const maxPriceParam = searchParams.get('max_price') || ''
  const qParam = searchParams.get('q') || ''

  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Filter controls state initialized from URL params
  const [qInput, setQInput] = useState(qParam)
  const [minPriceInput, setMinPriceInput] = useState(minPriceParam)
  const [maxPriceInput, setMaxPriceInput] = useState(maxPriceParam)

  useEffect(() => {
    let ignore = false

    const params = {}
    if (cityParam) params.city = cityParam
    if (checkInParam) params.check_in = checkInParam
    if (checkOutParam) params.check_out = checkOutParam
    if (guestsParam) params.guests = guestsParam
    if (minPriceParam) params.min_price = minPriceParam
    if (maxPriceParam) params.max_price = maxPriceParam
    if (qParam) params.q = qParam

    getHotelsApi(params)
      .then((data) => {
        if (!ignore) {
          setHotels(Array.isArray(data) ? data : [])
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message || 'خطا در بارگذاری لیست هتل‌ها')
          setLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [cityParam, checkInParam, checkOutParam, guestsParam, minPriceParam, maxPriceParam, qParam])

  const handleSearchSubmit = (newParams) => {
    setLoading(true)
    const nextParams = new URLSearchParams(searchParams)
    if (newParams.city) nextParams.set('city', newParams.city)
    else nextParams.delete('city')

    if (newParams.check_in) nextParams.set('check_in', newParams.check_in)
    else nextParams.delete('check_in')

    if (newParams.check_out) nextParams.set('check_out', newParams.check_out)
    else nextParams.delete('check_out')

    if (newParams.guests) nextParams.set('guests', String(newParams.guests))
    else nextParams.delete('guests')

    setSearchParams(nextParams)
  }

  const handleApplyFilters = (e) => {
    e.preventDefault()
    setLoading(true)
    const nextParams = new URLSearchParams(searchParams)
    if (qInput.trim()) nextParams.set('q', qInput.trim())
    else nextParams.delete('q')

    if (minPriceInput) nextParams.set('min_price', minPriceInput)
    else nextParams.delete('min_price')

    if (maxPriceInput) nextParams.set('max_price', maxPriceInput)
    else nextParams.delete('max_price')

    setSearchParams(nextParams)
  }

  const handleClearFilters = () => {
    setQInput('')
    setMinPriceInput('')
    setMaxPriceInput('')
    setLoading(true)
    const nextParams = new URLSearchParams()
    if (cityParam) nextParams.set('city', cityParam)
    if (checkInParam) nextParams.set('check_in', checkInParam)
    if (checkOutParam) nextParams.set('check_out', checkOutParam)
    if (guestsParam) nextParams.set('guests', guestsParam)
    setSearchParams(nextParams)
  }

  const buildHotelDetailUrl = (hotelId) => {
    const params = new URLSearchParams()
    if (checkInParam) params.set('check_in', checkInParam)
    if (checkOutParam) params.set('check_out', checkOutParam)
    if (guestsParam) params.set('guests', guestsParam)
    const qs = params.toString()
    return `/hotels/${hotelId}${qs ? `?${qs}` : ''}`
  }

  const hasExtraFilters = Boolean(qParam || minPriceParam || maxPriceParam)

  return (
    <div className="space-y-8">
      {/* Search Header Form */}
      <div>
        <SearchForm
          key={`${cityParam}_${checkInParam}_${checkOutParam}_${guestsParam}`}
          initialValues={{
            city: cityParam,
            check_in: checkInParam,
            check_out: checkOutParam,
            guests: guestsParam ? parseInt(guestsParam, 10) : 1,
          }}
          onSearch={handleSearchSubmit}
          compact
          className="shadow-sm border border-gray-200"
        />
      </div>

      {/* Main Content Area: Sidebar filters + Hotels list */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
        {/* Sidebar Filters */}
        <aside className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>فیلترهای پیشرفته</span>
            </h2>
            {hasExtraFilters && (
              <button
                type="button"
                onClick={handleClearFilters}
                className="text-xs text-red-600 hover:text-red-700 cursor-pointer font-medium"
              >
                حذف فیلترها
              </button>
            )}
          </div>

          <form
            key={`${qParam}_${minPriceParam}_${maxPriceParam}`}
            onSubmit={handleApplyFilters}
            className="space-y-4"
          >
            {/* Search by name/keyword */}
            <div>
              <label htmlFor="filter-q" className="block text-xs font-semibold text-gray-700 mb-1">
                نام یا مشخصات هتل
              </label>
              <input
                id="filter-q"
                type="text"
                placeholder="مثلاً اسپیناس، هما..."
                value={qInput}
                onChange={(e) => setQInput(e.target.value)}
                className="w-full h-10 px-3 bg-gray-50 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              />
            </div>

            {/* Price range */}
            <div className="space-y-2">
              <span className="block text-xs font-semibold text-gray-700">
                محدوده قیمت (تومان / شب)
              </span>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <input
                    type="number"
                    placeholder="از"
                    min="0"
                    step="10000"
                    value={minPriceInput}
                    onChange={(e) => setMinPriceInput(e.target.value)}
                    className="w-full h-10 px-2 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    placeholder="تا"
                    min="0"
                    step="10000"
                    value={maxPriceInput}
                    onChange={(e) => setMaxPriceInput(e.target.value)}
                    className="w-full h-10 px-2 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors cursor-pointer"
            >
              اعمال فیلترها
            </button>
          </form>
        </aside>

        {/* Hotels Results Listing */}
        <section className="lg:col-span-3 space-y-4">
          {/* Status summary */}
          <div className="flex items-center justify-between bg-white px-5 py-3 rounded-2xl border border-gray-200 text-sm text-gray-600">
            <div>
              {cityParam ? (
                <span>
                  هتل‌های موجود در <strong className="text-gray-900">{cityParam}</strong>
                </span>
              ) : (
                <span>نمایش همه هتل‌ها</span>
              )}
              {checkInParam && checkOutParam && (
                <span className="text-xs text-blue-600 mr-2 bg-blue-50 px-2.5 py-1 rounded-full">
                  {checkInParam} تا {checkOutParam} ({guestsParam} مسافر)
                </span>
              )}
            </div>
            <span className="font-semibold text-gray-900">
              {loading ? 'در حال جستجو...' : `${hotels.length} هتل یافت شد`}
            </span>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-2xl border border-gray-200 p-5 animate-pulse space-y-4">
                  <div className="h-40 bg-gray-200 rounded-xl" />
                  <div className="h-5 bg-gray-200 rounded-md w-3/4" />
                  <div className="h-4 bg-gray-200 rounded-md w-1/2" />
                  <div className="h-10 bg-gray-200 rounded-xl" />
                </div>
              ))}
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700 space-y-3">
              <p className="font-medium">{error}</p>
              <button
                type="button"
                onClick={() => {
                  setLoading(true)
                  const params = {}
                  if (cityParam) params.city = cityParam
                  if (checkInParam) params.check_in = checkInParam
                  if (checkOutParam) params.check_out = checkOutParam
                  if (guestsParam) params.guests = guestsParam
                  if (minPriceParam) params.min_price = minPriceParam
                  if (maxPriceParam) params.max_price = maxPriceParam
                  if (qParam) params.q = qParam
                  getHotelsApi(params)
                    .then((data) => {
                      setHotels(Array.isArray(data) ? data : [])
                      setError(null)
                      setLoading(false)
                    })
                    .catch((err) => {
                      setError(err.message || 'خطا در بارگذاری لیست هتل‌ها')
                      setLoading(false)
                    })
                }}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
              >
                تلاش مجدد
              </button>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && hotels.length === 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center space-y-4">
              <div className="text-5xl">🔍</div>
              <h3 className="text-lg font-bold text-gray-800">هیچ هتلی با این مشخصات یافت نشد!</h3>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                {checkInParam
                  ? 'ممکن است ظرفیت اتاق‌ها در تاریخ انتخابی تکمیل شده باشد یا معیارهای جستجو را خیلی محدود کرده باشید.'
                  : 'لطفاً فیلترهای جستجو، شهر یا محدوده قیمت را تغییر دهید.'}
              </p>
              <button
                type="button"
                onClick={handleClearFilters}
                className="px-5 py-2.5 bg-blue-50 text-blue-600 hover:bg-blue-100 font-bold rounded-xl text-xs transition-colors cursor-pointer"
              >
                مشاهده همه هتل‌ها
              </button>
            </div>
          )}

          {/* Hotels Grid */}
          {!loading && !error && hotels.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {hotels.map((hotel) => (
                <div
                  key={hotel.id}
                  className="bg-white rounded-2xl border border-gray-200 shadow-xs hover:shadow-md transition-all flex flex-col justify-between overflow-hidden"
                >
                  {/* Hotel Header Image / Banner */}
                  <div className="relative h-44 bg-linear-to-tr from-blue-700 via-indigo-600 to-sky-500 p-4 flex flex-col justify-between text-white">
                    <div className="flex items-center justify-between">
                      <span className="bg-black/30 backdrop-blur-xs px-2.5 py-1 rounded-full text-xs font-medium">
                        📍 {hotel.city}
                      </span>
                      <div className="flex items-center gap-0.5 text-amber-300 text-sm">
                        {'★'.repeat(hotel.stars || 1)}
                        <span className="text-xs text-white/80 mr-1">({hotel.stars} ستاره)</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-black text-white drop-shadow-xs">
                        {hotel.name}
                      </h3>
                      <p className="text-xs text-white/90 line-clamp-1 mt-0.5">
                        {hotel.address}
                      </p>
                    </div>
                  </div>

                  {/* Hotel Details Body */}
                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
                      {hotel.description || 'هتلی زیبا با امکانات رفاهی کامل برای اقامتی آسوده و به‌یادماندنی.'}
                    </p>

                    <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
                      <div>
                        <span className="text-[11px] text-gray-500 block">شروع قیمت هر شب از:</span>
                        <div className="text-base font-black text-blue-600">
                          {hotel.min_price != null ? (
                            <>
                              <span>{Number(hotel.min_price).toLocaleString('fa-IR')}</span>
                              <span className="text-xs font-normal text-gray-500 mr-1">تومان</span>
                            </>
                          ) : (
                            <span className="text-xs font-normal text-gray-400">تماس بگیرید</span>
                          )}
                        </div>
                      </div>

                      <Link
                        to={buildHotelDetailUrl(hotel.id)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5"
                      >
                        <span>مشاهده اتاق‌ها</span>
                        <span>←</span>
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
