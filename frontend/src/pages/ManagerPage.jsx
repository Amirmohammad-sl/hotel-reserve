import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { getManagerHotelsApi } from '../api/manager'
import HotelListTab from './manager/HotelListTab'
import RoomTypesTab from './manager/RoomTypesTab'
import BookingsTab from './manager/BookingsTab'
import AvailabilityTab from './manager/AvailabilityTab'
import DiscountsTab from './manager/DiscountsTab'

const TABS = [
  { id: 'hotels', label: 'هتل‌های من', icon: '🏨' },
  { id: 'rooms', label: 'انواع اتاق‌ها', icon: '🚪' },
  { id: 'bookings', label: 'رزروها', icon: '📋' },
  { id: 'availability', label: 'تقویم ظرفیت', icon: '📊' },
  { id: 'discounts', label: 'کدهای تخفیف', icon: '🏷️' },
]

export default function ManagerPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const currentTab = searchParams.get('tab') || 'hotels'
  const currentHotelId = searchParams.get('hotelId')
    ? Number(searchParams.get('hotelId'))
    : null

  const [hotels, setHotels] = useState([])

  useEffect(() => {
    let isMounted = true

    async function loadHotels() {
      try {
        const data = await getManagerHotelsApi()
        if (isMounted) {
          setHotels(Array.isArray(data) ? data : [])
        }
      } catch {
        // HotelListTab displays its own error handling
      }
    }

    loadHotels()

    return () => {
      isMounted = false
    }
  }, [])

  // Derived selected hotel id: URL param if valid, or first hotel
  const selectedHotelId =
    currentHotelId || (hotels.length > 0 ? hotels[0].id : null)

  function handleTabChange(tabId) {
    const params = new URLSearchParams(searchParams)
    params.set('tab', tabId)
    if (selectedHotelId) {
      params.set('hotelId', selectedHotelId)
    }
    setSearchParams(params)
  }

  function handleHotelChange(hotelId) {
    const params = new URLSearchParams(searchParams)
    params.set('hotelId', hotelId)
    setSearchParams(params)
  }

  function handleSelectHotelForTab(hotelId, targetTab) {
    const params = new URLSearchParams()
    params.set('tab', targetTab)
    params.set('hotelId', hotelId)
    setSearchParams(params)
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-gray-200 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-gray-900">پنل مدیریت هتل‌ها</h1>
            <span className="text-xs px-2.5 py-1 rounded-full bg-blue-100 text-blue-800 font-semibold">
              هتل‌دار
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            مدیریت هتل‌ها، ظرفیت روزانه اتاق‌ها، مشاهده رزروهای ثبت‌شده و تعریف کدهای تخفیف
          </p>
        </div>

        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-blue-600 bg-white border border-gray-200 hover:border-blue-200 px-3 py-2 rounded-xl transition shadow-sm"
        >
          <span>←</span>
          <span>بازگشت به صفحه اصلی</span>
        </Link>
      </div>

      {/* Tabs navigation */}
      <div
        role="tablist"
        aria-label="بخش‌های پنل مدیریت"
        className="flex overflow-x-auto gap-2 p-1.5 bg-gray-100 rounded-2xl border border-gray-200/80"
      >
        {TABS.map((tab) => {
          const isActive = currentTab === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isActive}
              onClick={() => handleTabChange(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                isActive
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/60'
              }`}
            >
              <span aria-hidden="true">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Contents */}
      <div role="tabpanel" className="min-h-[450px]">
        {currentTab === 'hotels' && (
          <HotelListTab
            onSelectHotelForTab={handleSelectHotelForTab}
            onHotelsChange={setHotels}
          />
        )}

        {currentTab === 'rooms' && (
          <RoomTypesTab
            hotels={hotels}
            selectedHotelId={selectedHotelId}
            onHotelChange={handleHotelChange}
          />
        )}

        {currentTab === 'bookings' && (
          <BookingsTab
            hotels={hotels}
            selectedHotelId={selectedHotelId}
            onHotelChange={handleHotelChange}
          />
        )}

        {currentTab === 'availability' && (
          <AvailabilityTab
            hotels={hotels}
            selectedHotelId={selectedHotelId}
            onHotelChange={handleHotelChange}
          />
        )}

        {currentTab === 'discounts' && (
          <DiscountsTab
            hotels={hotels}
            selectedHotelId={selectedHotelId}
            onHotelChange={handleHotelChange}
          />
        )}
      </div>
    </div>
  )
}
