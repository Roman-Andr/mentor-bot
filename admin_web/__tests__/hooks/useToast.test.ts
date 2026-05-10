import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useToast } from '@/shared/hooks/use-toast'

// Mock the useContext hook
const mockUseContext = vi.hoisted(() => vi.fn())
vi.mock('react', async () => {
  const actual = await vi.importActual('react')
  const mockToast = vi.fn(() => Promise.resolve(true))
  return {
    ...actual,
    useContext: mockUseContext,
  }
})

vi.mock('@/shared/ui/toast', () => ({
  ToastContext: {
    Provider: ({ children }: { children: React.ReactNode }) => children,
  },
}))

describe('useToast', () => {
  it('exports useToast function', () => {
    expect(typeof useToast).toBe('function')
  })

  it('returns toast function from context', () => {
    const mockToast = vi.fn(() => Promise.resolve(true))
    mockUseContext.mockReturnValue({ toast: mockToast })
    
    const { result } = renderHook(() => useToast())
    expect(typeof result.current.toast).toBe('function')
  })

  it('returns a promise from toast call', () => {
    const mockToast = vi.fn(() => Promise.resolve(true))
    mockUseContext.mockReturnValue({ toast: mockToast })
    
    const { result } = renderHook(() => useToast())
    const resultPromise = result.current.toast('Test message')
    expect(resultPromise).toBeInstanceOf(Promise)
  })

  it('accepts options object', () => {
    const mockToast = vi.fn(() => Promise.resolve(true))
    mockUseContext.mockReturnValue({ toast: mockToast })
    
    const { result } = renderHook(() => useToast())
    const resultPromise = result.current.toast('Test message', 'success')
    expect(resultPromise).toBeInstanceOf(Promise)
  })

  it('memoizes toast function across renders', () => {
    const mockToast = vi.fn(() => Promise.resolve(true))
    mockUseContext.mockReturnValue({ toast: mockToast })
    
    const { result, rerender } = renderHook(() => useToast())
    const firstToast = result.current.toast
    rerender()
    expect(result.current.toast).toBe(firstToast)
  })

  it('throws error when used outside ToastProvider', () => {
    mockUseContext.mockReturnValue(null)

    expect(() => {
      renderHook(() => useToast())
    }).toThrow('useToast must be used within ToastProvider')
  })
})
