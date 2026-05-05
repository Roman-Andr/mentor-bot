import { describe, it, expect } from 'vitest'
import { useEntity } from '@/hooks/entity'

describe('entity index exports', () => {
  it('exports useEntity function', () => {
    expect(typeof useEntity).toBe('function')
  })
})
