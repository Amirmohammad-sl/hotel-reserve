export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
        <div>
          <span>© {new Date().toLocaleDateString('fa-IR', { year: 'numeric' })} سامانه رزرواسیون هتل</span>
          <span className="mx-2">•</span>
          <span>پروژه درس برنامه‌نویسی وب</span>
        </div>
        <div className="flex gap-4">
          <span className="text-gray-400">طراحی و پیاده‌سازی هیبریدی (Django + React)</span>
        </div>
      </div>
    </footer>
  )
}
