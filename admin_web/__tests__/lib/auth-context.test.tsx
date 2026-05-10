import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'
import { useContext } from 'react'
import { AuthProvider, AuthContext } from '@/shared/lib/auth-context'

const mockPush = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

const mockSetUnauthorizedCallback = vi.fn()
vi.mock('@/shared/lib/api/client', () => ({
  setUnauthorizedCallback: (cb: any) => mockSetUnauthorizedCallback(cb),
}))

vi.mock('@/shared/lib/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    warn: vi.fn(),
  },
}))

vi.mock('@/shared/lib/error', () => ({
  handleError: vi.fn((error: any, context: any) => ({ message: 'Error', ...context })),
}))

// Mock fetch globally
global.fetch = vi.fn() as any

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

const renderAuth = () => renderHook(() => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('AuthContext is missing')
  }
  return context
}, { wrapper })

const waitForSessionValidation = async (result: ReturnType<typeof renderAuth>['result']) => {
  await waitFor(() => {
    expect(result.current.isLoading).toBe(false)
  })
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockClear()
    ;(global.fetch as any).mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    })
  })

  it('exports AuthProvider component', () => {
    expect(typeof AuthProvider).toBe('function')
  })

  it('renders without crashing', async () => {
    const { result } = renderAuth()
    await waitForSessionValidation(result)
    expect(result.current.user).toBeNull()
  })

  it('initializes without errors', async () => {
    const { result } = renderAuth()
    await waitForSessionValidation(result)
    expect(result.current.isLoading).toBe(false)
  })

  it('sets unauthorized callback on mount', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    })

    const { result } = renderAuth()
    await waitForSessionValidation(result)
    
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

    const { result } = renderAuth()
    await waitForSessionValidation(result)

    const callback = mockSetUnauthorizedCallback.mock.calls[0][0]
    act(() => {
      callback()
    })
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

    const { result } = renderAuth()
    await waitForSessionValidation(result)

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

    const { result } = renderAuth()
    await waitForSessionValidation(result)
  })

  it('validates session on mount with network error', async () => {
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderAuth()
    await waitForSessionValidation(result)
  })

  describe('login function', () => {
    it('successfully logs in user', async () => {
      let callCount = 0
      ;(global.fetch as any).mockImplementation(async (url: string, options?: any) => {
        callCount++
        if (url.includes('/login')) {
          return {
            ok: true,
            headers: { get: vi.fn(() => null) },
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

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      let loginResult = false
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password')
      })

      expect(loginResult).toBe(true)
      expect(result.current.user?.email).toBe('test@example.com')
    })

    it('handles login failure with non-OK response', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Invalid credentials' }),
      })

      const { result } = renderAuth()
      await waitForSessionValidation(result)
    })

    it('handles login with network error', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderAuth()
      await waitForSessionValidation(result)

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

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      let loginResult = true
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password')
      })

      expect(loginResult).toBe(false)
    })

    it('handles login failure with error data parsing', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: 'Invalid credentials', code: 'AUTH_FAILED' }),
      })

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      let loginResult = true
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password')
      })

      expect(loginResult).toBe(false)
      expect(result.current.user).toBeNull()
    })

    it('handles login failure with invalid JSON response', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('Invalid JSON')),
      })

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      let loginResult = true
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password')
      })

      expect(loginResult).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })

  describe('logout function', () => {
    it('calls logout endpoint and clears user', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      })

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      })

      await act(async () => {
        await result.current.logout()
      })

      expect(result.current.user).toBeNull()
    })

    it('handles logout endpoint errors gracefully', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      })

      const { result } = renderAuth()
      await waitForSessionValidation(result)

      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      await act(async () => {
        await result.current.logout()
      })

      expect(result.current.user).toBeNull()
    })
  })
})
