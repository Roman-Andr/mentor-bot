import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDebounce } from '@/hooks/use-debounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 300))
    expect(result.current).toBe('initial')
  })

  it('delays value update', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'initial' } }
    )

    rerender({ value: 'changed' })
    expect(result.current).toBe('initial')

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(result.current).toBe('changed')
  })

  it('resets timer on rapid changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'initial' } }
    )

    rerender({ value: 'change1' })
    await act(async () => { vi.advanceTimersByTime(100) })
    expect(result.current).toBe('initial')

    rerender({ value: 'change2' })
    await act(async () => { vi.advanceTimersByTime(100) })
    expect(result.current).toBe('initial')

    rerender({ value: 'change3' })
    await act(async () => { vi.advanceTimersByTime(100) })
    expect(result.current).toBe('initial')

    await act(async () => { vi.advanceTimersByTime(200) })
    expect(result.current).toBe('change3')
  })

  it('cleans up timer on unmount', () => {
    const { unmount } = renderHook(() => useDebounce('value', 300))
    unmount()
    // No error should occur, timer is cleaned up
    expect(vi.getTimerCount()).toBe(0)
  })

  it('respects custom delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    )

    rerender({ value: 'changed', delay: 500 })
    await act(async () => { vi.advanceTimersByTime(400) })
    expect(result.current).toBe('initial')

    await act(async () => { vi.advanceTimersByTime(100) })
    expect(result.current).toBe('changed')
  })

  it('handles number values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 0 } }
    )

    rerender({ value: 42 })
    await act(async () => { vi.advanceTimersByTime(300) })

    expect(result.current).toBe(42)
  })

  it('handles object values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: { a: 1 } } }
    )

    const newValue = { a: 2 }
    rerender({ value: newValue })
    await act(async () => { vi.advanceTimersByTime(300) })

    expect(result.current).toEqual({ a: 2 })
  })
})
