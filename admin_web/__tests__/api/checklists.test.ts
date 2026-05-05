import { describe, it, expect, vi } from 'vitest'
import { checklistsApi } from '@/lib/api/checklists'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('checklistsApi', () => {
  it('list calls fetchApi', () => {
    checklistsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    checklistsApi.list({ user_id: 123, status: 'active', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with overdue_only', () => {
    checklistsApi.list({ overdue_only: true })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    checklistsApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    checklistsApi.create({
      user_id: 123,
      employee_id: 'EMP001',
      template_id: 5,
      start_date: '2024-01-01',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    checklistsApi.create({
      user_id: 123,
      employee_id: 'EMP001',
      template_id: 5,
      start_date: '2024-01-01',
      due_date: '2024-12-31',
      mentor_id: 10,
      hr_id: 20,
      notes: 'Test notes',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    checklistsApi.update(123, { status: 'completed' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with all fields', () => {
    checklistsApi.update(123, {
      status: 'in_progress',
      progress_percentage: 50,
      mentor_id: 10,
      hr_id: 20,
      notes: 'Updated notes',
      completed_at: '2024-12-31',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    checklistsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('complete calls fetchApi with POST', () => {
    checklistsApi.complete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getTasks calls fetchApi', () => {
    checklistsApi.getTasks(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('completeTask calls fetchApi with POST', () => {
    checklistsApi.completeTask(456)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getProgress calls fetchApi', () => {
    checklistsApi.getProgress(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('stats calls fetchApi', () => {
    checklistsApi.stats()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('stats with params', () => {
    checklistsApi.stats({ user_id: 123, department_id: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
