import LoadingSpinner from './LoadingSpinner'

export default function PageLoader({ message = 'در حال بارگذاری صفحه...' }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="min-h-[50vh] flex flex-col items-center justify-center p-8"
    >
      <div className="text-3xl mb-3 animate-bounce select-none" aria-hidden="true">
        🏨
      </div>
      <LoadingSpinner size="md" message={message} />
      <span className="sr-only">{message}</span>
    </div>
  )
}
