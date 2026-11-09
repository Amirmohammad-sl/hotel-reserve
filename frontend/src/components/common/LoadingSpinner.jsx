export default function LoadingSpinner({
  size = 'md',
  message = 'در حال بارگذاری...',
  inline = false,
  className = '',
}) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }

  const spinner = (
    <div
      className={`inline-block animate-spin rounded-full border-blue-600 border-t-transparent ${sizeClasses[size] || sizeClasses.md}`}
      aria-hidden="true"
    />
  )

  if (inline) {
    return (
      <div
        role="status"
        aria-live="polite"
        className={`inline-flex items-center gap-2 text-sm text-gray-500 ${className}`}
      >
        {spinner}
        <span>{message}</span>
        <span className="sr-only">{message}</span>
      </div>
    )
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className={`py-12 flex flex-col items-center justify-center text-center ${className}`}
    >
      {spinner}
      {message && <p className="mt-3 text-sm text-gray-500">{message}</p>}
      <span className="sr-only">{message || 'در حال بارگذاری...'}</span>
    </div>
  )
}
