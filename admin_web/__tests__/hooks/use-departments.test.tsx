import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NextIntlClientProvider } from 'next-intl'
import { ToastProvider } from '@/components/ui/toast'
import { PaginationContext } from '@/components/providers/pagination-provider'
import { useDepartments, mapDepartment, toCreatePayload, toUpdatePayload, toForm, type DepartmentRow, type DepartmentFormData } from '@/hooks/use-departments'
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

describe('useDepartments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('helper functions', () => {
    it('exports useDepartments function', () => {
      expect(typeof useDepartments).toBe('function')
    })

    describe('mapDepartment', () => {
      it('maps Department to DepartmentRow', () => {
        const department = {
          id: 1,
          name: 'Engineering',
          description: 'Engineering department',
          created_at: '2024-01-01T00:00:00Z',
        }

        const result = mapDepartment(department)
        expect(result.id).toBe(1)
        expect(result.name).toBe('Engineering')
        expect(result.description).toBe('Engineering department')
        expect(result.createdAt).toBe('2024-01-01')
      })

      it('handles null description', () => {
        const department = {
          id: 1,
          name: 'Engineering',
          description: null,
          created_at: '2024-01-01T00:00:00Z',
        }

        const result = mapDepartment(department)
        expect(result.description).toBe('')
      })

      it('handles null created_at', () => {
        const department = {
          id: 1,
          name: 'Engineering',
          description: 'Test',
          created_at: null,
        }

        const result = mapDepartment(department)
        expect(result.createdAt).toBe('')
      })
    })

    describe('toCreatePayload', () => {
      it('converts form data to create payload', () => {
        const form: DepartmentFormData = {
          name: 'Engineering',
          description: 'Engineering department',
        }

        const result = toCreatePayload(form)
        expect(result.name).toBe('Engineering')
        expect(result.description).toBe('Engineering department')
      })

      it('converts empty description to null', () => {
        const form: DepartmentFormData = {
          name: 'Engineering',
          description: '',
        }

        const result = toCreatePayload(form)
        expect(result.description).toBeNull()
      })
    })

    describe('toUpdatePayload', () => {
      it('uses same logic as toCreatePayload', () => {
        const form: DepartmentFormData = {
          name: 'Engineering',
          description: 'Updated description',
        }

        const result = toUpdatePayload(form)
        expect(result.name).toBe('Engineering')
        expect(result.description).toBe('Updated description')
      })

      it('converts empty description to null', () => {
        const form: DepartmentFormData = {
          name: 'Engineering',
          description: '',
        }

        const result = toUpdatePayload(form)
        expect(result.description).toBeNull()
      })
    })

    describe('toForm', () => {
      it('converts DepartmentRow to FormData', () => {
        const item: DepartmentRow = {
          id: 1,
          name: 'Engineering',
          description: 'Engineering department',
          createdAt: '2024-01-01',
        }

        const result = toForm(item)
        expect(result.name).toBe('Engineering')
        expect(result.description).toBe('Engineering department')
      })

      it('handles empty description', () => {
        const item: DepartmentRow = {
          id: 1,
          name: 'Engineering',
          description: '',
          createdAt: '2024-01-01',
        }

        const result = toForm(item)
        expect(result.description).toBe('')
      })
    })
  })

  describe('hook integration', () => {
    it('loads departments list', async () => {
      mockFetchResponse({
        departments: [
          {
            id: 1,
            name: 'Engineering',
            description: 'Engineering department',
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 1,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.items).toHaveLength(1)
      expect(result.current.totalCount).toBe(1)
    })

    it('handles search query', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSearchQuery('engineering')
      })
      expect(result.current.searchQuery).toBe('engineering')
    })

    it('handles pagination', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.pageSize).toBe(20)
      expect(result.current.currentPage).toBe(1)

      act(() => {
        result.current.setCurrentPage(2)
      })
      expect(result.current.currentPage).toBe(2)
    })

    it('handles sorting', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

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
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const newFormData: DepartmentFormData = {
        name: 'New Department',
        description: 'New description',
      }

      act(() => {
        result.current.setFormData(newFormData)
      })
      expect(result.current.formData).toEqual(newFormData)
    })

    it('resets form', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.resetForm()
      })
      expect(result.current.formData.name).toBe('')
    })

    it('handles dialog states', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

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

    it('handles selected item', async () => {
      mockFetchResponse({
        departments: [],
        total: 0,
      })

      const { result } = renderHook(() => useDepartments(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const department: DepartmentRow = {
        id: 1,
        name: 'Engineering',
        description: '',
        createdAt: '2024-01-01',
      }

      act(() => {
        result.current.setSelectedItem(department)
      })
      expect(result.current.selectedItem).toEqual(department)
    })
  })
})
