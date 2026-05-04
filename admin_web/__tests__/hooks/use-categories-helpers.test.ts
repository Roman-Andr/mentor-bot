import { describe, it, expect } from 'vitest'
import { mapCategory, toCreatePayload, toUpdatePayload, toForm } from '@/hooks/use-categories'
import type { Category } from '@/types'

describe('use-categories helper functions', () => {
  const mockCategory: Category = {
    id: 1,
    name: 'Onboarding',
    slug: 'onboarding',
    description: 'New employee onboarding guides',
    parent_id: null,
    parent_name: null,
    order: 1,
    department_id: 2,
    department: { id: 2, name: 'Engineering', description: null, created_at: '2024-01-01T00:00:00Z', updated_at: null },
    position: 'Developer',
    level: 'MIDDLE',
    icon: 'book',
    color: '#3B82F6',
    children_count: 3,
    articles_count: 10,
    article_count: 10,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: null,
  }

  const departmentsMap: Record<number, string> = { 2: 'Engineering' }

  describe('mapCategory', () => {
    it('maps Category to CategoryRow correctly with all fields', () => {
      const result = mapCategory(mockCategory, departmentsMap)

      expect(result.id).toBe(1)
      expect(result.name).toBe('Onboarding')
      expect(result.slug).toBe('onboarding')
      expect(result.description).toBe('New employee onboarding guides')
      expect(result.department).toBe('Engineering')
      expect(result.department_id).toBe(2)
      expect(result.parent_name).toBe('')
      expect(result.children_count).toBe(3)
      expect(result.articles_count).toBe(10)
      expect(result.createdAt).toBe('2024-01-01')
    })

    it('maps department_id to empty string when not in departmentsMap', () => {
      const result = mapCategory({ ...mockCategory, department_id: 999 }, departmentsMap)
      expect(result.department).toBe('')
    })

    it('handles null parent_id and department_id', () => {
      const result = mapCategory(
        { ...mockCategory, parent_id: null, department_id: null },
        departmentsMap
      )
      expect(result.department).toBe('')
      expect(result.department_id).toBeNull()
    })

    it('uses default values for optional fields', () => {
      const minimalCategory: Category = {
        ...mockCategory,
        description: null,
        position: null,
        level: null,
        icon: null,
        color: null,
        created_at: '2024-01-01T00:00:00Z',
      }
      const result = mapCategory(minimalCategory, departmentsMap)

      expect(result.description).toBe('')
      expect(result.position).toBe('')
      expect(result.level).toBe('')
      expect(result.icon).toBe('')
      expect(result.color).toBe('')
      expect(result.createdAt).toBe('2024-01-01')
    })
  })

  describe('toCreatePayload', () => {
    it('generates slug from name when empty', () => {
      const formData = {
        name: 'Test Category',
        slug: '',
        description: 'desc',
        parent_id: 0,
        order: 1,
        department_id: 2,
        position: 'Developer',
        level: 'MIDDLE',
        icon: 'icon',
        color: '#000',
      }
      const result = toCreatePayload(formData)
      expect(result.slug).toBe('test-category')
    })

    it('uses provided slug when not empty', () => {
      const formData = {
        name: 'Test',
        slug: 'custom-slug',
        description: '',
        parent_id: 0,
        order: 1,
        department_id: 0,
        position: '',
        level: '',
        icon: '',
        color: '',
      }
      const result = toCreatePayload(formData)
      expect(result.slug).toBe('custom-slug')
      expect(result.description).toBeNull()
      expect(result.parent_id).toBeNull()
      expect(result.department_id).toBeNull()
      expect(result.position).toBeNull()
    })
  })

  describe('toUpdatePayload', () => {
    it('converts empty fields to null', () => {
      const formData = {
        name: 'Updated',
        slug: 'updated',
        description: '',
        parent_id: 0,
        order: 2,
        department_id: 0,
        position: '',
        level: '',
        icon: '',
        color: '',
      }
      const result = toUpdatePayload(formData)
      expect(result.name).toBe('Updated')
      expect(result.description).toBeNull()
      expect(result.parent_id).toBeNull()
      expect(result.department_id).toBeNull()
    })
  })

  describe('toForm', () => {
    it('maps CategoryRow to form data correctly', () => {
      const row = {
        id: 1,
        name: 'Test',
        slug: 'test',
        description: 'desc',
        parent_id: 0,
        order: 1,
        department_id: 2,
        department: 'Eng',
        position: 'Dev',
        level: 'MID',
        icon: 'icon',
        color: '#000',
        parent_name: '',
        children_count: 0,
        articles_count: 0,
        createdAt: '2024-01-01',
      }
      const result = toForm(row)

      expect(result.name).toBe('Test')
      expect(result.parent_id).toBe(0)
      expect(result.department_id).toBe(2)
    })

    it('handles null parent_id and department_id', () => {
      const row = {
        id: 1,
        name: 'Test',
        slug: 'test',
        description: '',
        parent_id: null,
        parent_name: '',
        order: 0,
        department_id: null,
        department: '',
        position: '',
        level: '',
        icon: '',
        color: '',
        children_count: 0,
        articles_count: 0,
        createdAt: '',
      }
      const result = toForm(row)
      expect(result.parent_id).toBe(0)
      expect(result.department_id).toBe(0)
    })
  })
})
