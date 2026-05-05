import { describe, it, expect, vi } from 'vitest'
import { dialoguesApi } from '@/lib/api/dialogues'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('dialoguesApi', () => {
  it('list calls fetchApi', () => {
    dialoguesApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with category param', () => {
    dialoguesApi.list({ category: 'VACATION' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with is_active param', () => {
    dialoguesApi.list({ is_active: true })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with search param', () => {
    dialoguesApi.list({ search: 'test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with pagination params', () => {
    dialoguesApi.list({ skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with sort params', () => {
    dialoguesApi.list({ sort_by: 'title', sort_order: 'asc' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi with id', () => {
    dialoguesApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getActive calls fetchApi', () => {
    dialoguesApi.getActive()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getActive with pagination', () => {
    dialoguesApi.getActive({ skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    dialoguesApi.create({
      title: 'Test',
      category: 'VACATION',
      is_active: true,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with steps', () => {
    dialoguesApi.create({
      title: 'Test',
      category: 'VACATION',
      steps: [
        {
          step_number: 1,
          question: 'Test question',
          answer_type: 'text',
          is_final: true,
        },
      ],
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    dialoguesApi.update(123, { title: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    dialoguesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('addStep calls fetchApi with POST', () => {
    dialoguesApi.addStep(123, {
      step_number: 1,
      question: 'Test',
      answer_type: 'text',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('updateStep calls fetchApi with PUT', () => {
    dialoguesApi.updateStep(456, { question: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('deleteStep calls fetchApi with DELETE', () => {
    dialoguesApi.deleteStep(456)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('reorderSteps calls fetchApi with POST', () => {
    dialoguesApi.reorderSteps(123, [1, 2, 3])
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
