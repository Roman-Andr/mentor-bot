import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ToastProvider, useToast } from '@/shared/ui/toast'
import { renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'

vi.mock('@/shared/lib/utils', () => ({
  cn: (...args: string[]) => args.filter(Boolean).join(' '),
}))

const wrapper = ({ children }: { children: ReactNode }) => (
  <ToastProvider>{children}</ToastProvider>
)

describe('ToastProvider', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('renders children', () => {
    render(<ToastProvider><div data-testid="child">child</div></ToastProvider>)
    expect(screen.getByTestId('child')).toBeDefined()
  })

  it('shows a success toast', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Saved!', 'success'))
    expect(screen.getByText('Saved!')).toBeDefined()
  })

  it('shows an error toast', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Something went wrong', 'error'))
    expect(screen.getByText('Something went wrong')).toBeDefined()
  })

  it('shows an info toast by default', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Information'))
    expect(screen.getByText('Information')).toBeDefined()
  })

  it('removes toast after timeout', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Temporary'))
    expect(screen.getByText('Temporary')).toBeDefined()
    act(() => vi.advanceTimersByTime(5000))
    expect(screen.queryByText('Temporary')).toBeNull()
  })

  it('removes toast on close button click', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Closeable'))
    const closeBtn = screen.getByRole('button')
    fireEvent.click(closeBtn)
    expect(screen.queryByText('Closeable')).toBeNull()
  })

  it('can show multiple toasts', () => {
    const { result } = renderHook(() => useToast(), { wrapper })
    act(() => {
      result.current.toast('First', 'success')
      result.current.toast('Second', 'error')
    })
    expect(screen.getByText('First')).toBeDefined()
    expect(screen.getByText('Second')).toBeDefined()
  })

  it('clears timeouts on unmount', () => {
    const clearSpy = vi.spyOn(globalThis, 'clearTimeout')
    const { result, unmount } = renderHook(() => useToast(), { wrapper })
    act(() => result.current.toast('Will be cleared'))
    unmount()
    expect(clearSpy).toHaveBeenCalled()
  })
})

describe('useToast outside provider', () => {
  it('throws when used outside ToastProvider', () => {
    expect(() => renderHook(() => useToast())).toThrow(
      'useToast must be used within ToastProvider'
    )
  })
})
