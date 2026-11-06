import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout, isManager } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch {
      // Handled in auth context
    }
  }

  const navLinkClass = ({ isActive }) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-700 text-white'
        : 'text-gray-700 hover:bg-gray-100 hover:text-blue-600'
    }`

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-blue-600">
              <span className="text-2xl">🏨</span>
              <span>رزرواسیون هتل</span>
            </Link>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-2">
            <NavLink to="/" end className={navLinkClass}>
              صفحه اصلی
            </NavLink>
            <NavLink to="/hotels" className={navLinkClass}>
              هتل‌ها
            </NavLink>
            {isManager && (
              <NavLink to="/manager" className={navLinkClass}>
                پنل مدیریت
              </NavLink>
            )}
          </nav>

          {/* Auth Links */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="font-medium text-gray-900">{user.username}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-medium">
                    {user.role === 'manager' ? 'مدیر هتل' : 'مهمان'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                >
                  خروج
                </button>
              </div>
            ) : (
              <>
                <NavLink
                  to="/login"
                  className="text-sm font-medium text-gray-700 hover:text-blue-600 px-3 py-1.5"
                >
                  ورود
                </NavLink>
                <NavLink
                  to="/register"
                  className="text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
                >
                  ثبت‌نام
                </NavLink>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              aria-label="باز کردن منو"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden border-t border-gray-100 px-4 pt-2 pb-4 space-y-2 bg-white">
          <NavLink
            to="/"
            end
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
          >
            صفحه اصلی
          </NavLink>
          <NavLink
            to="/hotels"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
          >
            هتل‌ها
          </NavLink>
          {isManager && (
            <NavLink
              to="/manager"
              onClick={() => setIsOpen(false)}
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              پنل مدیریت
            </NavLink>
          )}

          <div className="pt-3 border-t border-gray-100">
            {user ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-900">{user.username}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                    {user.role === 'manager' ? 'مدیر هتل' : 'مهمان'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setIsOpen(false)
                    handleLogout()
                  }}
                  className="w-full text-center px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors"
                >
                  خروج از حساب
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <NavLink
                  to="/login"
                  onClick={() => setIsOpen(false)}
                  className="block text-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md"
                >
                  ورود
                </NavLink>
                <NavLink
                  to="/register"
                  onClick={() => setIsOpen(false)}
                  className="block text-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md"
                >
                  ثبت‌نام
                </NavLink>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
