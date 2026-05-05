import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useToast } from '@/hooks/use-toast'

vi.mock('@/components/ui/toast', () => ({
  ToastContext: {
    Provider: ({ children }: { children: React.ReactNode }) => children,
  },
}))

vi.mock('react', async () => {
  const actual = await vi.importActual('react')
  const mockToast = vi.fn(() => Promise.resolve(true))
  return {
    ...actual,
    useContext: () => mockToast,
  }
})

describe('useToast', () => {
  it('exports useToast function', () => {
    expect(typeof useToast).toBe('function')
  })

  it('returns toast function from context', () => {
    const { result } = renderHook(() => useToast())
    expect(typeof result.current).toBe('function')
  })

  it('returns a promise from toast call', () => {
    const { result } = renderHook(() => useToast())
    const resultPromise = result.current('Test message')
    expect(resultPromise).toBeInstanceOf(Promise)
  })

  it('accepts options object', () => {
    const { result } = renderHook(() => useToast())
    const resultPromise = result.current({
      title: 'Success',
      description: 'Operation completed',
      variant: 'success'
    })
    expect(resultPromise).toBeInstanceOf(Promise)
  })

  it('memoizes toast function across renders', () => {
    const { result, rerender } = renderHook(() => useToast())
    const firstToast = result.current
    rerender()
    expect(result.current).toBe(firstToast)
  })
})
