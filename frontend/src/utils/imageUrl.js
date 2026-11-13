/**
 * Resolves a hotel image URL.
 * Handles external URLs (http/https) and local asset paths (/hotels/...).
 * In production when served by Django (BASE_URL = '/static/'), ensures the '/static/' prefix is added.
 */
export function getHotelImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const base = import.meta.env.BASE_URL || '/'
  if (url.startsWith('/')) {
    return (base.endsWith('/') ? base : `${base}/`) + url.slice(1)
  }
  return base + url
}
