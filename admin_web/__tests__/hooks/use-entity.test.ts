import { describe, it, expect } from 'vitest'
import { useEntity } from '@/hooks/use-entity'

describe('use-entity exports', () => {
  it('exports useEntity function', () => {
    expect(typeof useEntity).toBe('function')
  })
})
