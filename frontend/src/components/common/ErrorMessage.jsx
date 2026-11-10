export default function ErrorMessage({
  title,
  message,
  onRetry,
  className = '',
}) {
  if (!message) return null

  return (
    <div
      role="alert"
      className={`p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-sm ${className}`}
    >
      <div className="flex items-center gap-2">
        <span className="text-base select-none" aria-hidden="true">
          ⚠️
        </span>
        <div>
          {title && <strong className="font-semibold block">{title}</strong>}
          <span>{message}</span>
        </div>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="self-end sm:self-auto px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-800 rounded-lg text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-red-400 cursor-pointer"
        >
          تلاش مجدد
        </button>
      )}
    </div>
  )
}
