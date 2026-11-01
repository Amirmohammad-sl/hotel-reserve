/**
 * Utility to extract a cookie value by name (e.g., Django's csrftoken)
 */
export function getCookie(name) {
  if (typeof document === 'undefined') return null
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return decodeURIComponent(parts.pop().split(';').shift())
  }
  return null
}

/**
 * Normalized API error class containing status and field-level validation errors
 */
export class ApiError extends Error {
  constructor(message, status = 500, errors = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.errors = errors
  }
}

/**
 * Unified fetch wrapper with CSRF, same-origin credentials, and error normalization.
 */
export async function apiRequest(endpoint, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = { ...options.headers }

  const isMutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)
  if (isMutating) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  let body = options.body
  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }

  const config = {
    method,
    credentials: 'same-origin',
    ...options,
    headers,
    body,
  }

  let response
  try {
    response = await fetch(endpoint, config)
  } catch (err) {
    throw new ApiError(
      'خطا در برقراری ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید.',
      0,
      { network: [err.message] }
    )
  }

  if (response.status === 204) {
    return null
  }

  let responseData = null
  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    try {
      responseData = await response.json()
    } catch {
      responseData = null
    }
  }

  if (!response.ok) {
    const message =
      responseData?.message ||
      (response.status === 404
        ? 'منبع درخواستی یافت نشد.'
        : response.status === 403
          ? 'شما دسترسی لازم برای این عملیات را ندارید.'
          : response.status === 401
            ? 'لطفاً ابتدا وارد سیستم شوید.'
            : 'خطایی در پردازش درخواست رخ داد.')

    const errors = responseData?.errors || {}
    throw new ApiError(message, response.status, errors)
  }

  if (responseData && typeof responseData === 'object' && 'data' in responseData) {
    return responseData.data
  }

  return responseData
}

export const apiClient = {
  get: (url, options) => apiRequest(url, { ...options, method: 'GET' }),
  post: (url, body, options) => apiRequest(url, { ...options, method: 'POST', body }),
  put: (url, body, options) => apiRequest(url, { ...options, method: 'PUT', body }),
  patch: (url, body, options) => apiRequest(url, { ...options, method: 'PATCH', body }),
  delete: (url, options) => apiRequest(url, { ...options, method: 'DELETE' }),
}

export default apiClient
