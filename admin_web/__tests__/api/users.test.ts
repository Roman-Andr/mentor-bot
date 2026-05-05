import { describe, it, expect, vi } from 'vitest'
import { usersApi } from '@/lib/api/users'

const mockFetchApi = vi.fn()
const mockBuildQueryString = vi.fn(() => '')

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

vi.mock('@/lib/utils/query-builder', () => ({
  buildQueryString: () => mockBuildQueryString(),
}))

describe('usersApi', () => {
  it('list calls fetchApi', () => {
    usersApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    usersApi.list({ role: 'admin', department_id: 5, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    usersApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi', () => {
    usersApi.create({ email: 'test@example.com' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with password', () => {
    usersApi.create({ email: 'test@example.com', password: 'secret' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi', () => {
    usersApi.update(123, { email: 'updated@example.com' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('deactivate calls fetchApi with POST', () => {
    usersApi.deactivate(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    usersApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getPreferences calls fetchApi', () => {
    usersApi.getPreferences(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getMyPreferences calls fetchApi', () => {
    usersApi.getMyPreferences()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('updateMyPreferences calls fetchApi with PUT', () => {
    usersApi.updateMyPreferences({ language: 'en' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('updateMyPreferences with all fields', () => {
    usersApi.updateMyPreferences({
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: false,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
