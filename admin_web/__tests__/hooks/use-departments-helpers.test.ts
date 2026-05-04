import { describe, it, expect } from 'vitest'
import { mapDepartment, toCreatePayload, toUpdatePayload, toForm } from '@/hooks/use-departments'
import type { Department } from '@/types/department'
import type { DepartmentRow } from '@/hooks/use-departments'

describe('use-departments helper functions', () => {
  const mockDepartment: Department = {
    id: 1,
    name: 'Engineering',
    description: 'Software engineering department',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-06-01T00:00:00Z',
  }

  describe('mapDepartment', () => {
    it('maps Department to DepartmentRow correctly', () => {
      const result = mapDepartment(mockDepartment)

      expect(result.id).toBe(1)
      expect(result.name).toBe('Engineering')
      expect(result.description).toBe('Software engineering department')
      expect(result.createdAt).toBe('2024-01-01')
    })

    it('handles null description', () => {
      const result = mapDepartment({ ...mockDepartment, description: null })
      expect(result.description).toBe('')
    })

    it('handles null created_at', () => {
      const result = mapDepartment({ ...mockDepartment, created_at: null as any })
      expect(result.createdAt).toBe('')
    })
  })

  describe('toCreatePayload', () => {
    it('maps form data to create payload', () => {
      const formData = { name: 'Engineering', description: 'Software' }
      const result = toCreatePayload(formData)

      expect(result.name).toBe('Engineering')
      expect(result.description).toBe('Software')
    })

    it('converts empty description to null', () => {
      const result = toCreatePayload({ name: 'Engineering', description: '' })
      expect(result.description).toBeNull()
    })
  })

  describe('toUpdatePayload', () => {
    it('behaves same as toCreatePayload', () => {
      const formData = { name: 'Updated', description: 'New desc' }
      expect(toUpdatePayload(formData)).toEqual(toCreatePayload(formData))
    })
  })

  describe('toForm', () => {
    it('maps DepartmentRow to form data', () => {
      const row: DepartmentRow = {
        id: 1,
        name: 'Engineering',
        description: 'Software',
        createdAt: '2024-01-01',
      }
      const result = toForm(row)

      expect(result.name).toBe('Engineering')
      expect(result.description).toBe('Software')
    })
  })
})
