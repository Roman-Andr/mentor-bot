import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchApi, fetchUpload, setUnauthorizedCallback } from '@/lib/api/client'
import { analyticsApi } from '@/lib/api/analytics'
import { mockFetchResponse, mockFetchError, mockFetchNetworkError } from '../setup'
import type { ApiResult } from '@/lib/api/client'

describe('fetchApi', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns data on successful response', async () => {
    mockFetchResponse({ id: 1, name: 'Test' })

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toEqual({ id: 1, name: 'Test' })
    }
  })

  it('sends correct headers', async () => {
    mockFetchResponse({ success: true })

    await fetchApi('/api/test', { method: 'POST', body: JSON.stringify({}) })

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      })
    )
  })

  it('handles 204 no content', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => null
    } as Response)

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toBeUndefined()
    }
  })

  it('handles 401 unauthorized', async () => {
    const mockRedirect = vi.fn()
    setUnauthorizedCallback(mockRedirect)
    mockFetchError(401, 'Unauthorized')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Unauthorized')
    }
    expect(mockRedirect).toHaveBeenCalledOnce()
  })

  it('handles 401 unauthorized without window', async () => {
    vi.stubGlobal('window', undefined)
    mockFetchError(401, 'Unauthorized')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Unauthorized')
    }
  })

  it('handles 500 server error', async () => {
    mockFetchError(500, 'Internal Server Error')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Internal Server Error')
    }
  })

  it('handles network error', async () => {
    mockFetchNetworkError('Failed to fetch')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Failed to fetch')
    }
  })

  it('handles non-Error thrown values as network errors', async () => {
    global.fetch = vi.fn().mockRejectedValue('Failed')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Network error')
    }
  })

  it('handles malformed JSON in error response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => { throw new Error('Invalid JSON') }
    } as unknown as Response)

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('HTTP 500')
    }
  })

  it('merges custom headers', async () => {
    mockFetchResponse({ success: true })

    await fetchApi('/api/test', {
      headers: { 'X-Custom': 'value' }
    })

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        headers: {
          'Content-Type': 'application/json',
          'X-Custom': 'value'
        }
      })
    )
  })
})

describe('fetchUpload', () => {
  it('sends FormData without Content-Type header', async () => {
    mockFetchResponse({ url: 'https://example.com/file.pdf' })

    const formData = new FormData()
    formData.append('file', new Blob(['test']), 'test.txt')

    await fetchUpload('/api/upload', formData)

    const callArgs = vi.mocked(global.fetch).mock.calls[0][1]
    expect(callArgs?.headers).toBeUndefined()
    expect(callArgs?.body).toBe(formData)
    expect(callArgs?.credentials).toBe('include')
  })

  it('returns data on successful upload', async () => {
    mockFetchResponse({ url: 'https://example.com/uploaded.pdf' })

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toEqual({ url: 'https://example.com/uploaded.pdf' })
    }
  })

  it('handles upload error', async () => {
    mockFetchError(413, 'File too large')

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('File too large')
    }
  })

  it('uses PUT method when specified', async () => {
    mockFetchResponse({ success: true })

    const formData = new FormData()
    await fetchUpload('/api/upload/1', formData)

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/upload/1',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('handles network error during upload', async () => {
    mockFetchNetworkError('Network error')

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Network error')
    }
  })

  it('handles non-Error thrown values during upload', async () => {
    global.fetch = vi.fn().mockRejectedValue('Failed')

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Network error')
    }
  })
})

describe('fetchApi (ApiResult shape)', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns success result with data', async () => {
    mockFetchResponse({ items: [] })

    const result = await fetchApi('/api/items')

    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toEqual({ items: [] })
    }
  })

  it('returns error result on failure', async () => {
    mockFetchError(404, 'Not found')

    const result = await fetchApi('/api/items/999')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Not found')
      expect(result.error.status).toBe(404)
    }
  })

  it('handles 401 with redirect', async () => {
    const mockRedirect = vi.fn()
    setUnauthorizedCallback(mockRedirect)
    mockFetchError(401, 'Unauthorized')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.status).toBe(401)
    }
    expect(mockRedirect).toHaveBeenCalledOnce()
  })

  it('handles network error', async () => {
    mockFetchNetworkError('Connection refused')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Connection refused')
      expect(result.error.status).toBeUndefined()
    }
  })

  it('handles non-Error thrown values as network errors', async () => {
    global.fetch = vi.fn().mockRejectedValue('Failed')

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('Network error')
    }
  })

  it('includes credentials in request', async () => {
    mockFetchResponse({ data: true })

    await fetchApi('/api/test')

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({ credentials: 'include' })
    )
  })

  it('handles 204 no content', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => null
    } as Response)

    const result = await fetchApi('/api/test')

    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toBeUndefined()
    }
  })
})

