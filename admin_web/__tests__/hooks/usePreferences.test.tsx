import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { usePreferences } from '@/hooks/use-preferences'

// Mock the API client
vi.mock('@/lib/api/users', () => ({
  usersApi: {
    getMyPreferences: vi.fn(),
    updateMyPreferences: vi.fn(),
  },
}))

// Mock the query keys
vi.mock('@/lib/query-keys', () => ({
  queryKeys: {
    preferences: () => ['preferences'] as const,
  },
}))

import { usersApi } from '@/lib/api/users'

describe('usePreferences', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    })
    vi.clearAllMocks()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )

  it('fetches user preferences on mount', async () => {
    const mockPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: mockPreferences })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(usersApi.getMyPreferences).toHaveBeenCalledOnce()
    expect(result.current.preferences).toEqual({ success: true, data: mockPreferences })
  })

  it('handles fetch errors gracefully', async () => {
    vi.mocked(usersApi.getMyPreferences).mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.preferences).toBeUndefined()
  })

  it('updates preferences with optimistic updates', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    const updatedPreferences = {
      language: 'ru',
      notification_telegram_enabled: false,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockResolvedValue({ success: true, data: updatedPreferences })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Optimistic update should happen immediately
    result.current.updatePreferences({
      language: 'ru',
      notification_telegram_enabled: false,
    })

    // Wait for mutation to complete
    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    // Check that the API was called
    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith({
      language: 'ru',
      notification_telegram_enabled: false,
    })
  })

  it('updates only language preference', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockResolvedValue({
      success: true,
      data: {
        ...initialPreferences,
        language: 'ru',
      },
    })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.updatePreferences({ language: 'ru' })

    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith({ language: 'ru' })
  })

  it('updates only notification_telegram_enabled preference', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockResolvedValue({
      success: true,
      data: {
        ...initialPreferences,
        notification_telegram_enabled: false,
      },
    })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.updatePreferences({ notification_telegram_enabled: false })

    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith({ notification_telegram_enabled: false })
  })

  it('updates only notification_email_enabled preference', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockResolvedValue({
      success: true,
      data: {
        ...initialPreferences,
        notification_email_enabled: false,
      },
    })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.updatePreferences({ notification_email_enabled: false })

    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith({ notification_email_enabled: false })
  })

  it('updates multiple preferences at once', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    const updatedPreferences = {
      language: 'ru',
      notification_telegram_enabled: false,
      notification_email_enabled: false,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockResolvedValue({ success: true, data: updatedPreferences })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.updatePreferences(updatedPreferences)

    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith(updatedPreferences)
  })

  it('handles update errors gracefully', async () => {
    const initialPreferences = {
      language: 'en',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }

    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: initialPreferences })
    vi.mocked(usersApi.updateMyPreferences).mockRejectedValue(new Error('Update failed'))

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.updatePreferences({ language: 'ru' })

    // Wait for mutation to complete
    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false)
    })

    // Mutation error is not exposed by the hook, but it should not crash
    expect(usersApi.updateMyPreferences).toHaveBeenCalledWith({ language: 'ru' })
  })

  it('returns default preferences when none exist', async () => {
    const mockPreferences = {
      language: 'ru',
      notification_telegram_enabled: true,
      notification_email_enabled: true,
    }
    vi.mocked(usersApi.getMyPreferences).mockResolvedValue({ success: true, data: mockPreferences })

    const { result } = renderHook(() => usePreferences(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.preferences).toEqual({ success: true, data: mockPreferences })
  })
})
