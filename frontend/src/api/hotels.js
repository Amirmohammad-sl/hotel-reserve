import { apiClient } from './client'

/**
 * Builds a valid query string from an object, skipping undefined, null, or empty string values.
 */
function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  }
  const qs = searchParams.toString()
  return qs ? `?${qs}` : ''
}

/**
 * Fetch distinct cities with active hotels.
 * GET /api/cities/
 */
export async function getCitiesApi() {
  return apiClient.get('/api/cities/')
}

/**
 * Search hotels by city, dates, guests count, price range, and name search query.
 * GET /api/hotels/?city=&check_in=&check_out=&guests=&min_price=&max_price=&q=
 */
export async function getHotelsApi(params = {}) {
  const qs = buildQueryString(params)
  return apiClient.get(`/api/hotels/${qs}`)
}

/**
 * Fetch detailed hotel information with room types.
 * GET /api/hotels/{id}/
 */
export async function getHotelDetailApi(hotelId) {
  return apiClient.get(`/api/hotels/${hotelId}/`)
}

/**
 * Fetch room types of a hotel with available_count for specified dates and guests.
 * GET /api/hotels/{id}/rooms/?check_in=&check_out=&guests=
 */
export async function getHotelRoomsApi(hotelId, params = {}) {
  const qs = buildQueryString(params)
  return apiClient.get(`/api/hotels/${hotelId}/rooms/${qs}`)
}

/**
 * Fetch single room type details including amenities and hotel summary.
 * GET /api/rooms/{id}/
 */
export async function getRoomDetailApi(roomId) {
  return apiClient.get(`/api/rooms/${roomId}/`)
}
