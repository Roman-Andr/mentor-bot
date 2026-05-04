import { describe, it, expect } from 'vitest'
import { mapTemplateToItem, toCreatePayload, toUpdatePayload, toForm } from '@/hooks/use-templates'

describe('use-templates helper functions', () => {
  const mockTemplateData = {
    id: 1,
    name: 'Onboarding',
    description: 'Standard onboarding',
    department_id: 2,
    department: { id: 2, name: 'Engineering' },
    position: 'Developer',
    duration_days: 30,
    status: 'ACTIVE',
    is_default: true,
    task_categories: [],
    task_count: 5,
  }

  const departments = [{ id: 2, name: 'Engineering' }]

  describe('mapTemplateToItem', () => {
    it('maps template data correctly with department', () => {
      const result = mapTemplateToItem(mockTemplateData, departments)

      expect(result.id).toBe(1)
      expect(result.name).toBe('Onboarding')
      expect(result.department_id).toBe(2)
      expect(result.department).toBe('Engineering')
      expect(result.position).toBe('Developer')
      expect(result.durationDays).toBe(30)
      expect(result.status).toBe('ACTIVE')
      expect(result.isDefault).toBe(true)
      expect(result.taskCount).toBe(5)
    })

    it('falls back to department object name when not in map', () => {
      const result = mapTemplateToItem(mockTemplateData, [])
      expect(result.department).toBe('Engineering')
    })

    it('uses empty string when no department info', () => {
      const data = { ...mockTemplateData, department: null, department_id: null }
      const result = mapTemplateToItem(data, [])
      expect(result.department).toBe('')
    })

    it('defaults position to empty string when null', () => {
      const data = { ...mockTemplateData, position: null }
      const result = mapTemplateToItem(data, departments)
      expect(result.position).toBe('')
    })
  })

  describe('toCreatePayload', () => {
    it('maps form data correctly', () => {
      const formData = {
        name: 'Test',
        description: 'desc',
        department_id: 2,
        position: 'Dev',
        duration_days: 14,
        status: 'DRAFT' as const,
        is_default: false,
      }
      const result = toCreatePayload(formData)

      expect(result.name).toBe('Test')
      expect(result.department_id).toBe(2)
      expect(result.duration_days).toBe(14)
      expect(result.status).toBe('DRAFT')
      expect(result.task_categories).toEqual([])
    })

    it('converts empty department_id to null', () => {
      const formData = {
        name: 'Test',
        description: '',
        department_id: 0,
        position: '',
        duration_days: 30,
        status: 'DRAFT' as const,
        is_default: false,
      }
      const result = toCreatePayload(formData)
      expect(result.department_id).toBeNull()
      expect(result.position).toBeNull()
    })
  })

  describe('toUpdatePayload', () => {
    it('maps form data correctly', () => {
      const formData = {
        name: 'Updated',
        description: 'new desc',
        department_id: 0,
        position: '',
        duration_days: 30,
        status: 'ACTIVE' as const,
        is_default: true,
      }
      const result = toUpdatePayload(formData)

      expect(result.name).toBe('Updated')
      expect(result.is_default).toBe(true)
      expect(result.status).toBe('ACTIVE')
    })
  })

  describe('toForm', () => {
    it('maps TemplateItem to form data', () => {
      const item = {
        id: 1,
        name: 'Test',
        description: 'desc',
        department_id: 2,
        department: 'Eng',
        position: 'Dev',
        durationDays: 14,
        taskCount: 3,
        status: 'ACTIVE' as const,
        isDefault: false,
      }
      const result = toForm(item)

      expect(result.name).toBe('Test')
      expect(result.department_id).toBe(2)
      expect(result.duration_days).toBe(14)
      expect(result.is_default).toBe(false)
    })

    it('handles null department_id', () => {
      const item = {
        id: 1,
        name: 'Test',
        description: '',
        department_id: null,
        department: '',
        position: '',
        durationDays: 30,
        taskCount: 0,
        status: 'DRAFT' as const,
        isDefault: false,
      }
      const result = toForm(item)
      expect(result.department_id).toBe(0)
    })
  })
})
