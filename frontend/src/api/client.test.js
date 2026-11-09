import test, { describe, beforeEach, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { ApiError, apiRequest, apiClient, getCookie, setCookie, ensureCsrfToken } from './client.js'

describe('ApiError class', () => {
  test('constructs correctly with message, status, and errors dictionary', () => {
    const error = new ApiError('Validation failed', 400, { email: ['Email already taken'] })
    assert.equal(error.name, 'ApiError')
    assert.equal(error.message, 'Validation failed')
    assert.equal(error.status, 400)
    assert.deepEqual(error.errors, { email: ['Email already taken'] })
    assert.ok(error instanceof Error)
  })

  test('defaults status to 500 and errors to empty object', () => {
    const error = new ApiError('Internal crash')
    assert.equal(error.status, 500)
    assert.deepEqual(error.errors, {})
  })
})

describe('Cookie helpers', () => {
  const originalDocument = globalThis.document

  afterEach(() => {
    globalThis.document = originalDocument
  })

  test('returns null when document is undefined', () => {
    delete globalThis.document
    assert.equal(getCookie('csrftoken'), null)
    // setCookie should be a no-op without crashing
    assert.doesNotThrow(() => setCookie('csrftoken', 'abc'))
  })

  test('extracts cookie value correctly', () => {
    globalThis.document = { cookie: 'theme=dark; csrftoken=secretToken456; last_city=Isfahan' }
    assert.equal(getCookie('csrftoken'), 'secretToken456')
    assert.equal(getCookie('last_city'), 'Isfahan')
    assert.equal(getCookie('nonexistent'), null)
  })

  test('sets cookie with encoded value and attributes', () => {
    globalThis.document = { cookie: '' }
    setCookie('last_city', 'تهران', 7)
    assert.ok(globalThis.document.cookie.includes('last_city=%D8%AA%D9%87%D8%B1%D8%A7%D9%86'))
    assert.ok(globalThis.document.cookie.includes('SameSite=Lax'))
    assert.ok(globalThis.document.cookie.includes('path=/'))
  })

  test('ensureCsrfToken fetches token from endpoint if cookie is absent', async () => {
    globalThis.document = { cookie: '' }
    let fetchCalled = false
    globalThis.fetch = async (url) => {
      fetchCalled = true
      assert.equal(url, '/api/auth/csrf/')
      globalThis.document.cookie = 'csrftoken=fetched-token-777'
      return new Response(JSON.stringify({ data: { message: 'ok' } }), { status: 200 })
    }

    const token = await ensureCsrfToken()
    assert.equal(fetchCalled, true)
    assert.equal(token, 'fetched-token-777')
  })
})

describe('apiRequest & apiClient error normalisation smoke suite', () => {
  const originalFetch = globalThis.fetch
  const originalDocument = globalThis.document

  beforeEach(() => {
    globalThis.document = { cookie: 'csrftoken=valid-csrf-token' }
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
    globalThis.document = originalDocument
  })

  test('normalises network connection errors to status 0 and Persian message', async () => {
    globalThis.fetch = async () => {
      throw new TypeError('Failed to fetch')
    }

    await assert.rejects(
      async () => {
        await apiRequest('/api/hotels/')
      },
      (err) => {
        assert.ok(err instanceof ApiError)
        assert.equal(err.status, 0)
        assert.ok(err.message.includes('خطا در برقراری ارتباط با سرور'))
        assert.deepEqual(err.errors, { network: ['Failed to fetch'] })
        return true
      }
    )
  })

  test('normalises 400 validation error with backend field messages', async () => {
    const errorPayload = {
      message: 'اعتبارسنجی داده‌ها ناموفق بود.',
      errors: {
        check_out: ['تاریخ خروج باید بعد از تاریخ ورود باشد.'],
        rooms_count: ['تعداد اتاق درخواستی موجود نیست.'],
      },
    }

    globalThis.fetch = async () => {
      return new Response(JSON.stringify(errorPayload), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    await assert.rejects(
      async () => {
        await apiRequest('/api/bookings/', { method: 'POST', body: {} })
      },
      (err) => {
        assert.ok(err instanceof ApiError)
        assert.equal(err.status, 400)
        assert.equal(err.message, 'اعتبارسنجی داده‌ها ناموفق بود.')
        assert.deepEqual(err.errors, errorPayload.errors)
        return true
      }
    )
  })

  test('provides Persian fallback message for 401 Unauthorized', async () => {
    globalThis.fetch = async () => {
      return new Response('Unauthorized', { status: 401 })
    }

    await assert.rejects(
      async () => {
        await apiRequest('/api/bookings/mine/')
      },
      (err) => {
        assert.ok(err instanceof ApiError)
        assert.equal(err.status, 401)
        assert.equal(err.message, 'لطفاً ابتدا وارد سیستم شوید.')
        return true
      }
    )
  })

  test('provides Persian fallback message for 403 Forbidden', async () => {
    globalThis.fetch = async () => {
      return new Response('Forbidden', { status: 403 })
    }

    await assert.rejects(
      async () => {
        await apiRequest('/api/manager/hotels/')
      },
      (err) => {
        assert.ok(err instanceof ApiError)
        assert.equal(err.status, 403)
        assert.equal(err.message, 'شما دسترسی لازم برای این عملیات را ندارید.')
        return true
      }
    )
  })

  test('provides Persian fallback message for 404 Not Found', async () => {
    globalThis.fetch = async () => {
      return new Response('Not Found', { status: 404 })
    }

    await assert.rejects(
      async () => {
        await apiRequest('/api/hotels/99999/')
      },
      (err) => {
        assert.ok(err instanceof ApiError)
        assert.equal(err.status, 404)
        assert.equal(err.message, 'منبع درخواستی یافت نشد.')
        return true
      }
    )
  })

  test('unpacks { data: ... } on success', async () => {
    const payload = {
      data: [
        { id: 1, name: 'هتل عباسی' },
        { id: 2, name: 'هتل کوثر' },
      ],
    }

    globalThis.fetch = async () => {
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const data = await apiRequest('/api/hotels/')
    assert.deepEqual(data, payload.data)
  })

  test('returns null for HTTP 204 No Content', async () => {
    globalThis.fetch = async () => {
      return new Response(null, { status: 204 })
    }

    const result = await apiRequest('/api/auth/logout/', { method: 'POST' })
    assert.equal(result, null)
  })

  test('apiClient convenience methods forward HTTP verbs and JSON serialization', async () => {
    let captured = null

    globalThis.fetch = async (url, config) => {
      captured = { url, config }
      return new Response(JSON.stringify({ data: { success: true } }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    await apiClient.get('/api/cities/')
    assert.equal(captured.config.method, 'GET')

    await apiClient.post('/api/bookings/quote/', { rooms: 2 })
    assert.equal(captured.config.method, 'POST')
    assert.equal(captured.config.headers['X-CSRFToken'], 'valid-csrf-token')
    assert.equal(captured.config.headers['Content-Type'], 'application/json')
    assert.equal(captured.config.body, JSON.stringify({ rooms: 2 }))

    await apiClient.put('/api/manager/hotels/1/', { name: 'Updated' })
    assert.equal(captured.config.method, 'PUT')

    await apiClient.patch('/api/manager/hotels/1/', { is_active: true })
    assert.equal(captured.config.method, 'PATCH')

    await apiClient.delete('/api/manager/hotels/1/')
    assert.equal(captured.config.method, 'DELETE')
  })
})
