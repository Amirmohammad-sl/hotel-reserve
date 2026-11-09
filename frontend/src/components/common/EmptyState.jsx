export default function EmptyState({
  icon = '📋',
  title = 'موردی یافت نشد',
  description,
  action,
  className = '',
}) {
  return (
    <div
      className={`bg-white rounded-2xl border border-gray-200 p-8 sm:p-12 text-center flex flex-col items-center justify-center ${className}`}
    >
      <div className="text-4xl sm:text-5xl mb-4 select-none" aria-hidden="true">
        {icon}
      </div>
      <h3 className="text-base sm:text-lg font-bold text-gray-800">
        {title}
      </h3>
      {description && (
        <p className="text-xs sm:text-sm text-gray-500 max-w-md mx-auto mt-2 leading-relaxed">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
