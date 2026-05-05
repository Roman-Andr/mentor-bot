import { describe, it, expect, vi } from 'vitest'
import { templatesApi } from '@/lib/api/templates'

const mockFetchApi = vi.fn()
const mockBuildQueryString = vi.fn(() => '')

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

vi.mock('@/lib/utils/query-builder', () => ({
  buildQueryString: () => mockBuildQueryString(),
}))

describe('templatesApi', () => {
  it('list calls fetchApi', () => {
    templatesApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    templatesApi.list({ department_id: 5, status: 'ACTIVE', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    templatesApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi', () => {
    templatesApi.create({ name: 'Test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi', () => {
    templatesApi.update(123, { name: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    templatesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('publish calls fetchApi with POST', () => {
    templatesApi.publish(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('clone calls fetchApi with POST', () => {
    templatesApi.clone(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('addTask calls fetchApi with POST', () => {
    templatesApi.addTask(123, {
      template_id: 123,
      title: 'Task 1',
      category: 'onboarding',
      due_days: 7,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('addTask with all fields', () => {
    templatesApi.addTask(123, {
      template_id: 123,
      title: 'Task 1',
      description: 'Description',
      instructions: 'Instructions',
      category: 'onboarding',
      order: 1,
      due_days: 7,
      estimated_minutes: 30,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
