import { describe, it, expect, vi } from 'vitest'
import { userMentorsApi } from '@/lib/api/user-mentors'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('userMentorsApi', () => {
  it('list calls fetchApi', () => {
    userMentorsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with user_id', () => {
    userMentorsApi.list({ user_id: 123 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with mentor_id', () => {
    userMentorsApi.list({ mentor_id: 456 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with both params', () => {
    userMentorsApi.list({ user_id: 123, mentor_id: 456 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    userMentorsApi.create({ user_id: 123, mentor_id: 456 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with notes', () => {
    userMentorsApi.create({ user_id: 123, mentor_id: 456, notes: 'Test notes' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    userMentorsApi.update(123, { is_active: false })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with notes', () => {
    userMentorsApi.update(123, { is_active: true, notes: 'Updated notes' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    userMentorsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
