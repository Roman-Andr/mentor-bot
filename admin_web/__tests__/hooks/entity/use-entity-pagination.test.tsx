import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useEntityPagination } from '@/hooks/entity/use-entity-pagination'

vi.mock('@/components/providers/pagination-provider', () => ({
  usePaginationSettings: () => ({
    pageSize: 10,
    setPageSize: vi.fn(),
  }),
}))

describe('useEntityPagination', () => {
  it('initializes with current page 1', () => {
    const { result } = renderHook(() => useEntityPagination())
    expect(result.current.currentPage).toBe(1)
  })

  it('uses global page size when no initial size provided', () => {
    const { result } = renderHook(() => useEntityPagination())
    expect(result.current.pageSize).toBe(10)
  })

  it('uses initial page size when provided', () => {
    const { result } = renderHook(() => useEntityPagination(25))
    expect(result.current.pageSize).toBe(25)
  })

  it('sets current page', () => {
    const { result } = renderHook(() => useEntityPagination())
    
    act(() => {
      result.current.setCurrentPage(5)
    })

    expect(result.current.currentPage).toBe(5)
  })

  it('sets page size and resets current page to 1', () => {
    const { result } = renderHook(() => useEntityPagination())
    
    act(() => {
      result.current.setCurrentPage(5)
    })
    expect(result.current.currentPage).toBe(5)

    act(() => {
      result.current.setPageSize(20)
    })

    expect(result.current.pageSize).toBe(20)
    expect(result.current.currentPage).toBe(1)
  })
})
