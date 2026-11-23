import apiClient from './client'

/**
 * Manager API service for hotels, room types, amenities, bookings, availability, and discount codes.
 * Conforms to docs/API_CONTRACT.md and endpoints implemented in P2-03 and P2-04.
 */

// ---------------------------------------------------------------------------
// Hotels CRUD
// ---------------------------------------------------------------------------

export async function getManagerHotelsApi() {
  return apiClient.get('/api/manager/hotels/')
}

export async function getManagerHotelDetailApi(hotelId) {
  return apiClient.get(`/api/manager/hotels/${hotelId}/`)
}

export async function createManagerHotelApi(data) {
  return apiClient.post('/api/manager/hotels/', data)
}

export async function updateManagerHotelApi(hotelId, data) {
  return apiClient.put(`/api/manager/hotels/${hotelId}/`, data)
}

export async function deleteManagerHotelApi(hotelId) {
  return apiClient.delete(`/api/manager/hotels/${hotelId}/`)
}

// ---------------------------------------------------------------------------
// Room Types CRUD & Amenities
// ---------------------------------------------------------------------------

export async function getAmenitiesApi() {
  return apiClient.get('/api/amenities/')
}

export async function getManagerRoomTypesApi(hotelId) {
  return apiClient.get(`/api/manager/hotels/${hotelId}/room-types/`)
}

export async function createManagerRoomTypeApi(hotelId, data) {
  return apiClient.post(`/api/manager/hotels/${hotelId}/room-types/`, data)
}

export async function updateManagerRoomTypeApi(roomTypeId, data) {
  return apiClient.put(`/api/manager/room-types/${roomTypeId}/`, data)
}

export async function deleteManagerRoomTypeApi(roomTypeId) {
  return apiClient.delete(`/api/manager/room-types/${roomTypeId}/`)
}

// ---------------------------------------------------------------------------
// Bookings & Availability
// ---------------------------------------------------------------------------

export async function getManagerBookingsApi(hotelId, params = {}) {
  const query = new URLSearchParams()
  if (params.status) query.set('status', params.status)
  if (params.date_from) query.set('date_from', params.date_from)
  if (params.date_to) query.set('date_to', params.date_to)

  const queryString = query.toString()
  const url = queryString
    ? `/api/manager/hotels/${hotelId}/bookings/?${queryString}`
    : `/api/manager/hotels/${hotelId}/bookings/`
  return apiClient.get(url)
}

export async function getManagerAvailabilityApi(hotelId, dateFrom, dateTo) {
  const query = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
  })
  return apiClient.get(`/api/manager/hotels/${hotelId}/availability/?${query.toString()}`)
}

// ---------------------------------------------------------------------------
// Discount Codes CRUD
// ---------------------------------------------------------------------------

export async function getManagerDiscountsApi(hotelId) {
  return apiClient.get(`/api/manager/hotels/${hotelId}/discounts/`)
}

export async function createManagerDiscountApi(hotelId, data) {
  return apiClient.post(`/api/manager/hotels/${hotelId}/discounts/`, data)
}

export async function updateManagerDiscountApi(discountId, data) {
  return apiClient.put(`/api/manager/discounts/${discountId}/`, data)
}

export async function deleteManagerDiscountApi(discountId) {
  return apiClient.delete(`/api/manager/discounts/${discountId}/`)
}
