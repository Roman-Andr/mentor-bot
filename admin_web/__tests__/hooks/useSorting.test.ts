import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSorting } from '@/hooks/use-sorting'

describe('useSorting', () => {
  it('initializes with null field and asc direction', () => {
    const { result } = renderHook(() => useSorting())
    expect(result.current.sortField).toBeNull()
    expect(result.current.sortDirection).toBe('asc')
  })

  it('initializes with provided field', () => {
    const { result } = renderHook(() => useSorting('name'))
    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('sets field on first toggle', () => {
    const { result } = renderHook(() => useSorting())

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('toggles direction when clicking same field', () => {
    const { result } = renderHook(() => useSorting('name'))

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortField).toBe('name')
    expect(result.current.sortDirection).toBe('desc')
  })

  it('toggles back to asc from desc', () => {
    const { result } = renderHook(() => useSorting('name'))

    act(() => {
      result.current.toggleSort('name')
    })
    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.sortDirection).toBe('asc')
  })

  it('resets to asc when switching to different field', () => {
    const { result } = renderHook(() => useSorting('name'))

    act(() => {
      result.current.toggleSort('name')
    })
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.toggleSort('email')
    })

    expect(result.current.sortField).toBe('email')
    expect(result.current.sortDirection).toBe('asc')
  })

  it('allows setting specific field and direction', () => {
    const { result } = renderHook(() => useSorting())

    act(() => {
      result.current.setSort('created_at', 'desc')
    })

    expect(result.current.sortField).toBe('created_at')
    expect(result.current.sortDirection).toBe('desc')
  })

  it('clears sorting', () => {
    const { result } = renderHook(() => useSorting('name'))

    act(() => {
      result.current.toggleSort('name')
    })
    expect(result.current.sortDirection).toBe('desc')

    act(() => {
      result.current.clearSort()
    })

    expect(result.current.sortField).toBeNull()
    expect(result.current.sortDirection).toBe('asc')
  })

  it('exposes sortState object', () => {
    const { result } = renderHook(() => useSorting('name'))

    expect(result.current.sortState).toEqual({
      field: 'name',
      direction: 'asc'
    })
  })

  it('memoizes callback functions', () => {
    const { result, rerender } = renderHook(() => useSorting())

    const firstToggleSort = result.current.toggleSort
    const firstSetSort = result.current.setSort
    const firstClearSort = result.current.clearSort

    rerender()

    expect(result.current.toggleSort).toBe(firstToggleSort)
    expect(result.current.setSort).toBe(firstSetSort)
    expect(result.current.clearSort).toBe(firstClearSort)
  })

  it('updates callback when sortField changes', () => {
    const { result, rerender } = renderHook(() => useSorting())

    const firstToggleSort = result.current.toggleSort

    act(() => {
      result.current.toggleSort('name')
    })

    expect(result.current.toggleSort).not.toBe(firstToggleSort)
  })
})
