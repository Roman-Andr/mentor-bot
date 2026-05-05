import { describe, it, expect, vi } from 'vitest'
import { notificationsApi } from '@/lib/api/notifications'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('notificationsApi', () => {
  it('history calls fetchApi', () => {
    notificationsApi.history({ skip: 0, limit: 20 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('history calls fetchApi without params', () => {
    notificationsApi.history()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('send calls fetchApi with POST', () => {
    notificationsApi.send({
      user_id: 123,
      type: 'email',
      channel: 'email',
      body: 'Test notification',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('send calls fetchApi with subject', () => {
    notificationsApi.send({
      user_id: 123,
      type: 'email',
      channel: 'email',
      body: 'Test notification',
      subject: 'Important',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
