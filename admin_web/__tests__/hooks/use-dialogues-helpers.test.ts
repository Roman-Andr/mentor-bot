import { describe, it, expect } from 'vitest'
import { mapDialogue, toPayload, toForm } from '@/hooks/use-dialogues'
import type { DialogueScenario } from '@/types'

describe('use-dialogues helper functions', () => {
  const mockScenario: DialogueScenario = {
    id: 1,
    title: 'Vacation Request',
    description: 'Handle vacation requests',
    keywords: ['vacation', 'leave'],
    category: 'VACATION',
    is_active: true,
    display_order: 1,
    steps: [
      { id: 1, scenario_id: 1, step_number: 1, question: 'Start date?', answer_type: 'TEXT', options: null, answer_content: null, next_step_id: null, parent_step_id: null, is_final: false, created_at: '2024-01-01T00:00:00Z', updated_at: null },
    ],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: null,
  }

  describe('mapDialogue', () => {
    it('maps DialogueScenario to DialogueRow correctly', () => {
      const result = mapDialogue(mockScenario)

      expect(result.id).toBe(1)
      expect(result.title).toBe('Vacation Request')
      expect(result.description).toBe('Handle vacation requests')
      expect(result.keywords).toEqual(['vacation', 'leave'])
      expect(result.category).toBe('VACATION')
      expect(result.isActive).toBe(true)
      expect(result.displayOrder).toBe(1)
      expect(result.stepsCount).toBe(1)
      expect(result.createdAt).toBe('2024-01-01')
    })

    it('handles null description', () => {
      const result = mapDialogue({ ...mockScenario, description: null })
      expect(result.description).toBe('')
    })

    it('handles empty steps array', () => {
      const result = mapDialogue({ ...mockScenario, steps: [] })
      expect(result.stepsCount).toBe(0)
    })

    it('handles null created_at', () => {
      const result = mapDialogue({ ...mockScenario, created_at: null as any })
      expect(result.createdAt).toBe('')
    })
  })

  describe('toPayload', () => {
    it('converts keywords string to array', () => {
      const formData = {
        title: 'Test',
        description: 'desc',
        keywords: 'a, b, c',
        category: 'VACATION' as const,
        is_active: true,
        display_order: 1,
      }
      const result = toPayload(formData)

      expect(result.keywords).toEqual(['a', 'b', 'c'])
      expect(result.title).toBe('Test')
      expect(result.category).toBe('VACATION')
    })

    it('filters empty keywords', () => {
      const formData = {
        title: 'Test',
        description: '',
        keywords: 'a,, , b',
        category: 'VACATION' as const,
        is_active: true,
        display_order: 0,
      }
      const result = toPayload(formData)
      expect(result.keywords).toEqual(['a', 'b'])
      expect(result.description).toBeUndefined()
    })

    it('returns empty keywords array for empty string', () => {
      const formData = {
        title: 'Test',
        description: '',
        keywords: '',
        category: 'VACATION' as const,
        is_active: true,
        display_order: 0,
      }
      const result = toPayload(formData)
      expect(result.keywords).toEqual([])
    })
  })

  describe('toForm', () => {
    it('maps DialogueRow to form data', () => {
      const row = {
        id: 1,
        title: 'Test',
        description: 'desc',
        keywords: ['a', 'b'],
        category: 'VACATION' as const,
        isActive: true,
        displayOrder: 2,
        stepsCount: 3,
        createdAt: '2024-01-01',
      }
      const result = toForm(row)

      expect(result.title).toBe('Test')
      expect(result.keywords).toBe('a, b')
      expect(result.display_order).toBe(2)
      expect(result.is_active).toBe(true)
    })
  })
})
