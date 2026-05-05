import { describe, it, expect, vi } from 'vitest'
import { escalationsApi } from '@/lib/api/escalations'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('escalationsApi', () => {
  it('list calls fetchApi', () => {
    escalationsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    escalationsApi.list({ user_id: 123, status: 'open', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    escalationsApi.create({
      user_id: 123,
      type: 'performance',
      source: 'manual',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    escalationsApi.create({
      user_id: 123,
      type: 'performance',
      source: 'manual',
      reason: 'Low performance',
      context: { metrics: 'low' },
      assigned_to: 456,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    escalationsApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PATCH', () => {
    escalationsApi.update(123, { status: 'resolved' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with all fields', () => {
    escalationsApi.update(123, {
      status: 'in_progress',
      assigned_to: 456,
      resolution_note: 'Resolved',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('assign calls fetchApi with POST', () => {
    escalationsApi.assign(123, 456)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('resolve calls fetchApi with POST', () => {
    escalationsApi.resolve(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    escalationsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
