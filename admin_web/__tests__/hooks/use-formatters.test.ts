import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useFormatters } from '@/hooks/use-formatters'

vi.mock('next-intl', () => ({
  useLocale: () => 'ru',
}))

describe('useFormatters', () => {
  it('returns formatDate and formatDateTime functions', () => {
    const { result } = renderHook(() => useFormatters())
    expect(typeof result.current.formatDate).toBe('function')
    expect(typeof result.current.formatDateTime).toBe('function')
  })

  it('formats a date string', () => {
    const { result } = renderHook(() => useFormatters())
    const formatted = result.current.formatDate('2024-01-15')
    expect(formatted).toBeTruthy()
  })

  it('handles null date gracefully', () => {
    const { result } = renderHook(() => useFormatters())
    const formatted = result.current.formatDate(null)
    expect(formatted).toBe('-')
  })

  it('formats a Date object', () => {
    const { result } = renderHook(() => useFormatters())
    const formatted = result.current.formatDate(new Date('2024-01-15'))
    expect(formatted).toBeTruthy()
  })
})
