import { describe, it, expect } from 'vitest'
import { buildQueryString } from '@/lib/utils/query-builder'

describe('buildQueryString', () => {
  it('returns empty string for undefined params', () => {
    expect(buildQueryString()).toBe('')
  })

  it('returns empty string for empty object', () => {
    expect(buildQueryString({})).toBe('')
  })

  it('builds single parameter', () => {
    expect(buildQueryString({ name: 'value' })).toBe('name=value')
  })

  it('builds multiple parameters', () => {
    const result = buildQueryString({ a: '1', b: '2' })
    expect(result).toContain('a=1')
    expect(result).toContain('b=2')
    expect(result).toMatch(/^(a=1&b=2|b=2&a=1)$/)
  })

  it('excludes undefined values', () => {
    expect(buildQueryString({ a: '1', b: undefined })).toBe('a=1')
  })

  it('excludes null values', () => {
    expect(buildQueryString({ a: '1', b: null })).toBe('a=1')
  })

  it('includes zero values', () => {
    expect(buildQueryString({ page: 0 })).toBe('page=0')
  })

  it('includes false values', () => {
    expect(buildQueryString({ active: false })).toBe('active=false')
  })

  it('includes empty string values', () => {
    expect(buildQueryString({ search: '' })).toBe('search=')
  })

  it('converts numbers to strings', () => {
    expect(buildQueryString({ count: 42 })).toBe('count=42')
  })

  it('converts booleans to strings', () => {
    expect(buildQueryString({ active: true })).toBe('active=true')
  })

  it('URL-encodes special characters', () => {
    expect(buildQueryString({ search: 'hello world' })).toBe('search=hello+world')
  })

  it('handles complex example with mixed types', () => {
    const result = buildQueryString({
      skip: 0,
      limit: 10,
      search: 'test query',
      active: true,
      category: undefined,
    })
    expect(result).toContain('skip=0')
    expect(result).toContain('limit=10')
    expect(result).toContain('search=test+query')
    expect(result).toContain('active=true')
    expect(result).not.toContain('category')
  })
})
