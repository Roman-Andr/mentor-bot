import { describe, it, expect, vi } from 'vitest'
import { AppError, handleError, isAppError } from '@/lib/error'

describe('AppError', () => {
  it('creates an error with message', () => {
    const error = new AppError('Test error')
    expect(error.message).toBe('Test error')
    expect(error.name).toBe('AppError')
  })

  it('creates an error with code', () => {
    const error = new AppError('Test error', 'TEST_CODE')
    expect(error.code).toBe('TEST_CODE')
  })

  it('creates an error with statusCode', () => {
    const error = new AppError('Test error', 'TEST_CODE', 404)
    expect(error.statusCode).toBe(404)
  })

  it('creates an error with context', () => {
    const context = { userId: 123 }
    const error = new AppError('Test error', 'TEST_CODE', 404, context)
    expect(error.context).toEqual(context)
  })

  it('creates an error with all parameters', () => {
    const context = { userId: 123, action: 'test' }
    const error = new AppError('Test error', 'TEST_CODE', 500, context)
    expect(error.message).toBe('Test error')
    expect(error.code).toBe('TEST_CODE')
    expect(error.statusCode).toBe(500)
    expect(error.context).toEqual(context)
  })
})

describe('handleError', () => {
  it('returns AppError as-is', () => {
    const appError = new AppError('Test error', 'TEST_CODE', 404, { userId: 123 })
    const result = handleError(appError)
    expect(result).toBe(appError)
  })

  it('handles object with message property', () => {
    const error = { message: 'API error' }
    const result = handleError(error, { action: 'create' })
    expect(result).toBeInstanceOf(AppError)
    expect(result.message).toBe('API error')
    expect(result.code).toBe('API_ERROR')
    expect(result.context).toEqual({ action: 'create' })
  })

  it('handles Error instance', () => {
    const error = new Error('Generic error')
    const result = handleError(error, { action: 'update' })
    expect(result).toBeInstanceOf(AppError)
    expect(result.message).toBe('Generic error')
    expect(result.code).toBe('API_ERROR')
    expect(result.context).toEqual({ action: 'update' })
  })

  it('handles unknown error type', () => {
    const error = null
    const result = handleError(error, { action: 'delete' })
    expect(result).toBeInstanceOf(AppError)
    expect(result.message).toBe('An unknown error occurred')
    expect(result.code).toBe('UNKNOWN_ERROR')
    expect(result.context).toEqual({ action: 'delete' })
  })

  it('handles string error', () => {
    const error = 'String error'
    const result = handleError(error)
    expect(result).toBeInstanceOf(AppError)
    expect(result.code).toBe('UNKNOWN_ERROR')
  })

  it('handles number error', () => {
    const error = 12345
    const result = handleError(error)
    expect(result).toBeInstanceOf(AppError)
    expect(result.code).toBe('UNKNOWN_ERROR')
  })
})

describe('isAppError', () => {
  it('returns true for AppError instance', () => {
    const error = new AppError('Test error')
    expect(isAppError(error)).toBe(true)
  })

  it('returns false for generic Error', () => {
    const error = new Error('Test error')
    expect(isAppError(error)).toBe(false)
  })

  it('returns false for object with message', () => {
    const error = { message: 'Test error' }
    expect(isAppError(error)).toBe(false)
  })

  it('returns false for null', () => {
    expect(isAppError(null)).toBe(false)
  })

  it('returns false for undefined', () => {
    expect(isAppError(undefined)).toBe(false)
  })

  it('returns false for string', () => {
    expect(isAppError('error')).toBe(false)
  })
})
