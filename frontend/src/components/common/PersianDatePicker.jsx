import { useState, useRef, useEffect } from 'react'
import {
  toJalaali,
  jalaaliMonthLength,
  jalaliToIso,
  isoToJalali,
  formatJalaliDate,
  getTodayIso,
  getJalaliWeekday,
  PERSIAN_MONTH_NAMES,
  PERSIAN_WEEKDAY_SHORT,
} from '../../utils/jalali'

export default function PersianDatePicker({
  value = '', // ISO date string "YYYY-MM-DD"
  onChange,
  min = '', // Minimum allowed ISO date string
  placeholder = 'انتخاب تاریخ...',
  label = '',
  className = '',
  required = false,
  id,
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [navOffset, setNavOffset] = useState(0) // offset in months
  const containerRef = useRef(null)

  const todayIso = getTodayIso()
  const todayJalali = toJalaali(todayIso)

  // Determine base year and month from selected value or today
  const selectedJalali = value ? isoToJalali(value) : null
  const baseYear = selectedJalali?.jy || todayJalali.jy
  const baseMonth = selectedJalali?.jm || todayJalali.jm

  // Total months calculation
  const totalMonths = baseYear * 12 + (baseMonth - 1) + navOffset
  const viewYear = Math.floor(totalMonths / 12)
  const viewMonth = (totalMonths % 12) + 1

  // Close calendar when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handlePrevMonth = () => {
    setNavOffset((prev) => prev - 1)
  }

  const handleNextMonth = () => {
    setNavOffset((prev) => prev + 1)
  }

  const handleSelectDay = (day) => {
    const iso = jalaliToIso(viewYear, viewMonth, day)
    onChange?.(iso)
    setIsOpen(false)
    setNavOffset(0)
  }

  const handleSelectToday = () => {
    onChange?.(todayIso)
    setIsOpen(false)
    setNavOffset(0)
  }

  const handleClear = () => {
    onChange?.('')
    setIsOpen(false)
    setNavOffset(0)
  }

  const monthLength = jalaaliMonthLength(viewYear, viewMonth)
  const startWeekday = getJalaliWeekday(viewYear, viewMonth, 1) // 0 = Sat, 6 = Fri

  const days = []
  for (let d = 1; d <= monthLength; d++) {
    const dayIso = jalaliToIso(viewYear, viewMonth, d)
    const isDisabled = min ? dayIso < min : false
    const isSelected = value === dayIso
    const isToday = todayIso === dayIso
    days.push({
      day: d,
      iso: dayIso,
      isDisabled,
      isSelected,
      isToday,
    })
  }

  const toFa = (num) => String(num).replace(/[0-9]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d])

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {label && (
        <label htmlFor={id} className="block text-[11px] font-bold text-gray-700 mb-1">
          {label}
        </label>
      )}

      {/* Trigger Button */}
      <button
        type="button"
        id={id}
        onClick={() => {
          setIsOpen((prev) => !prev)
          setNavOffset(0)
        }}
        className="w-full h-10 px-3 bg-white border border-gray-300 rounded-xl text-xs text-right font-medium flex items-center justify-between gap-2 shadow-2xs hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors cursor-pointer"
      >
        <span className={value ? 'text-gray-900 font-semibold' : 'text-gray-400'}>
          {value ? formatJalaliDate(value, 'long') : placeholder}
        </span>
        <svg
          className="w-4 h-4 text-gray-400 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.8}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </button>

      {/* Hidden input for form requirements */}
      {required && (
        <input
          type="text"
          value={value}
          required
          tabIndex={-1}
          className="sr-only"
          onChange={() => {}}
        />
      )}

      {/* Calendar Dropdown Popup */}
      {isOpen && (
        <div className="absolute z-50 mt-1.5 w-72 bg-white rounded-2xl shadow-xl border border-gray-200 p-3.5 right-0 animate-in fade-in zoom-in-95 duration-100">
          {/* Calendar Header: Month/Year navigation */}
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <button
              type="button"
              onClick={handleNextMonth}
              className="p-1 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors cursor-pointer"
              title="ماه بعد"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <span className="text-xs font-bold text-gray-900">
              {PERSIAN_MONTH_NAMES[viewMonth - 1]} {toFa(viewYear)}
            </span>

            <button
              type="button"
              onClick={handlePrevMonth}
              className="p-1 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors cursor-pointer"
              title="ماه قبل"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Weekday Labels (Sat to Fri) */}
          <div className="grid grid-cols-7 gap-1 mt-2 mb-1 text-center">
            {PERSIAN_WEEKDAY_SHORT.map((wd, i) => (
              <span
                key={wd}
                className={`text-[10px] font-bold ${i === 6 ? 'text-red-500' : 'text-gray-400'}`}
              >
                {wd}
              </span>
            ))}
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7 gap-1 text-center">
            {/* Empty slots before first day of month */}
            {Array.from({ length: startWeekday }).map((_, i) => (
              <div key={`empty-${i}`} className="h-7 w-7" />
            ))}

            {days.map(({ day, isDisabled, isSelected, isToday }) => (
              <button
                key={day}
                type="button"
                disabled={isDisabled}
                onClick={() => handleSelectDay(day)}
                className={`h-7 w-7 mx-auto rounded-lg text-xs font-medium flex items-center justify-center transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-600 text-white font-bold shadow-xs'
                    : isToday
                      ? 'border border-blue-500 text-blue-600 font-bold hover:bg-blue-50'
                      : isDisabled
                        ? 'text-gray-300 cursor-not-allowed'
                        : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {toFa(day)}
              </button>
            ))}
          </div>

          {/* Footer Shortcuts */}
          <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-[11px]">
            <button
              type="button"
              onClick={handleSelectToday}
              className="text-blue-600 hover:text-blue-800 font-semibold cursor-pointer"
            >
              امروز
            </button>
            {value && (
              <button
                type="button"
                onClick={handleClear}
                className="text-red-500 hover:text-red-700 font-medium cursor-pointer"
              >
                پاک کردن
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
