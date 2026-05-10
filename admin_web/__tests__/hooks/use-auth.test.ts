import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useAuth } from '@/shared/hooks/use-auth'
import { AuthContext } from '@/shared/lib/auth-context'

// Mock the useContext hook using hoisted approach
const mockUseContext = vi.hoisted(() => vi.fn())
vi.mock('react', async () => {
  const actual = await vi.importActual('react')
  return {
    ...actual,
    useContext: mockUseContext,
  }
})

describe('useAuth', () => {
  it('exports useAuth function', () => {
    expect(typeof useAuth).toBe('function')
  })

  it('returns auth context when available', () => {
    const mockContext = { user: { id: 1, name: 'Test User' }, token: 'test-token' }
    mockUseContext.mockReturnValue(mockContext)

    const { result } = renderHook(() => useAuth())
    
    expect(result.current).toBe(mockContext)
    expect(mockUseContext).toHaveBeenCalledWith(AuthContext)
  })

  it('throws error when used outside AuthProvider', () => {
    mockUseContext.mockReturnValue(undefined)

    expect(() => {
      renderHook(() => useAuth())
    }).toThrow('useAuth must be used within an AuthProvider')
    
    expect(mockUseContext).toHaveBeenCalledWith(AuthContext)
  })
})
