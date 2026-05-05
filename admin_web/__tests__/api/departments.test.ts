import { describe, it, expect, vi } from 'vitest'
import { departmentsApi } from '@/lib/api/departments'

const mockFetchApi = vi.fn()
const mockBuildQueryString = vi.fn(() => '')

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

vi.mock('@/lib/utils/query-builder', () => ({
  buildQueryString: () => mockBuildQueryString(),
}))

describe('departmentsApi', () => {
  it('list calls fetchApi', () => {
    departmentsApi.list()
    expect(mockBuildQueryString).toHaveBeenCalled()
  })

  it('create calls fetchApi with data', () => {
    departmentsApi.create({ name: 'Test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with id and data', () => {
    departmentsApi.update(123, { name: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with id', () => {
    departmentsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
