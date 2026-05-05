import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useEntityMutations } from '@/hooks/entity/use-entity-mutations'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

vi.mock('@/lib/error', () => ({
  handleError: vi.fn((error) => error),
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      mutations: {
        retry: false,
      },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useEntityMutations', () => {
  it('returns loading states', () => {
    const createFn = vi.fn().mockResolvedValue({ success: true, data: {} })
    const updateFn = vi.fn().mockResolvedValue({ success: true, data: {} })
    const deleteFn = vi.fn().mockResolvedValue({ success: true, data: {} })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn,
            updateFn,
            deleteFn,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: {},
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.isDeleting).toBe(false)
  })

  it('handles create mutation success', async () => {
    const createFn = vi.fn().mockResolvedValue({ success: true, data: { id: 1 } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn,
            updateFn: undefined,
            deleteFn: undefined,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: { name: 'Test' },
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      result.current.createMutation.mutate({ name: 'Test' })
    })

    expect(createFn).toHaveBeenCalledWith({ name: 'Test' })
    expect(toast).toHaveBeenCalledWith('Created', 'success')
    expect(invalidate).toHaveBeenCalled()
    expect(setIsCreateDialogOpen).toHaveBeenCalledWith(false)
    expect(resetFormInternal).toHaveBeenCalled()
  })

  it('handles create mutation error', async () => {
    const createFn = vi.fn().mockResolvedValue({ success: false, error: { message: 'Error' } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn,
            updateFn: undefined,
            deleteFn: undefined,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: {},
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      try {
        result.current.createMutation.mutate({ name: 'Test' })
      } catch (e) {
        // Expected
      }
    })

    expect(toast).toHaveBeenCalledWith('Create error', 'error')
  })

  it('handles update mutation success', async () => {
    const updateFn = vi.fn().mockResolvedValue({ success: true, data: { id: 1 } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn: undefined,
            updateFn,
            deleteFn: undefined,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: { name: 'Updated' },
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      result.current.updateMutation.mutate({ id: 1, data: { name: 'Updated' } })
    })

    expect(updateFn).toHaveBeenCalledWith(1, { name: 'Updated' })
    expect(toast).toHaveBeenCalledWith('Updated', 'success')
    expect(invalidate).toHaveBeenCalled()
    expect(setIsEditDialogOpen).toHaveBeenCalledWith(false)
    expect(setSelectedItem).toHaveBeenCalledWith(null)
  })

  it('handles delete mutation success', async () => {
    const deleteFn = vi.fn().mockResolvedValue({ success: true, data: {} })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn: undefined,
            updateFn: undefined,
            deleteFn,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: {},
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      result.current.deleteMutation.mutate(1)
    })

    expect(deleteFn).toHaveBeenCalledWith(1)
    expect(toast).toHaveBeenCalledWith('Deleted', 'success')
    expect(invalidate).toHaveBeenCalled()
  })

  it('handles delete mutation error', async () => {
    const deleteFn = vi.fn().mockResolvedValue({ success: false, error: { message: 'Error' } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn: undefined,
            updateFn: undefined,
            deleteFn,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: {},
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      try {
        result.current.deleteMutation.mutate(1)
      } catch (e) {
        // Expected
      }
    })

    expect(toast).toHaveBeenCalledWith('Delete error', 'error')
  })

  it('handleSubmit calls create mutation when no selected item', async () => {
    const createFn = vi.fn().mockResolvedValue({ success: true, data: { id: 1 } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn,
            updateFn: undefined,
            deleteFn: undefined,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: null,
            formData: { name: 'New' },
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      result.current.handleSubmit()
    })

    expect(createFn).toHaveBeenCalled()
  })

  it('handleSubmit calls update mutation when selected item exists', async () => {
    const updateFn = vi.fn().mockResolvedValue({ success: true, data: { id: 1 } })
    const toast = vi.fn()
    const invalidate = vi.fn()
    const setExtendedState = vi.fn()
    const setSelectedItem = vi.fn()
    const setIsCreateDialogOpen = vi.fn()
    const setIsEditDialogOpen = vi.fn()
    const resetFormInternal = vi.fn()

    const { result } = renderHook(
      () =>
        useEntityMutations(
          {
            createFn: undefined,
            updateFn,
            deleteFn: undefined,
            queryKeyPrefix: 'users',
            toCreatePayload: (data: any) => data,
          },
          {
            toast,
            invalidate,
            extendedState: {},
            setExtendedState,
            selectedItem: { id: 1 },
            formData: { name: 'Updated' },
          },
          {
            created: 'Created',
            updated: 'Updated',
            deleted: 'Deleted',
            createError: 'Create error',
            updateError: 'Update error',
            deleteError: 'Delete error',
          },
          resetFormInternal,
          setIsCreateDialogOpen,
          setIsEditDialogOpen,
          setSelectedItem,
          (form: any) => form,
        ),
      { wrapper: createWrapper() },
    )

    await act(async () => {
      result.current.handleSubmit()
    })

    expect(updateFn).toHaveBeenCalledWith(1, { name: 'Updated' })
  })
})
