import { describe, it, expect, vi } from 'vitest'
import { articlesApi, categoriesApi } from '@/lib/api/articles'

const mockFetchApi = vi.fn()
const mockFetchUpload = vi.fn()
const mockBuildQueryString = vi.fn(() => '')

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
  fetchUpload: () => mockFetchUpload(),
}))

vi.mock('@/lib/utils/query-builder', () => ({
  buildQueryString: () => mockBuildQueryString(),
}))

describe('articlesApi additional', () => {
  it('publish calls fetchApi', () => {
    articlesApi.publish(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})

describe('categoriesApi', () => {
  it('list calls fetchApi', () => {
    categoriesApi.list()
    expect(mockBuildQueryString).toHaveBeenCalled()
  })

  it('list with params', () => {
    categoriesApi.list({ skip: 0, limit: 10, parent_id: 5 })
    expect(mockBuildQueryString).toHaveBeenCalled()
  })

  it('create calls fetchApi', () => {
    categoriesApi.create({ name: 'Test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi', () => {
    categoriesApi.update(123, { name: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    categoriesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
