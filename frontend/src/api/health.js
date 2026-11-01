import { apiClient } from './client'

/**
 * Check backend health status via GET /api/health/
 * @returns {Promise<{status: string}>}
 */
export async function getHealth() {
  return apiClient.get('/api/health/')
}
