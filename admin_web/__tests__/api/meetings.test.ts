import { describe, it, expect, vi } from 'vitest'
import { meetingsApi } from '@/lib/api/meetings'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('meetingsApi', () => {
  it('list calls fetchApi', () => {
    meetingsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    meetingsApi.list({ mentor_id: 123, skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    meetingsApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    meetingsApi.create({ title: 'Test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    meetingsApi.create({
      title: 'Test Meeting',
      scheduled_at: '2024-12-31T10:00:00Z',
      mentor_id: 123,
      mentee_id: 456,
      notes: 'Test notes',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    meetingsApi.update(123, { title: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    meetingsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
