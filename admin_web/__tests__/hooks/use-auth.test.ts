import { describe, it, expect } from 'vitest'
import { useAuth } from '@/hooks/use-auth'

describe('useAuth', () => {
  it('exports useAuth function', () => {
    expect(typeof useAuth).toBe('function')
  })
})
