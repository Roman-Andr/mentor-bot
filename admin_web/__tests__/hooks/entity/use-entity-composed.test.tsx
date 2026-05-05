import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useEntity } from '@/hooks/entity/use-entity-composed'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

vi.mock('@/lib/query-keys', () => ({
  queryKeys: {
    users: {
      list: (params: any) => ['users', 'list', params],
    },
  },
}))

vi.mock('@/components/providers/pagination-provider', () => ({
  usePaginationSettings: () => ({
    pageSize: 10,
    setPageSize: vi.fn(),
  }),
}))

vi.mock('@/hooks/use-debounce', () => ({
  useDebounce: (value: string) => value,
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

vi.mock('@/hooks/use-confirm', () => ({
  useConfirm: () => vi.fn(() => Promise.resolve(true)),
}))

vi.mock('@/hooks/use-translations', () => ({
  useTranslations: () => (key: string) => key,
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useEntity', () => {
  it('initializes with default values', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          translationNamespace: 'users',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    expect(result.current.items).toEqual([])
    expect(result.current.currentPage).toBe(1)
    expect(result.current.searchQuery).toBe('')
    expect(result.current.isCreateDialogOpen).toBe(false)
    expect(result.current.isEditDialogOpen).toBe(false)
    expect(result.current.selectedItem).toBeNull()
  })

  it('sets search query', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setSearchQuery('test')
    })

    expect(result.current.searchQuery).toBe('test')
  })

  it('sets current page', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setCurrentPage(5)
    })

    expect(result.current.currentPage).toBe(5)
  })

  it('opens and closes create dialog', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setIsCreateDialogOpen(true)
    })

    expect(result.current.isCreateDialogOpen).toBe(true)

    act(() => {
      result.current.setIsCreateDialogOpen(false)
    })

    expect(result.current.isCreateDialogOpen).toBe(false)
  })

  it('opens and closes edit dialog', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setIsEditDialogOpen(true)
    })

    expect(result.current.isEditDialogOpen).toBe(true)

    act(() => {
      result.current.setIsEditDialogOpen(false)
    })

    expect(result.current.isEditDialogOpen).toBe(false)
  })

  it('sets selected item', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    const item = { id: 1, name: 'Test' }

    act(() => {
      result.current.setSelectedItem(item)
    })

    expect(result.current.selectedItem).toEqual(item)
  })

  it('updates form field', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '', email: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.updateFormField('name', 'Test User')
    })

    expect(result.current.formData.name).toBe('Test User')
  })

  it('resets form', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setFormData({ name: 'Changed' })
      result.current.setSelectedItem({ id: 1 } as any)
      result.current.resetForm()
    })

    expect(result.current.formData).toEqual({ name: '' })
    expect(result.current.selectedItem).toBeNull()
  })

  it('updates extended state', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          defaultExtendedState: { attachments: [] },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setExtendedState((prev) => ({ ...prev, attachments: ['file.pdf'] }))
    })

    expect(result.current.extendedState.attachments).toEqual(['file.pdf'])
  })

  it('opens edit dialog with item data', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    const item = { id: 1, name: 'Test User' }

    act(() => {
      result.current.openEditDialog(item)
    })

    expect(result.current.selectedItem).toEqual(item)
    expect(result.current.formData).toEqual(item)
    expect(result.current.isEditDialogOpen).toBe(true)
  })

  it('handles sorting', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          sortable: true,
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.clearSort()
    })

    expect(result.current.sortField).toBeNull()
  })

  it('handles filters', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          filters: [{ name: 'status', defaultValue: 'ALL' }],
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.setFilterValue('status', 'active')
    })

    expect(result.current.filterValues.status).toBe('active')

    act(() => {
      result.current.resetFilters()
    })

    expect(result.current.filterValues.status).toBe('ALL')
  })

  it('invalidates queries', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })

    const { result } = renderHook(
      () =>
        useEntity({
          entityName: 'User',
          queryKeyPrefix: 'users',
          listFn,
          defaultForm: { name: '' },
          mapItem: (item: any) => item,
          toCreatePayload: (form: any) => form,
          toUpdatePayload: (form: any) => form,
          toForm: (item: any) => item,
        }),
      { wrapper: createWrapper() },
    )

    act(() => {
      result.current.invalidate()
    })

    // Should not throw
    expect(result.current.invalidate).toBeDefined()
  })
})
