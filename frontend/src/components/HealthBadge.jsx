import { useEffect, useState, useCallback } from 'react'
import { getHealth } from '../api/health'

export default function HealthBadge() {
  const [status, setStatus] = useState('loading') // 'loading' | 'online' | 'offline'
  const [details, setDetails] = useState(null)

  const checkHealth = useCallback(async () => {
    setStatus('loading')
    try {
      const data = await getHealth()
      if (data && data.status === 'ok') {
        setStatus('online')
        setDetails(data)
      } else {
        setStatus('offline')
        setDetails(data)
      }
    } catch (err) {
      setStatus('offline')
      setDetails({ error: err.message })
    }
  }, [])

  useEffect(() => {
    let ignore = false
    getHealth()
      .then((data) => {
        if (!ignore) {
          if (data && data.status === 'ok') {
            setStatus('online')
            setDetails(data)
          } else {
            setStatus('offline')
            setDetails(data)
          }
        }
      })
      .catch((err) => {
        if (!ignore) {
          setStatus('offline')
          setDetails({ error: err.message })
        }
      })

    return () => {
      ignore = true
    }
  }, [])

  return (
    <div className="inline-flex items-center gap-3 p-3 rounded-xl border bg-white shadow-xs">
      <span className="text-sm font-medium text-gray-700">وضعیت اتصال به سرور بک‌اند:</span>

      {status === 'loading' && (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
          <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
          در حال بررسی...
        </span>
      )}

      {status === 'online' && (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
          بک‌اند آنلاین است ({details?.status || 'ok'})
        </span>
      )}

      {status === 'offline' && (
        <div className="inline-flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
            <span className="h-2 w-2 rounded-full bg-rose-500"></span>
            بک‌اند در دسترس نیست
          </span>
          <button
            type="button"
            onClick={checkHealth}
            className="text-xs text-blue-600 hover:text-blue-800 underline cursor-pointer"
          >
            تلاش مجدد
          </button>
        </div>
      )}
    </div>
  )
}
