import { describe, it, expect, vi, beforeEach } from 'vitest'
import { pad, formatTimestamp, getCallerLocation, LoggerClass } from '@/lib/logger'

describe('logger helper functions', () => {
  describe('pad', () => {
    it('pads single digit with zero', () => {
      expect(pad(5)).toBe('05')
    })

    it('pads with default width 2', () => {
      expect(pad(9)).toBe('09')
    })

    it('does not pad two-digit numbers', () => {
      expect(pad(12)).toBe('12')
    })

    it('pads with custom width', () => {
      expect(pad(5, 3)).toBe('005')
    })

    it('pads zero', () => {
      expect(pad(0)).toBe('00')
    })

    it('handles large numbers', () => {
      expect(pad(999)).toBe('999')
    })
  })

  describe('formatTimestamp', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-15T12:30:45.123Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{4}-\d{2}-\d{2}/)
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}\.\d{3}/)
    })

    it('handles single digit month', () => {
      const date = new Date('2024-01-01T00:00:00.000Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{4}-01-\d{2}/)
    })

    it('handles single digit day', () => {
      const date = new Date('2024-01-05T00:00:00.000Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{4}-01-05/)
    })

    it('handles single digit hour', () => {
      const date = new Date('2024-01-01T09:00:00.000Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}/)
    })

    it('handles single digit minute', () => {
      const date = new Date('2024-01-01T00:05:00.000Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}/)
    })

    it('handles single digit second', () => {
      const date = new Date('2024-01-01T00:00:05.000Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}/)
    })

    it('handles milliseconds', () => {
      const date = new Date('2024-01-01T00:00:00.005Z')
      const result = formatTimestamp(date)
      expect(result).toMatch(/\.\d{3}$/)
    })
  })

  describe('getCallerLocation', () => {
    it('returns a string', () => {
      const result = getCallerLocation()
      expect(typeof result).toBe('string')
    })

    it('returns fallback when cannot parse stack', () => {
      const result = getCallerLocation()
      expect(result).toBeTruthy()
    })
  })
})

describe('logger', () => {
  const originalEnv = process.env.NODE_ENV
  let testLogger: LoggerClass

  beforeEach(() => {
    vi.clearAllMocks()
    process.env.NODE_ENV = originalEnv
  })

  it('exports logger object', () => {
    testLogger = new LoggerClass()
    expect(testLogger).toBeDefined()
    expect(typeof testLogger.info).toBe('function')
    expect(typeof testLogger.warn).toBe('function')
    expect(typeof testLogger.error).toBe('function')
    expect(typeof testLogger.debug).toBe('function')
  })

  it('info method can be called without throwing', () => {
    expect(() => testLogger.info('Test message')).not.toThrow()
  })

  it('warn method can be called without throwing', () => {
    expect(() => testLogger.warn('Test message')).not.toThrow()
  })

  it('error method can be called without throwing', () => {
    expect(() => testLogger.error('Test message')).not.toThrow()
  })

  it('debug method can be called without throwing', () => {
    expect(() => testLogger.debug('Test message')).not.toThrow()
  })

  it('info method can be called with context', () => {
    expect(() => testLogger.info('Test message', { key: 'value' })).not.toThrow()
  })

  it('warn method can be called with context', () => {
    expect(() => testLogger.warn('Test message', { key: 'value' })).not.toThrow()
  })

  it('error method can be called with context', () => {
    expect(() => testLogger.error('Error message', { code: 'TEST_ERROR' })).not.toThrow()
  })

  it('debug method can be called with context', () => {
    expect(() => testLogger.debug('Debug message', { debug: true })).not.toThrow()
  })

  it('handles null context', () => {
    expect(() => testLogger.info('Test message', null as any)).not.toThrow()
  })

  it('handles undefined context', () => {
    expect(() => testLogger.info('Test message', undefined)).not.toThrow()
  })

  it('handles empty object context', () => {
    expect(() => testLogger.info('Test message', {})).not.toThrow()
  })

  it('handles complex context objects', () => {
    const context = {
      userId: 123,
      action: 'create',
      nested: { key: 'value' },
      array: [1, 2, 3],
    }
    expect(() => testLogger.info('Test message', context)).not.toThrow()
  })

  it('handles special characters in message', () => {
    expect(() => testLogger.info('Test with "quotes" and \n newlines')).not.toThrow()
  })

  it('handles empty message', () => {
    expect(() => testLogger.info('')).not.toThrow()
  })

  it('handles very long messages', () => {
    const longMessage = 'x'.repeat(10000)
    expect(() => testLogger.info(longMessage)).not.toThrow()
  })

  it('handles context with null values', () => {
    expect(() => testLogger.info('Test message', { key: null, value: undefined })).not.toThrow()
  })

  it('handles context with circular references (should not throw)', () => {
    const context: Record<string, unknown> = { key: 'value' }
    context.self = context
    expect(() => testLogger.info('Test message', context)).not.toThrow()
  })

  it('handles context with numbers', () => {
    expect(() => testLogger.info('Test message', { count: 42, price: 19.99 })).not.toThrow()
  })

  it('handles context with booleans', () => {
    expect(() => testLogger.info('Test message', { active: true, deleted: false })).not.toThrow()
  })

  it('handles context with arrays', () => {
    expect(() => testLogger.info('Test message', { tags: ['tag1', 'tag2'] })).not.toThrow()
  })

  it('handles context with mixed types', () => {
    expect(() => testLogger.info('Test message', {
      string: 'test',
      number: 123,
      boolean: true,
      array: [1, 2, 3],
      nested: { key: 'value' },
    })).not.toThrow()
  })

  describe('development mode', () => {
    let consoleErrorSpy: any
    let consoleWarnSpy: any
    let consoleDebugSpy: any
    let consoleLogSpy: any

    beforeEach(() => {
      vi.clearAllMocks()
      process.env.NODE_ENV = 'development'
      consoleErrorSpy = vi.spyOn(console, 'error')
      consoleWarnSpy = vi.spyOn(console, 'warn')
      consoleDebugSpy = vi.spyOn(console, 'debug')
      consoleLogSpy = vi.spyOn(console, 'log')
      testLogger = new LoggerClass()
    })

    it('logs info to console.log in development', () => {
      testLogger.info('Test message')
      expect(consoleLogSpy).toHaveBeenCalled()
    })

    it('logs warn to console.warn in development', () => {
      testLogger.warn('Test message')
      expect(consoleWarnSpy).toHaveBeenCalled()
    })

    it('logs error to console.error in development', () => {
      testLogger.error('Test message')
      expect(consoleErrorSpy).toHaveBeenCalled()
    })

    it('logs debug to console.debug in development', () => {
      testLogger.debug('Test message')
      expect(consoleDebugSpy).toHaveBeenCalled()
    })

    it('formats log output with timestamp, level, location and message', () => {
      testLogger.info('Test message', { key: 'value' })
      expect(consoleLogSpy).toHaveBeenCalled()
      const call = consoleLogSpy.mock.calls[0][0] as string
      expect(call).toContain('INFO')
      expect(call).toContain('Test message')
      expect(call).toContain('key')
    })

    it('includes context in formatted output', () => {
      testLogger.info('Test', { userId: 123 })
      expect(consoleLogSpy).toHaveBeenCalled()
      const call = consoleLogSpy.mock.calls[0][0] as string
      expect(call).toContain('userId')
      expect(call).toContain('123')
    })

    it('does not include context when undefined', () => {
      testLogger.info('Test')
      expect(consoleLogSpy).toHaveBeenCalled()
      const call = consoleLogSpy.mock.calls[0][0] as string
      expect(call).toContain('Test')
    })
  })

  describe('production mode', () => {
    let consoleErrorSpy: any
    let consoleLogSpy: any
    let consoleWarnSpy: any
    let consoleDebugSpy: any

    beforeEach(() => {
      vi.clearAllMocks()
      process.env.NODE_ENV = 'production'
      consoleErrorSpy = vi.spyOn(console, 'error')
      consoleLogSpy = vi.spyOn(console, 'log')
      consoleWarnSpy = vi.spyOn(console, 'warn')
      consoleDebugSpy = vi.spyOn(console, 'debug')
      testLogger = new LoggerClass()
    })

    it('logs errors as JSON in production', () => {
      testLogger.error('Error message', { code: 'TEST' })
      expect(consoleErrorSpy).toHaveBeenCalled()
      const call = consoleErrorSpy.mock.calls[0][0] as string
      const parsed = JSON.parse(call)
      expect(parsed.level).toBe('error')
      expect(parsed.message).toBe('Error message')
      expect(parsed.context).toEqual({ code: 'TEST' })
      expect(parsed.timestamp).toBeTruthy()
      expect(parsed.location).toBeTruthy()
    })

    it('does not log non-error levels in production', () => {
      testLogger.info('Info message')
      testLogger.warn('Warn message')
      testLogger.debug('Debug message')
      expect(consoleLogSpy).not.toHaveBeenCalled()
      expect(consoleWarnSpy).not.toHaveBeenCalled()
      expect(consoleDebugSpy).not.toHaveBeenCalled()
    })

    it('includes location in production error logs', () => {
      testLogger.error('Error')
      expect(consoleErrorSpy).toHaveBeenCalled()
      const call = consoleErrorSpy.mock.calls[0][0] as string
      const parsed = JSON.parse(call)
      expect(parsed.location).toBeTruthy()
    })
  })
})
