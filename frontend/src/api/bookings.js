import { apiClient } from './client'

/**
 * Request real-time booking price quote and availability.
 * POST /api/bookings/quote/
 * Payload: { room_type, check_in, check_out, rooms_count, guests_count, discount_code? }
 */
export async function getBookingQuoteApi(payload) {
  return apiClient.post('/api/bookings/quote/', payload)
}

/**
 * Validate a discount code for a specific hotel.
 * POST /api/discounts/validate/
 * Payload: { hotel, code }
 */
export async function validateDiscountApi(payload) {
  return apiClient.post('/api/discounts/validate/', payload)
}

/**
 * Create a confirmed room booking reservation.
 * POST /api/bookings/
 * Payload: { room_type, check_in, check_out, rooms_count, guests_count, discount_code? }
 */
export async function createBookingApi(payload) {
  return apiClient.post('/api/bookings/', payload)
}

/**
 * Fetch current authenticated guest's bookings list.
 * GET /api/bookings/mine/
 */
export async function getMyBookingsApi() {
  return apiClient.get('/api/bookings/mine/')
}

/**
 * Cancel a future confirmed booking.
 * POST /api/bookings/{id}/cancel/
 */
export async function cancelBookingApi(bookingId) {
  return apiClient.post(`/api/bookings/${bookingId}/cancel/`)
}
