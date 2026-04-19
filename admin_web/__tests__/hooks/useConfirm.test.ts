import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { ConfirmProvider, useConfirm } from '@/components/ui/confirm-dialog'

// Mock next-intl
vi.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key
}))

describe('useConfirm', () => {
  it('returns confirm function from context', () => {
    const { result } = renderHook(() => useConfirm(), {
      wrapper: ConfirmProvider
    })

    expect(typeof result.current).toBe('function')
  })

  it('returns default function outside provider', () => {
    const { result } = renderHook(() => useConfirm())

    // Should return default function that resolves to false, not throw
    expect(typeof result.current).toBe('function')
  })

  it('returns a promise from confirm call', () => {
    const { result } = renderHook(() => useConfirm(), {
      wrapper: ConfirmProvider
    })

    const confirmPromise = result.current('Are you sure?')

    expect(confirmPromise).toBeInstanceOf(Promise)
  })

  it('accepts options object', () => {
    const { result } = renderHook(() => useConfirm(), {
      wrapper: ConfirmProvider
    })

    const confirmPromise = result.current({
      title: 'Delete Item',
      description: 'This cannot be undone',
      confirmText: 'Delete',
      cancelText: 'Keep',
      variant: 'destructive'
    })

    expect(confirmPromise).toBeInstanceOf(Promise)
  })

  it('accepts string message', () => {
    const { result } = renderHook(() => useConfirm(), {
      wrapper: ConfirmProvider
    })

    const confirmPromise = result.current('Simple confirmation message')

    expect(confirmPromise).toBeInstanceOf(Promise)
  })

  it('confirm function is memoized across renders', () => {
    const { result, rerender } = renderHook(() => useConfirm(), {
      wrapper: ConfirmProvider
    })

    const firstConfirm = result.current

    rerender()

    // Should be same function reference
    expect(result.current).toBe(firstConfirm)
  })
})
