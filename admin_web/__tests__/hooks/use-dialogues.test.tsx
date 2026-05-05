import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NextIntlClientProvider } from 'next-intl'
import { ToastProvider } from '@/components/ui/toast'
import { PaginationContext } from '@/components/providers/pagination-provider'
import { useDialogues, mapDialogue, toPayload, toForm, type DialogueRow, type DialogueFormData } from '@/hooks/use-dialogues'
import { mockFetchResponse } from '../setup'

const MockPaginationProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <PaginationContext.Provider value={{ pageSize: 20, setPageSize: vi.fn() }}>
      {children}
    </PaginationContext.Provider>
  )
}

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <NextIntlClientProvider locale="en">
      <MockPaginationProvider>
        <ToastProvider>
          <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </ToastProvider>
      </MockPaginationProvider>
    </NextIntlClientProvider>
  )
}

describe('useDialogues', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exports useDialogues function', () => {
    expect(typeof useDialogues).toBe('function')
  })

  describe('mapDialogue', () => {
    it('maps DialogueScenario to DialogueRow', () => {
      const scenario = {
        id: 1,
        title: 'Test Dialogue',
        description: 'Test description',
        keywords: ['test', 'dialogue'],
        category: 'VACATION' as const,
        is_active: true,
        display_order: 0,
        steps: [
          { id: 1, step_number: 1, question: 'Question 1', answer_type: 'text' as const, options: null, answer_content: null, is_final: false },
          { id: 2, step_number: 2, question: 'Question 2', answer_type: 'text' as const, options: null, answer_content: null, is_final: true },
        ],
        created_at: '2024-01-01T00:00:00Z',
      }

      const result = mapDialogue(scenario)
      expect(result.id).toBe(1)
      expect(result.title).toBe('Test Dialogue')
      expect(result.description).toBe('Test description')
      expect(result.keywords).toEqual(['test', 'dialogue'])
      expect(result.category).toBe('VACATION')
      expect(result.isActive).toBe(true)
      expect(result.displayOrder).toBe(0)
      expect(result.stepsCount).toBe(2)
      expect(result.createdAt).toBe('2024-01-01')
    })

    it('handles null description', () => {
      const scenario = {
        id: 1,
        title: 'Test',
        description: null,
        keywords: [],
        category: 'VACATION' as const,
        is_active: true,
        display_order: 0,
        steps: [],
        created_at: null,
      }

      const result = mapDialogue(scenario)
      expect(result.description).toBe('')
      expect(result.createdAt).toBe('')
    })

    it('handles missing steps', () => {
      const scenario = {
        id: 1,
        title: 'Test',
        description: 'Test',
        keywords: [],
        category: 'VACATION' as const,
        is_active: true,
        display_order: 0,
        steps: null,
        created_at: '2024-01-01T00:00:00Z',
      }

      const result = mapDialogue(scenario)
      expect(result.stepsCount).toBe(0)
    })
  })

  describe('toPayload', () => {
    it('converts form data to API payload', () => {
      const form: DialogueFormData = {
        title: 'Test Dialogue',
        description: 'Test description',
        keywords: 'test, dialogue, sample',
        category: 'VACATION',
        is_active: true,
        display_order: 0,
      }

      const result = toPayload(form)
      expect(result.title).toBe('Test Dialogue')
      expect(result.description).toBe('Test description')
      expect(result.keywords).toEqual(['test', 'dialogue', 'sample'])
      expect(result.category).toBe('VACATION')
      expect(result.is_active).toBe(true)
      expect(result.display_order).toBe(0)
    })

    it('splits keywords by comma and trims whitespace', () => {
      const form: DialogueFormData = {
        title: 'Test',
        description: '',
        keywords: '  test  ,  dialogue  , sample  ',
        category: 'VACATION',
        is_active: true,
        display_order: 0,
      }

      const result = toPayload(form)
      expect(result.keywords).toEqual(['test', 'dialogue', 'sample'])
    })

    it('filters empty keywords', () => {
      const form: DialogueFormData = {
        title: 'Test',
        description: '',
        keywords: 'test, , dialogue, , sample',
        category: 'VACATION',
        is_active: true,
        display_order: 0,
      }

      const result = toPayload(form)
      expect(result.keywords).toEqual(['test', 'dialogue', 'sample'])
    })

    it('handles empty keywords string', () => {
      const form: DialogueFormData = {
        title: 'Test',
        description: '',
        keywords: '',
        category: 'VACATION',
        is_active: true,
        display_order: 0,
      }

      const result = toPayload(form)
      expect(result.keywords).toEqual([])
    })

    it('handles null description', () => {
      const form: DialogueFormData = {
        title: 'Test',
        description: '',
        keywords: 'test',
        category: 'VACATION',
        is_active: true,
        display_order: 0,
      }

      const result = toPayload(form)
      expect(result.description).toBeUndefined()
    })
  })

  describe('toForm', () => {
    it('converts DialogueRow to FormData', () => {
      const row: DialogueRow = {
        id: 1,
        title: 'Test Dialogue',
        description: 'Test description',
        keywords: ['test', 'dialogue'],
        category: 'VACATION',
        isActive: true,
        displayOrder: 0,
        stepsCount: 2,
        createdAt: '2024-01-01',
      }

      const result = toForm(row)
      expect(result.title).toBe('Test Dialogue')
      expect(result.description).toBe('Test description')
      expect(result.keywords).toBe('test, dialogue')
      expect(result.category).toBe('VACATION')
      expect(result.is_active).toBe(true)
      expect(result.display_order).toBe(0)
    })

    it('joins keywords with comma and space', () => {
      const row: DialogueRow = {
        id: 1,
        title: 'Test',
        description: '',
        keywords: ['test', 'dialogue', 'sample'],
        category: 'VACATION',
        isActive: true,
        displayOrder: 0,
        stepsCount: 0,
        createdAt: '2024-01-01',
      }

      const result = toForm(row)
      expect(result.keywords).toBe('test, dialogue, sample')
    })

    it('handles empty keywords array', () => {
      const row: DialogueRow = {
        id: 1,
        title: 'Test',
        description: '',
        keywords: [],
        category: 'VACATION',
        isActive: true,
        displayOrder: 0,
        stepsCount: 0,
        createdAt: '2024-01-01',
      }

      const result = toForm(row)
      expect(result.keywords).toBe('')
    })
  })

  describe('hook integration', () => {
    it('loads dialogues list', async () => {
      mockFetchResponse({
        scenarios: [
          {
            id: 1,
            title: 'Test Dialogue',
            description: 'Test description',
            keywords: ['test', 'dialogue'],
            category: 'VACATION',
            is_active: true,
            display_order: 0,
            steps: [],
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 1,
      })

      const { result } = renderHook(() => useDialogues(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.dialogues).toHaveLength(1)
      expect(result.current.totalCount).toBe(1)
    })

    it('resets filters', async () => {
      mockFetchResponse({
        scenarios: [],
        total: 0,
      })

      const { result } = renderHook(() => useDialogues(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      result.current.resetFilters()
      expect(result.current.searchQuery).toBe('')
      expect(result.current.categoryFilter).toBe('ALL')
    })

    it('returns selected steps as array', async () => {
      mockFetchResponse({
        scenarios: [],
        total: 0,
      })

      const { result } = renderHook(() => useDialogues(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(Array.isArray(result.current.selectedSteps)).toBe(true)
    })
  })
})
