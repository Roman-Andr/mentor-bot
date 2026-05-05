import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useEntityFilters } from '@/hooks/entity/use-entity-filters'

describe('useEntityFilters', () => {
  it('initializes with default filter values', () => {
    const filters = [
      { name: 'status', defaultValue: 'ALL' },
      { name: 'category', defaultValue: 'default' },
    ]
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    expect(result.current.filterValues).toEqual({
      status: 'ALL',
      category: 'default',
    })
  })

  it('initializes with empty filter values when no filters provided', () => {
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters([], setCurrentPage))

    expect(result.current.filterValues).toEqual({})
  })

  it('sets filter value and resets page', () => {
    const filters = [{ name: 'status', defaultValue: 'ALL' }]
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.setFilterValue('status', 'active')
    })

    expect(result.current.filterValues.status).toBe('active')
    expect(setCurrentPage).toHaveBeenCalledWith(1)
  })

  it('resets filters to defaults', () => {
    const filters = [
      { name: 'status', defaultValue: 'ALL' },
      { name: 'category', defaultValue: 'default' },
    ]
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.setFilterValue('status', 'active')
      result.current.setFilterValue('category', 'tech')
    })

    expect(result.current.filterValues.status).toBe('active')
    expect(result.current.filterValues.category).toBe('tech')

    act(() => {
      result.current.resetFilters()
    })

    expect(result.current.filterValues).toEqual({
      status: 'ALL',
      category: 'default',
    })
  })

  it('resets sort when resetting filters', () => {
    const filters = [{ name: 'status', defaultValue: 'ALL' }]
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.setSort('name', 'desc')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.resetFilters()
    })

    expect(result.current.sortField).toBeNull()
    expect(result.current.sortDirection).toBe('asc')
  })

  it('toggles sort direction on same field', () => {
    const filters = []
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('sets sort field and toggles direction when toggling new field', () => {
    const filters = []
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.toggleSort('name')
    })
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.toggleSort('date')
    })

    expect(result.current.sortField).toBe('date')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('sets sort with explicit direction', () => {
    const filters = []
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.setSort('name', 'desc')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.setSort('date', 'asc')
    })

    expect(result.current.sortField).toBe('date')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('clears sort', () => {
    const filters = []
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    act(() => {
      result.current.setSort('name', 'asc')
    })

    expect(result.current.sortField).toBe('name')

    act(() => {
      result.current.clearSort()
    })

    expect(result.current.sortField).toBeNull()
    expect(result.current.sortDirection).toBe('asc')
  })

  it('initializes sort with null field and asc direction', () => {
    const filters = []
    const setCurrentPage = vi.fn()
    const { result } = renderHook(() => useEntityFilters(filters, setCurrentPage))

    expect(result.current.sortField).toBeNull()
    expect(result.current.sortDirection).toBe('asc')
  })
})
