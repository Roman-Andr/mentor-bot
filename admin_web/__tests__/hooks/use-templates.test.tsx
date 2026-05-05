import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NextIntlClientProvider } from 'next-intl'
import { ToastProvider } from '@/components/ui/toast'
import { PaginationContext } from '@/components/providers/pagination-provider'
import { useTemplates, mapTemplateToItem, toCreatePayload, toUpdatePayload, toForm, type TemplateItem, type TemplateFormData } from '@/hooks/use-templates'
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

describe('useTemplates', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exports useTemplates function', () => {
    expect(typeof useTemplates).toBe('function')
  })

  describe('mapTemplateToItem', () => {
    it('maps template data to TemplateItem', () => {
      const data = {
        id: 1,
        name: 'Test Template',
        description: 'Test description',
        department_id: 5,
        department: { id: 5, name: 'Engineering' },
        position: 'Senior',
        duration_days: 30,
        status: 'ACTIVE',
        is_default: false,
        task_categories: ['onboarding'],
        task_count: 10,
      }

      const result = mapTemplateToItem(data)
      expect(result.id).toBe(1)
      expect(result.name).toBe('Test Template')
      expect(result.description).toBe('Test description')
      expect(result.department_id).toBe(5)
      expect(result.department).toBe('Engineering')
      expect(result.position).toBe('Senior')
      expect(result.durationDays).toBe(30)
      expect(result.taskCount).toBe(10)
      expect(result.status).toBe('ACTIVE')
      expect(result.isDefault).toBe(false)
    })

    it('handles null description', () => {
      const data = {
        id: 1,
        name: 'Test',
        description: null,
        department_id: null,
        department: null,
        position: null,
        duration_days: 30,
        status: 'DRAFT',
        is_default: false,
        task_categories: [],
        task_count: 0,
      }

      const result = mapTemplateToItem(data)
      expect(result.description).toBe('')
      expect(result.position).toBe('')
    })

    it('finds department from departments list when not in response', () => {
      const data = {
        id: 1,
        name: 'Test',
        description: null,
        department_id: 5,
        department: null,
        position: null,
        duration_days: 30,
        status: 'DRAFT',
        is_default: false,
        task_categories: [],
        task_count: 0,
      }

      const departments = [{ id: 5, name: 'Engineering' }]
      const result = mapTemplateToItem(data, departments)
      expect(result.department).toBe('Engineering')
    })

    it('handles missing task_count', () => {
      const data = {
        id: 1,
        name: 'Test',
        description: null,
        department_id: null,
        department: null,
        position: null,
        duration_days: 30,
        status: 'DRAFT',
        is_default: false,
        task_categories: [],
      }

      const result = mapTemplateToItem(data)
      expect(result.taskCount).toBe(0)
    })
  })

  describe('toCreatePayload', () => {
    it('converts form data to create payload', () => {
      const form: TemplateFormData = {
        name: 'Test Template',
        description: 'Test description',
        department_id: 5,
        position: 'Senior',
        duration_days: 30,
        status: 'ACTIVE',
        is_default: false,
      }

      const result = toCreatePayload(form)
      expect(result.name).toBe('Test Template')
      expect(result.description).toBe('Test description')
      expect(result.department_id).toBe(5)
      expect(result.position).toBe('Senior')
      expect(result.duration_days).toBe(30)
      expect(result.status).toBe('ACTIVE')
      expect(result.level).toBeNull()
      expect(result.task_categories).toEqual([])
    })

    it('handles empty department_id', () => {
      const form: TemplateFormData = {
        name: 'Test',
        description: '',
        department_id: 0,
        position: '',
        duration_days: 30,
        status: 'DRAFT',
        is_default: false,
      }

      const result = toCreatePayload(form)
      expect(result.department_id).toBeNull()
      expect(result.position).toBeNull()
    })

    it('defaults status to DRAFT', () => {
      const form: TemplateFormData = {
        name: 'Test',
        description: '',
        department_id: 0,
        position: '',
        duration_days: 30,
        status: '',
        is_default: false,
      }

      const result = toCreatePayload(form)
      expect(result.status).toBe('DRAFT')
    })
  })

  describe('toUpdatePayload', () => {
    it('converts form data to update payload', () => {
      const form: TemplateFormData = {
        name: 'Updated Template',
        description: 'Updated description',
        department_id: 5,
        position: 'Senior',
        duration_days: 30,
        status: 'ACTIVE',
        is_default: true,
      }

      const result = toUpdatePayload(form)
      expect(result.name).toBe('Updated Template')
      expect(result.description).toBe('Updated description')
      expect(result.status).toBe('ACTIVE')
      expect(result.is_default).toBe(true)
      expect(result).not.toHaveProperty('department_id')
      expect(result).not.toHaveProperty('position')
      expect(result).not.toHaveProperty('duration_days')
    })

    it('defaults status to DRAFT', () => {
      const form: TemplateFormData = {
        name: 'Test',
        description: '',
        department_id: 0,
        position: '',
        duration_days: 30,
        status: '',
        is_default: false,
      }

      const result = toUpdatePayload(form)
      expect(result.status).toBe('DRAFT')
    })
  })

  describe('toForm', () => {
    it('converts TemplateItem to FormData', () => {
      const item: TemplateItem = {
        id: 1,
        name: 'Test Template',
        description: 'Test description',
        department_id: 5,
        department: 'Engineering',
        position: 'Senior',
        durationDays: 30,
        taskCount: 10,
        status: 'ACTIVE',
        isDefault: false,
      }

      const result = toForm(item)
      expect(result.name).toBe('Test Template')
      expect(result.description).toBe('Test description')
      expect(result.department_id).toBe(5)
      expect(result.position).toBe('Senior')
      expect(result.duration_days).toBe(30)
      expect(result.status).toBe('ACTIVE')
      expect(result.is_default).toBe(false)
    })

    it('handles null department_id', () => {
      const item: TemplateItem = {
        id: 1,
        name: 'Test',
        description: '',
        department_id: null,
        department: '',
        position: '',
        durationDays: 30,
        taskCount: 0,
        status: 'DRAFT',
        isDefault: false,
      }

      const result = toForm(item)
      expect(result.department_id).toBe(0)
    })
  })

  describe('hook integration', () => {
    it('loads templates list', async () => {
      mockFetchResponse({
        templates: [
          {
            id: 1,
            name: 'Test Template',
            description: 'Test description',
            department_id: 5,
            department: { id: 5, name: 'Engineering' },
            position: 'Senior',
            duration_days: 30,
            status: 'ACTIVE',
            is_default: false,
            task_categories: ['onboarding'],
            task_count: 10,
          },
        ],
        total: 1,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.templates).toHaveLength(1)
      expect(result.current.totalCount).toBe(1)
    })

    it('loads departments for mapping', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(Array.isArray(result.current.departments)).toBe(true)
    })

    it('handles search query', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSearchQuery('onboarding')
      })
      expect(result.current.searchQuery).toBe('onboarding')
    })

    it('handles status filter', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setStatusFilter('ACTIVE')
      })
      expect(result.current.statusFilter).toBe('ACTIVE')
    })

    it('handles pagination', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setCurrentPage(2)
      })
      expect(result.current.currentPage).toBe(2)

      act(() => {
        result.current.setPageSize(50)
      })
      expect(result.current.pageSize).toBe(50)
    })

    it('handles sorting', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.toggleSort('name')
      })
      expect(result.current.sortField).toBe('name')
    })

    it('handles form data', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const newFormData: TemplateFormData = {
        name: 'New Template',
        description: 'New description',
        department_id: 5,
        position: 'Senior',
        duration_days: 30,
        status: 'ACTIVE',
        is_default: false,
      }

      act(() => {
        result.current.setFormData(newFormData)
      })
      expect(result.current.formData).toEqual(newFormData)
    })

    it('resets form', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.resetForm()
      })
      expect(result.current.formData.name).toBe('')
    })

    it('resets filters', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSearchQuery('test')
        result.current.setStatusFilter('ACTIVE')
      })
      expect(result.current.searchQuery).toBe('test')
      expect(result.current.statusFilter).toBe('ACTIVE')

      act(() => {
        result.current.resetFilters()
      })
      // resetFilters only resets filter values, not searchQuery
      expect(result.current.searchQuery).toBe('test')
      expect(result.current.statusFilter).toBe('ALL')
    })

    it('handles dialog states', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setIsCreateDialogOpen(true)
      })
      expect(result.current.isCreateDialogOpen).toBe(true)

      act(() => {
        result.current.setIsEditDialogOpen(true)
      })
      expect(result.current.isEditDialogOpen).toBe(true)
    })

    it('handles selected template', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const template: TemplateItem = {
        id: 1,
        name: 'Test',
        description: '',
        department_id: null,
        department: '',
        position: '',
        durationDays: 30,
        taskCount: 0,
        status: 'DRAFT',
        isDefault: false,
      }

      act(() => {
        result.current.setSelectedTemplate(template)
      })
      expect(result.current.selectedTemplate).toEqual(template)
    })

    it('returns tasks as array', async () => {
      mockFetchResponse({
        templates: [],
        total: 0,
      })

      const { result } = renderHook(() => useTemplates(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(Array.isArray(result.current.tasks)).toBe(true)
    })
  })
})
