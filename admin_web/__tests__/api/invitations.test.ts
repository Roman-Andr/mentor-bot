import { describe, it, expect, vi } from 'vitest'
import { invitationsApi } from '@/lib/api/invitations'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('invitationsApi', () => {
  it('list calls fetchApi', () => {
    invitationsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with skip only', () => {
    invitationsApi.list({ skip: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with limit only', () => {
    invitationsApi.list({ limit: 20 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with skip and limit', () => {
    invitationsApi.list({ skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with status', () => {
    invitationsApi.list({ status: 'pending' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with role', () => {
    invitationsApi.list({ role: 'mentor' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with email', () => {
    invitationsApi.list({ email: 'test@example.com' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with department_id', () => {
    invitationsApi.list({ department_id: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with expired_only', () => {
    invitationsApi.list({ expired_only: true })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with all params', () => {
    invitationsApi.list({
      status: 'pending',
      role: 'mentor',
      email: 'test@example.com',
      department_id: 5,
      expired_only: false,
      skip: 0,
      limit: 10,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with minimal data calls fetchApi', () => {
    invitationsApi.create({ email: 'test@example.com', role: 'admin' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with role', () => {
    invitationsApi.create({ email: 'test@example.com', role: 'mentor' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with admin role', () => {
    invitationsApi.create({ email: 'test@example.com', role: 'admin' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with department_id', () => {
    invitationsApi.create({ email: 'test@example.com', role: 'admin', department_id: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    invitationsApi.create({
      email: 'test@example.com',
      role: 'admin',
      employee_id: 'EMP123',
      department_id: 5,
      position: 'manager',
      level: 'senior',
      mentor_id: 10,
      expires_in_days: 30,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('resend calls fetchApi', () => {
    invitationsApi.resend(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('revoke calls fetchApi', () => {
    invitationsApi.revoke(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    invitationsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
