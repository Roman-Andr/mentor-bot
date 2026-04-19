import { describe, it, expect } from 'vitest'
import { cn, formatDate, formatDateTime, getInitials } from '@/lib/utils'

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2')
  })

  it('handles conditional classes with objects', () => {
    expect(cn('base', { active: true, disabled: false })).toBe('base active')
  })

  it('handles arrays of classes', () => {
    expect(cn(['class1', 'class2'])).toBe('class1 class2')
  })

  it('merges tailwind classes (last wins)', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4')
  })

  it('filters out falsy values', () => {
    expect(cn('base', null, undefined, false, 'active')).toBe('base active')
  })

  it('returns empty string for no inputs', () => {
    expect(cn()).toBe('')
  })
})

describe('formatDate', () => {
  it('formats date string to Russian locale', () => {
    expect(formatDate('2024-03-15')).toBe('15.03.2024')
  })

  it('formats Date object', () => {
    expect(formatDate(new Date(2024, 2, 15))).toBe('15.03.2024')
  })

  it('returns dash for null', () => {
    expect(formatDate(null)).toBe('-')
  })

  it('returns dash for undefined', () => {
    expect(formatDate(undefined)).toBe('-')
  })

  it('returns dash for empty string', () => {
    expect(formatDate('')).toBe('-')
  })
})

describe('formatDateTime', () => {
  it('formats datetime to Russian locale', () => {
    const result = formatDateTime('2024-03-15T14:30:00')
    expect(result).toContain('15.03.2024')
    expect(result).toContain('14:30')
  })

  it('returns dash for null', () => {
    expect(formatDateTime(null)).toBe('-')
  })

  it('returns dash for undefined', () => {
    expect(formatDateTime(undefined)).toBe('-')
  })
})

describe('getInitials', () => {
  it('returns initials for first and last name', () => {
    expect(getInitials('John', 'Doe')).toBe('JD')
  })

  it('returns single initial for first name only', () => {
    expect(getInitials('John')).toBe('J')
  })

  it('handles uppercase input', () => {
    expect(getInitials('JOHN', 'DOE')).toBe('JD')
  })

  it('handles lowercase input', () => {
    expect(getInitials('john', 'doe')).toBe('JD')
  })

  it('returns empty string for empty inputs', () => {
    expect(getInitials('', '')).toBe('')
  })

  it('handles undefined lastName', () => {
    expect(getInitials('John', undefined)).toBe('J')
  })
})
