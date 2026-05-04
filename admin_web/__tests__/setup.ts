import { vi, afterEach } from 'vitest'
import '@testing-library/jest-dom'

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
    pathname: '/',
    query: {},
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}))

// Mock fetch globally
export function mockFetchResponse<T>(data: T, status = 200) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  } as Response)
}

export function mockFetchError(status = 500, message = 'Server error') {
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    status,
    json: async () => ({ detail: message }),
  } as Response)
}

export function mockFetchNetworkError(message = 'Network error') {
  global.fetch = vi.fn().mockRejectedValue(new Error(message))
}

// Reset mocks after each test
afterEach(() => {
  vi.restoreAllMocks()
})
