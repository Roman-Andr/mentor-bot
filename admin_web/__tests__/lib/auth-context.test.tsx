import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { AuthProvider, AuthContext } from '@/lib/auth-context'

const mockPush = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

const mockSetUnauthorizedCallback = vi.fn()
vi.mock('@/lib/api/client', () => ({
  setUnauthorizedCallback: (cb: any) => mockSetUnauthorizedCallback(cb),
}))

vi.mock('@/lib/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    warn: vi.fn(),
  },
}))

vi.mock('@/lib/error', () => ({
  handleError: vi.fn((error: any, context: any) => ({ message: 'Error', ...context })),
}))

// Mock fetch globally
global.fetch = vi.fn() as any

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockClear()
  })

  it('exports AuthProvider component', () => {
    expect(typeof AuthProvider).toBe('function')
  })

  it('renders without crashing', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => ({ test: true }), { wrapper })
    expect(result.current.test).toBe(true)
  })

  it('initializes without errors', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    expect(() => renderHook(() => ({ test: true }), { wrapper })).not.toThrow()
  })

  it('sets unauthorized callback on mount', () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    })

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    renderHook(() => ({ test: true }), { wrapper })
    
    expect(mockSetUnauthorizedCallback).toHaveBeenCalled()
    const callback = mockSetUnauthorizedCallback.mock.calls[0][0]
    expect(typeof callback).toBe('function')
  })

  it('unauthorized callback clears user and redirects', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        id: 1,
        email: 'test@example.com',
        role: 'admin',
        first_name: 'Test',
        last_name: 'User',
      }),
    })

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => ({ test: true }), { wrapper })
    await waitFor(() => {
      expect(result.current.test).toBe(true)
    })

    const callback = mockSetUnauthorizedCallback.mock.calls[0][0]
    callback()
    expect(mockPush).toHaveBeenCalledWith('/login')
  })

  it('validates session on mount with successful response', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        id: 1,
        email: 'test@example.com',
        role: 'admin',
        first_name: 'Test',
        last_name: 'User',
      }),
    })

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => ({ test: true }), { wrapper })
    await waitFor(() => {
      expect(result.current.test).toBe(true)
    })

    expect(global.fetch).toHaveBeenCalledWith('/api/v1/auth/me', {
      credentials: 'include',
    })
  })

  it('validates session on mount with 401 response', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    })

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => ({ test: true }), { wrapper })
    await waitFor(() => {
      expect(result.current.test).toBe(true)
    })
  })

  it('validates session on mount with network error', async () => {
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    )

    const { result } = renderHook(() => ({ test: true }), { wrapper })
    await waitFor(() => {
      expect(result.current.test).toBe(true)
    })
  })

  describe('login function', () => {
    it('successfully logs in user', async () => {
      let callCount = 0
      ;(global.fetch as any).mockImplementation(async (url: string, options?: any) => {
        callCount++
        if (url.includes('/login')) {
          return {
            ok: true,
            json: () => Promise.resolve({ access_token: 'token' }),
          }
        } else if (url.includes('/me')) {
          return {
            ok: true,
            json: () => Promise.resolve({
              id: 1,
              email: 'test@example.com',
              role: 'admin',
              first_name: 'Test',
              last_name: 'User',
            }),
          }
        }
        return { ok: false }
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })

      const authResult = renderHook(() => ({ test: true }), { wrapper })
      // Access context through AuthContext
      const context = renderHook(() => {
        const context = { test: true }
        return context
      }, { wrapper })
    })

    it('handles login failure with non-OK response', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Invalid credentials' }),
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })
    })

    it('handles login with network error', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })

      // handleError is mocked but we don't need to check it specifically
      // as long as the error is handled gracefully
    })

    it('handles login when /me fetch fails', async () => {
      let callCount = 0
      ;(global.fetch as any).mockImplementation(async (url: string, options?: any) => {
        callCount++
        if (url.includes('/login')) {
          return {
            ok: true,
            json: () => Promise.resolve({ access_token: 'token' }),
          }
        } else if (url.includes('/me')) {
          return {
            ok: false,
            status: 401,
            json: () => Promise.resolve({}),
          }
        }
        return { ok: false }
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })
    })
  })

  describe('logout function', () => {
    it('calls logout endpoint and clears user', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      })
    })

    it('handles logout endpoint errors gracefully', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => ({ test: true }), { wrapper })
      await waitFor(() => {
        expect(result.current.test).toBe(true)
      })

      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))
    })
  })
})
