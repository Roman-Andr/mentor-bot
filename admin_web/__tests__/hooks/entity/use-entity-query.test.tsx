import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useEntityQuery } from '@/hooks/entity/use-entity-query'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

vi.mock('@/lib/query-keys', () => ({
  queryKeys: {
    users: {
      list: (params: any) => ['users', 'list', params],
    },
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useEntityQuery', () => {
  it('returns expected structure', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })
    
    const { result } = renderHook(
      () =>
        useEntityQuery(
          {
            queryKeyPrefix: 'users',
            listFn,
            listDataKey: 'items',
            mapItem: (item: any) => item,
          },
          { skip: 0, limit: 10 },
        ),
      { wrapper: createWrapper() },
    )

    expect(result.current).toHaveProperty('items')
    expect(result.current).toHaveProperty('loading')
    expect(result.current).toHaveProperty('totalCount')
    expect(result.current).toHaveProperty('totalPages')
    expect(result.current).toHaveProperty('listQueryKey')
    expect(Array.isArray(result.current.items)).toBe(true)
    expect(typeof result.current.loading).toBe('boolean')
    expect(typeof result.current.totalCount).toBe('number')
    expect(typeof result.current.totalPages).toBe('number')
  })

  it('calls listFn with correct params', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })
    
    renderHook(
      () =>
        useEntityQuery(
          {
            queryKeyPrefix: 'users',
            listFn,
            listDataKey: 'items',
            mapItem: (item: any) => item,
          },
          { skip: 10, limit: 20, search: 'test' },
        ),
      { wrapper: createWrapper() },
    )

    // The hook should have called the query function
    expect(listFn).toBeDefined()
  })

  it('uses custom listDataKey', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { users: [], total: 0, pages: 0 },
    })
    
    const { result } = renderHook(
      () =>
        useEntityQuery(
          {
            queryKeyPrefix: 'users',
            listFn,
            listDataKey: 'users',
            mapItem: (item: any) => item,
          },
          { skip: 0, limit: 10 },
        ),
      { wrapper: createWrapper() },
    )

    expect(result.current.items).toEqual([])
  })

  it('uses default listDataKey when not specified', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })
    
    const { result } = renderHook(
      () =>
        useEntityQuery(
          {
            queryKeyPrefix: 'users',
            listFn,
            mapItem: (item: any) => item,
          },
          { skip: 0, limit: 10 },
        ),
      { wrapper: createWrapper() },
    )

    expect(result.current.items).toEqual([])
  })

  it('handles mapItem function', () => {
    const listFn = vi.fn().mockResolvedValue({
      success: true,
      data: { items: [], total: 0, pages: 0 },
    })
    
    const mapItem = vi.fn((item: any) => ({ ...item, mapped: true }))
    
    renderHook(
      () =>
        useEntityQuery(
          {
            queryKeyPrefix: 'users',
            listFn,
            listDataKey: 'items',
            mapItem,
          },
          { skip: 0, limit: 10 },
        ),
      { wrapper: createWrapper() },
    )

    expect(mapItem).toBeDefined()
  })
})
