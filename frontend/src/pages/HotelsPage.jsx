import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getHotelsApi } from '../api/hotels'
import SearchForm from '../components/SearchForm'
import ErrorMessage from '../components/common/ErrorMessage'
import EmptyState from '../components/common/EmptyState'
import { formatJalaliDate } from '../utils/jalali'

export default function HotelsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const cityParam = searchParams.get('city') || ''
  const checkInParam = searchParams.get('check_in') || ''
  const checkOutParam = searchParams.get('check_out') || ''
  const guestsParam = searchParams.get('guests') || '1'
  const minPriceParam = searchParams.get('min_price') || ''
  const maxPriceParam = searchParams.get('max_price') || ''
  const qParam = searchParams.get('q') || ''
  const starsParam = searchParams.get('star_rating') || ''
  const sortParam = searchParams.get('sort') || ''

  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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
    if (starsParam) params.star_rating = starsParam
    if (sortParam) params.sort = sortParam

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
  }, [cityParam, checkInParam, checkOutParam, guestsParam, minPriceParam, maxPriceParam, qParam, starsParam, sortParam])

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

  const handleApplyFilters = (filters) => {
    setLoading(true)
    const nextParams = new URLSearchParams(searchParams)

    if (filters.q) nextParams.set('q', filters.q)
    else nextParams.delete('q')

    if (filters.min_price) nextParams.set('min_price', filters.min_price)
    else nextParams.delete('min_price')

    if (filters.max_price) nextParams.set('max_price', filters.max_price)
    else nextParams.delete('max_price')

    if (filters.star_rating) nextParams.set('star_rating', filters.star_rating)
    else nextParams.delete('star_rating')

    if (filters.sort) nextParams.set('sort', filters.sort)
    else nextParams.delete('sort')

    setSearchParams(nextParams)
  }

  const handleClearFilters = () => {
    setLoading(true)
    const nextParams = new URLSearchParams()
    if (cityParam) nextParams.set('city', cityParam)
    if (checkInParam) nextParams.set('check_in', checkInParam)
    if (checkOutParam) nextParams.set('check_out', checkOutParam)
    if (guestsParam) nextParams.set('guests', guestsParam)
    setSearchParams(nextParams)
  }

  const handleRetry = () => {
    setLoading(true)
    const params = {}
    if (cityParam) params.city = cityParam
    if (checkInParam) params.check_in = checkInParam
    if (checkOutParam) params.check_out = checkOutParam
    if (guestsParam) params.guests = guestsParam
    if (minPriceParam) params.min_price = minPriceParam
    if (maxPriceParam) params.max_price = maxPriceParam
    if (qParam) params.q = qParam
    if (starsParam) params.star_rating = starsParam
    if (sortParam) params.sort = sortParam

    getHotelsApi(params)
      .then((data) => {
        setHotels(Array.isArray(data) ? data : [])
        setError(null)
      })
      .catch((err) => {
        setError(err.message || 'خطا در بارگذاری لیست هتل‌ها')
      })
      .finally(() => {
        setLoading(false)
      })
  }

  const buildHotelDetailUrl = (hotelId) => {
    const params = new URLSearchParams()
    if (checkInParam) params.set('check_in', checkInParam)
    if (checkOutParam) params.set('check_out', checkOutParam)
    if (guestsParam) params.set('guests', guestsParam)
    const qs = params.toString()
    return `/hotels/${hotelId}${qs ? `?${qs}` : ''}`
  }

  const hasExtraFilters = Boolean(qParam || minPriceParam || maxPriceParam || starsParam || sortParam)

  return (
    <div className="space-y-8">
      {/* Top Search Bar */}
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
        <FilterSidebar
          key={`${qParam}_${minPriceParam}_${maxPriceParam}_${starsParam}_${sortParam}`}
          initialQ={qParam}
          initialMinPrice={minPriceParam}
          initialMaxPrice={maxPriceParam}
          initialStars={starsParam}
          initialSort={sortParam}
          onApply={handleApplyFilters}
          onClear={handleClearFilters}
          hasExtraFilters={hasExtraFilters}
        />

        {/* Hotels Results Listing */}
        <section className="lg:col-span-3 space-y-4">
          {/* Status summary */}
          <div className="flex flex-wrap items-center justify-between gap-2 bg-white px-5 py-3 rounded-2xl border border-gray-200 text-sm text-gray-600 shadow-2xs">
            <div>
              {cityParam ? (
                <span>
                  هتل‌های موجود در <strong className="text-gray-900">{cityParam}</strong>
                </span>
              ) : (
                <span>نمایش همه هتل‌ها</span>
              )}
              {checkInParam && checkOutParam && (
                <span className="text-xs text-blue-600 mr-2 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100">
                  {formatJalaliDate(checkInParam, 'long')} تا {formatJalaliDate(checkOutParam, 'long')} ({guestsParam} مسافر)
                </span>
              )}
            </div>
            <span className="font-semibold text-gray-900 text-xs sm:text-sm">
              {loading ? 'در حال جستجو...' : `${hotels.length} هتل یافت شد`}
            </span>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-2xl border border-gray-200 p-5 animate-pulse space-y-4">
                  <div className="h-44 bg-gray-200 rounded-xl" />
                  <div className="h-5 bg-gray-200 rounded-md w-3/4" />
                  <div className="h-4 bg-gray-200 rounded-md w-1/2" />
                  <div className="h-10 bg-gray-200 rounded-xl" />
                </div>
              ))}
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <ErrorMessage
              message={error}
              onRetry={handleRetry}
            />
          )}

          {/* Empty State */}
          {!loading && !error && hotels.length === 0 && (
            <EmptyState
              icon="🔍"
              title="هیچ هتلی با این مشخصات یافت نشد!"
              description={
                checkInParam
                  ? 'ممکن است ظرفیت اتاق‌ها در تاریخ انتخابی تکمیل شده باشد یا معیارهای جستجو را خیلی محدود کرده باشید.'
                  : 'لطفاً فیلترهای جستجو، شهر یا محدوده قیمت را تغییر دهید.'
              }
              action={
                <button
                  type="button"
                  onClick={handleClearFilters}
                  className="px-5 py-2.5 bg-blue-50 text-blue-600 hover:bg-blue-100 font-bold rounded-xl text-xs transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  مشاهده همه هتل‌ها
                </button>
              }
            />
          )}

          {/* Hotels Grid */}
          {!loading && !error && hotels.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {hotels.map((hotel) => {
                const stars = hotel.star_rating || 1

                return (
                  <div
                    key={hotel.id}
                    className="group bg-white rounded-2xl border border-gray-200 shadow-xs hover:shadow-md transition-all flex flex-col justify-between overflow-hidden"
                  >
                    {/* Hotel Real Image / Header */}
                    <div className="relative h-48 bg-gray-900 overflow-hidden flex flex-col justify-between p-4 text-white">
                      {hotel.image_url ? (
                        <img
                          src={hotel.image_url}
                          alt={hotel.name}
                          className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-85"
                          onError={(e) => {
                            e.target.style.display = 'none'
                          }}
                        />
                      ) : null}

                      {/* Readability Gradient */}
                      <div className="absolute inset-0 bg-gradient-to-t from-gray-950/90 via-gray-900/40 to-black/30 pointer-events-none" />

                      <div className="relative z-10 flex items-center justify-between">
                        <span className="bg-black/50 backdrop-blur-md px-2.5 py-1 rounded-full text-xs font-medium border border-white/20">
                          📍 {hotel.city}
                        </span>
                        <div className="flex items-center gap-0.5 text-amber-300 text-xs sm:text-sm bg-black/40 backdrop-blur-md px-2.5 py-0.5 rounded-full border border-white/10">
                          {'★'.repeat(stars)}
                          <span className="text-[11px] text-white/90 mr-1">({stars} ستاره)</span>
                        </div>
                      </div>

                      <div className="relative z-10">
                        <h3 className="text-lg sm:text-xl font-black text-white drop-shadow-sm">
                          {hotel.name}
                        </h3>
                        <p className="text-xs text-gray-200 line-clamp-1 mt-0.5">
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
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                        >
                          <span>مشاهده اتاق‌ها</span>
                          <span>←</span>
                        </Link>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

function FilterSidebar({
  initialQ,
  initialMinPrice,
  initialMaxPrice,
  initialStars,
  initialSort,
  onApply,
  onClear,
  hasExtraFilters,
}) {
  const [q, setQ] = useState(initialQ)
  const [minPrice, setMinPrice] = useState(initialMinPrice)
  const [maxPrice, setMaxPrice] = useState(initialMaxPrice)
  const [stars, setStars] = useState(initialStars)
  const [sort, setSort] = useState(initialSort)

  const handleSubmit = (e) => {
    e.preventDefault()
    onApply({
      q: q.trim(),
      min_price: minPrice,
      max_price: maxPrice,
      star_rating: stars,
      sort,
    })
  }

  return (
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
            onClick={onClear}
            className="text-xs text-red-600 hover:text-red-700 cursor-pointer font-medium"
          >
            حذف فیلترها
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Search by name/keyword */}
        <div>
          <label htmlFor="filter-q" className="block text-xs font-semibold text-gray-700 mb-1">
            نام یا مشخصات هتل
          </label>
          <input
            id="filter-q"
            type="text"
            placeholder="مثلاً اسپیناس، درویشی..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-full h-10 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs sm:text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-2xs"
          />
        </div>

        {/* Star Rating Filter */}
        <div>
          <label htmlFor="filter-stars" className="block text-xs font-semibold text-gray-700 mb-1">
            درجه و ستاره هتل
          </label>
          <select
            id="filter-stars"
            value={stars}
            onChange={(e) => setStars(e.target.value)}
            className="w-full h-10 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs sm:text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-2xs cursor-pointer"
          >
            <option value="">همه درجه‌ها</option>
            <option value="5">⭐⭐⭐⭐⭐ فقط ۵ ستاره</option>
            <option value="4">⭐⭐⭐⭐ ۴ ستاره و بالاتر</option>
            <option value="3">⭐⭐⭐ ۳ ستاره و بالاتر</option>
          </select>
        </div>

        {/* Sorting Filter */}
        <div>
          <label htmlFor="filter-sort" className="block text-xs font-semibold text-gray-700 mb-1">
            مرتب‌سازی نتایج
          </label>
          <select
            id="filter-sort"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="w-full h-10 px-3 bg-gray-50 border border-gray-300 rounded-xl text-xs sm:text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-2xs cursor-pointer"
          >
            <option value="">پیش‌فرض سیستم</option>
            <option value="price_asc">ارزان‌ترین به گران‌ترین</option>
            <option value="price_desc">گران‌ترین به ارزان‌ترین</option>
            <option value="stars_desc">بیشترین ستاره</option>
          </select>
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
                step="100000"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="w-full h-10 px-2 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center shadow-2xs"
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="تا"
                min="0"
                step="100000"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="w-full h-10 px-2 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white text-center shadow-2xs"
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
  )
}
