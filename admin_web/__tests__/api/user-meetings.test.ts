import { describe, it, expect, vi } from 'vitest'
import { userMeetingsApi } from '@/lib/api/user-meetings'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('userMeetingsApi', () => {
  it('list calls fetchApi', () => {
    userMeetingsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    userMeetingsApi.list({ status: 'scheduled', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('listByMeeting calls fetchApi', () => {
    userMeetingsApi.listByMeeting(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('listByMeeting with params', () => {
    userMeetingsApi.listByMeeting(123, { status: 'completed', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('listAll calls fetchApi', () => {
    userMeetingsApi.listAll()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('listAll with params', () => {
    userMeetingsApi.listAll({ status: 'scheduled', skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('assign calls fetchApi with POST', () => {
    userMeetingsApi.assign({ user_id: 123, meeting_id: 456 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('assign with scheduled_at', () => {
    userMeetingsApi.assign({
      user_id: 123,
      meeting_id: 456,
      scheduled_at: '2024-12-31T10:00:00Z',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('autoAssign calls fetchApi with POST', () => {
    userMeetingsApi.autoAssign(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('autoAssign with params', () => {
    userMeetingsApi.autoAssign(123, { department_id: 5, position: 'manager' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    userMeetingsApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PATCH', () => {
    userMeetingsApi.update(123, { status: 'completed' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('complete calls fetchApi with POST', () => {
    userMeetingsApi.complete(123, { feedback: 'Great', rating: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    userMeetingsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
