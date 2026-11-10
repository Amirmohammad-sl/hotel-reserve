import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import RequireRole from './components/guards/RequireRole'
import PageLoader from './components/common/PageLoader'

const HomePage = lazy(() => import('./pages/HomePage'))
const HotelsPage = lazy(() => import('./pages/HotelsPage'))
const HotelDetailPage = lazy(() => import('./pages/HotelDetailPage'))
const MyBookingsPage = lazy(() => import('./pages/MyBookingsPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const ManagerPage = lazy(() => import('./pages/ManagerPage'))
const VerifyEmailPage = lazy(() => import('./pages/VerifyEmailPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="hotels" element={<HotelsPage />} />
              <Route path="hotels/:id" element={<HotelDetailPage />} />
              <Route
                path="my-bookings"
                element={
                  <RequireRole role="guest">
                    <MyBookingsPage />
                  </RequireRole>
                }
              />
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />
              <Route path="verify-email" element={<VerifyEmailPage />} />
              <Route
                path="manager"
                element={
                  <RequireRole role="manager">
                    <ManagerPage />
                  </RequireRole>
                }
              />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  )
}
