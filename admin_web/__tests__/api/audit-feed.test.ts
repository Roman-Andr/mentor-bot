import { describe, it, expect, vi } from 'vitest'
import { auditApi } from '@/lib/api/audit-feed'

const mockFetchApi = vi.fn(() => Promise.resolve({
  success: true,
  data: { items: [] },
}))

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('auditApi', () => {
  it('feed calls fetchApi', async () => {
    await auditApi.feed({ page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with from_date', async () => {
    await auditApi.feed({ from_date: '2024-01-01', page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with to_date', async () => {
    await auditApi.feed({ to_date: '2024-12-31', page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with sources', async () => {
    await auditApi.feed({ sources: ['users', 'meetings'], page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with event_types', async () => {
    await auditApi.feed({ event_types: ['create', 'update'], page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with actor_id', async () => {
    await auditApi.feed({ actor_id: 123, page: 1, page_size: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('feed with all params', async () => {
    await auditApi.feed({
      from_date: '2024-01-01',
      to_date: '2024-12-31',
      sources: ['users', 'meetings'],
      event_types: ['create'],
      actor_id: 123,
      page: 1,
      page_size: 10,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('fetchAll calls fetchApi', async () => {
    await auditApi.fetchAll({ from_date: '2024-01-01', to_date: '2024-12-31' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('fetchAll with skip calls fetchApi', async () => {
    await auditApi.fetchAll({ from_date: '2024-01-01', to_date: '2024-12-31' }, 5)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('fetchAll with limit calls fetchApi', async () => {
    await auditApi.fetchAll({ from_date: '2024-01-01', to_date: '2024-12-31' }, 50)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('fetchAll with all params calls fetchApi', async () => {
    await auditApi.fetchAll({ from_date: '2024-01-01', to_date: '2024-12-31' }, 100)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('fetchAll handles empty items', async () => {
    mockFetchApi.mockResolvedValueOnce({
      success: true,
      data: { items: [] },
    })
    const result = await auditApi.fetchAll({ page: 1, page_size: 10 })
    expect(result).toEqual([])
  })

  it('fetchAll handles success false', async () => {
    mockFetchApi.mockResolvedValueOnce({
      success: false,
    })
    const result = await auditApi.fetchAll({ page: 1, page_size: 10 })
    expect(result).toEqual([])
  })

  it('fetchAll handles data null', async () => {
    mockFetchApi.mockResolvedValueOnce({
      success: true,
      data: null,
    })
    const result = await auditApi.fetchAll({ page: 1, page_size: 10 })
    expect(result).toEqual([])
  })
})
