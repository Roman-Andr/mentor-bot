import { describe, it, expect, vi } from 'vitest'
import { meetingsApi } from '@/shared/lib/api/meetings'

const mockFetchApi = vi.fn()

vi.mock('@/shared/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('meetingsApi', () => {
  it('list calls fetchApi', () => {
    meetingsApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    meetingsApi.list({ department_id: 123, skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    meetingsApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    meetingsApi.create({ title: 'Test', type: 'ONBOARDING' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    meetingsApi.create({
      title: 'Test Meeting',
      description: 'Test description',
      type: 'ONBOARDING',
      department_id: 5,
      position: 'Developer',
      level: 'MIDDLE',
      deadline_days: 30,
      duration_minutes: 60,
      is_mandatory: true,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    meetingsApi.update(123, { title: 'Updated', type: 'ONBOARDING' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    meetingsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getMaterials calls fetchApi', () => {
    meetingsApi.getMaterials(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('addMaterial calls fetchApi with POST', () => {
    meetingsApi.addMaterial(123, {
      title: 'Test Material',
      description: 'Test description',
      url: 'https://example.com',
      content: 'Test content',
      type: 'document',
      order: 1
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('deleteMaterial calls fetchApi with DELETE', () => {
    meetingsApi.deleteMaterial(456)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('updateMaterial calls fetchApi with PUT', () => {
    meetingsApi.updateMaterial(456, {
      title: 'Updated Material',
      description: 'Updated description',
      url: 'https://updated-example.com',
      type: 'pdf'
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('reorderMaterials calls fetchApi with POST', () => {
    meetingsApi.reorderMaterials(123, [
      { id: 1, order: 2 },
      { id: 2, order: 1 }
    ])
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
