import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchApi, fetchUpload, fetchApiNew } from '@/lib/api/client'
import { mockFetchResponse, mockFetchError, mockFetchNetworkError } from '../setup'

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

    expect(result.data).toEqual({ id: 1, name: 'Test' })
    expect(result.error).toBeUndefined()
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

    expect(result.data).toBeUndefined()
    expect(result.error).toBeUndefined()
  })

  it('handles 401 unauthorized', async () => {
    mockFetchError(401, 'Unauthorized')

    const result = await fetchApi('/api/test')

    expect(result.error).toBe('Unauthorized')
    expect(window.location.href).toBe('/login')
  })

  it('handles 500 server error', async () => {
    mockFetchError(500, 'Internal Server Error')

    const result = await fetchApi('/api/test')

    expect(result.error).toBe('Internal Server Error')
  })

  it('handles network error', async () => {
    mockFetchNetworkError('Failed to fetch')

    const result = await fetchApi('/api/test')

    expect(result.error).toBe('Failed to fetch')
  })

  it('handles malformed JSON in error response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => { throw new Error('Invalid JSON') }
    } as Response)

    const result = await fetchApi('/api/test')

    expect(result.error).toBe('HTTP 500')
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

    expect(result.data).toEqual({ url: 'https://example.com/uploaded.pdf' })
  })

  it('handles upload error', async () => {
    mockFetchError(413, 'File too large')

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.error).toBe('File too large')
  })

  it('uses PUT method when specified', async () => {
    mockFetchResponse({ success: true })

    const formData = new FormData()
    await fetchUpload('/api/upload/1', formData, 'PUT')

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/upload/1',
      expect.objectContaining({ method: 'PUT' })
    )
  })

  it('handles network error during upload', async () => {
    mockFetchNetworkError('Network error')

    const formData = new FormData()
    const result = await fetchUpload('/api/upload', formData)

    expect(result.error).toBe('Network error')
  })
})

describe('fetchApiNew', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns success result with data', async () => {
    mockFetchResponse({ items: [] })

    const result = await fetchApiNew('/api/items')

    expect(result.success).toBe(true)
    expect(result.data).toEqual({ items: [] })
  })

  it('returns error result on failure', async () => {
    mockFetchError(404, 'Not found')

    const result = await fetchApiNew('/api/items/999')

    expect(result.success).toBe(false)
    expect(result.error.message).toBe('Not found')
    expect(result.error.status).toBe(404)
  })

  it('handles 401 with redirect', async () => {
    mockFetchError(401, 'Unauthorized')

    const result = await fetchApiNew('/api/protected')

    expect(result.success).toBe(false)
    expect(result.error.status).toBe(401)
    expect(window.location.href).toBe('/login')
  })

  it('handles network error', async () => {
    mockFetchNetworkError('Connection refused')

    const result = await fetchApiNew('/api/test')

    expect(result.success).toBe(false)
    expect(result.error.message).toBe('Connection refused')
    expect(result.error.status).toBeUndefined()
  })

  it('includes credentials in request', async () => {
    mockFetchResponse({ data: true })

    await fetchApiNew('/api/test')

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

    const result = await fetchApiNew('/api/test')

    expect(result.success).toBe(true)
    expect(result.data).toBeUndefined()
  })
})