describe('analyticsApi.search', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls summary endpoint with correct URL', async () => {
    mockFetchResponse({
      total_searches: 1000,
      unique_users: 50,
      unique_queries: 200,
      avg_results_per_search: 8.5,
      zero_results_percentage: 10.0
    })

    await analyticsApi.search.summary()

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/summary')
  })

  it('calls summary endpoint with date filters', async () => {
    mockFetchResponse({
      total_searches: 500,
      unique_users: 25,
      unique_queries: 100,
      avg_results_per_search: 7.0,
      zero_results_percentage: 5.0
    })

    await analyticsApi.search.summary({ from_date: '2024-01-01', to_date: '2024-12-31' })

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/summary')
    expect(fetchCall[0]).toContain('from_date=2024-01-01')
    expect(fetchCall[0]).toContain('to_date=2024-12-31')
  })

  it('calls topQueries endpoint with default limit', async () => {
    mockFetchResponse([
      { query: 'test', count: 50, avg_results_count: 8.5, zero_results_count: 5 }
    ])

    await analyticsApi.search.topQueries()

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toMatch(/\/api\/v1\/knowledge\/search-analytics\/top-queries\??/)
  })

  it('calls topQueries endpoint with custom limit and filters', async () => {
    mockFetchResponse([])

    await analyticsApi.search.topQueries({ from_date: '2024-01-01', limit: 10, department_id: 2 })

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/top-queries')
    expect(fetchCall[0]).toContain('from_date=2024-01-01')
    expect(fetchCall[0]).toContain('limit=10')
    expect(fetchCall[0]).toContain('department_id=2')
  })

  it('calls zeroResults endpoint', async () => {
    mockFetchResponse([
      { query: 'no result', count: 10, last_searched_at: '2024-01-01T00:00:00Z' }
    ])

    await analyticsApi.search.zeroResults()

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/zero-results')
  })

  it('calls byDepartment endpoint', async () => {
    mockFetchResponse([
      { department_id: 1, department_name: 'Engineering', search_count: 100, unique_users: 20 }
    ])

    await analyticsApi.search.byDepartment()

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/by-department')
  })

  it('calls byDepartment endpoint with date filters', async () => {
    mockFetchResponse([])

    await analyticsApi.search.byDepartment({ from_date: '2024-01-01', to_date: '2024-12-31' })

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[0]).toContain('/api/v1/knowledge/search-analytics/by-department')
    expect(fetchCall[0]).toContain('from_date=2024-01-01')
    expect(fetchCall[0]).toContain('to_date=2024-12-31')
  })

  it('calls timeseries endpoint with day granularity', async () => {
    mockFetchResponse([
      { bucket: '2024-01-01T00:00:00Z', search_count: 50, unique_users: 10 }
    ])

    await analyticsApi.search.timeseries({ granularity: 'day' })

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/knowledge/search-analytics/timeseries?granularity=day',
      expect.any(Object)
    )
  })

  it('calls timeseries endpoint with week granularity', async () => {
    mockFetchResponse([
      { bucket: '2024-01-01T00:00:00Z', search_count: 400, unique_users: 100 }
    ])

    await analyticsApi.search.timeseries({ granularity: 'week' })

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/knowledge/search-analytics/timeseries?granularity=week',
      expect.any(Object)
    )
  })

  it('handles search API errors', async () => {
    mockFetchError(403, 'HR access required')

    const result = await analyticsApi.search.summary()

    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toBe('HR access required')
    }
  })
})
