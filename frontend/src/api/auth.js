import { apiClient, ensureCsrfToken } from './client'

/**
 * Fetch CSRF token explicitly to seed the cookie.
 */
export async function getCsrfApi() {
  return ensureCsrfToken()
}

/**
 * Register a new user account.
 * Payload: { username, email, password, password2, role, phone }
 */
export async function registerApi(payload) {
  return apiClient.post('/api/auth/register/', payload)
}

/**
 * Log in a user and establish a server session.
 * Payload: { username_or_email, password, remember_me }
 */
export async function loginApi(payload) {
  return apiClient.post('/api/auth/login/', payload)
}

/**
 * Log out current authenticated session.
 */
export async function logoutApi() {
  return apiClient.post('/api/auth/logout/')
}

/**
 * Retrieve current user session ({ id, username, email, role, email_verified } or null).
 */
export async function getMeApi() {
  return apiClient.get('/api/auth/me/')
}

/**
 * Verify user email address with signed token.
 * Payload: { token }
 */
export async function verifyEmailApi(payload) {
  return apiClient.post('/api/auth/verify-email/', payload)
}

/**
 * Resend email verification link for current user session.
 */
export async function resendVerificationApi() {
  return apiClient.post('/api/auth/resend-verification/')
}
