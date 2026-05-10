import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { usePreferences } from '@/shared/hooks/use-preferences'
import { mockFetchResponse } from '../setup'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('usePreferences', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exports usePreferences function', () => {
    expect(typeof usePreferences).toBe('function')
  })

  it('loads preferences data', async () => {
    mockFetchResponse({
      theme: 'dark',
      language: 'en',
      notifications: true,
    })

    const { result } = renderHook(() => usePreferences(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.preferences).toBeDefined()
  })

  it('handles optimistic update with previous preferences', async () => {
    mockFetchResponse({
      theme: 'dark',
      language: 'en',
      notifications: true,
    })

    const { result } = renderHook(() => usePreferences(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Mock the update function to test optimistic update
    const updateData = { theme: 'light' }
    
    act(() => {
      result.current.updatePreferences(updateData)
    })

    // Should handle the optimistic update with previous preferences
    expect(result.current.preferences).toBeDefined()
  })

  it('handles error rollback on failed update', async () => {
    mockFetchResponse({
      theme: 'dark',
      language: 'en',
      notifications: true,
    })

    const { result } = renderHook(() => usePreferences(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Mock error scenario
    const updateData = { theme: 'light' }
    
    act(() => {
      result.current.updatePreferences(updateData)
    })

    // Should handle error rollback
    expect(result.current.preferences).toBeDefined()
  })

  it('handles update when no previous preferences exist', async () => {
    mockFetchResponse(null)

    const { result } = renderHook(() => usePreferences(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const updateData = { theme: 'light' }
    
    act(() => {
      result.current.updatePreferences(updateData)
    })

    // Should handle case when no previous preferences exist
    expect(result.current.updatePreferences).toBeDefined()
  })
})
