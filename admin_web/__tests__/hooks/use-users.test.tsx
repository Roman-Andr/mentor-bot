import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NextIntlClientProvider } from 'next-intl'
import { ToastProvider } from '@/components/ui/toast'
import { PaginationContext } from '@/components/providers/pagination-provider'
import { useUsers, mapUser, toCreatePayload, toUpdatePayload, toForm, type UserItem, type UserFormData } from '@/hooks/use-users'
import { mockFetchResponse } from '../setup'

const MockPaginationProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <PaginationContext.Provider value={{ pageSize: 20, setPageSize: vi.fn() }}>
      {children}
    </PaginationContext.Provider>
  )
}

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <NextIntlClientProvider locale="en">
      <MockPaginationProvider>
        <ToastProvider>
          <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </ToastProvider>
      </MockPaginationProvider>
    </NextIntlClientProvider>
  )
}

describe('useUsers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('helper functions', () => {
    it('exports useUsers function', () => {
      expect(typeof useUsers).toBe('function')
    })

    describe('mapUser', () => {
      it('maps User to UserItem', () => {
        const user = {
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: 5,
          department: { id: 5, name: 'Engineering' },
          position: 'Developer',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          telegram_id: 123456,
          phone: '+1234567890',
        }

        const result = mapUser(user)
        expect(result.id).toBe(1)
        expect(result.name).toBe('John Doe')
        expect(result.email).toBe('john@example.com')
        expect(result.employee_id).toBe('EMP001')
        expect(result.role).toBe('NEWBIE')
        expect(result.department_id).toBe(5)
        expect(result.department).toBe('Engineering')
        expect(result.position).toBe('Developer')
        expect(result.isActive).toBe(true)
        expect(result.telegram_id).toBe(123456)
        expect(result.phone).toBe('+1234567890')
      })

      it('handles null last_name', () => {
        const user = {
          id: 1,
          first_name: 'John',
          last_name: null,
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: null,
          department: null,
          position: null,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          telegram_id: null,
          phone: null,
        }

        const result = mapUser(user)
        expect(result.name).toBe('John')
        expect(result.department).toBe('')
        expect(result.position).toBe('')
      })

      it('handles null department', () => {
        const user = {
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: null,
          department: null,
          position: null,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          telegram_id: null,
          phone: null,
        }

        const result = mapUser(user)
        expect(result.department).toBe('')
      })
    })

    describe('toCreatePayload', () => {
      it('converts form data to create payload', () => {
        const form: UserFormData = {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '+1234567890',
          employee_id: 'EMP001',
          department_id: 5,
          position: 'Developer',
          level: 'Senior',
          role: 'NEWBIE',
          is_active: true,
          password: 'password123',
          telegram_id: 123456,
        }

        const result = toCreatePayload(form)
        expect(result.first_name).toBe('John')
        expect(result.last_name).toBe('Doe')
        expect(result.email).toBe('john@example.com')
        expect(result.phone).toBe('+1234567890')
        expect(result.employee_id).toBe('EMP001')
        expect(result.department_id).toBe(5)
        expect(result.position).toBe('Developer')
        expect(result.level).toBe('Senior')
        expect(result.role).toBe('NEWBIE')
        expect(result.is_active).toBe(true)
        expect(result.password).toBe('password123')
        expect(result.telegram_id).toBe(123456)
      })

      it('handles null values correctly', () => {
        const form: UserFormData = {
          first_name: 'John',
          last_name: '',
          email: 'john@example.com',
          phone: '',
          employee_id: 'EMP001',
          department_id: 0,
          position: '',
          level: '',
          role: 'NEWBIE',
          is_active: true,
          password: 'password123',
          telegram_id: null,
        }

        const result = toCreatePayload(form)
        expect(result.last_name).toBeNull()
        expect(result.phone).toBeNull()
        expect(result.department_id).toBeUndefined()
        expect(result.position).toBeNull()
        expect(result.level).toBeNull()
      })
    })

    describe('toUpdatePayload', () => {
      it('converts form data to update payload', () => {
        const form: UserFormData = {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '+1234567890',
          employee_id: 'EMP001',
          department_id: 5,
          position: 'Developer',
          level: 'Senior',
          role: 'MENTOR',
          is_active: false,
          password: '',
          telegram_id: 123456,
        }

        const result = toUpdatePayload(form)
        expect(result.first_name).toBe('John')
        expect(result.last_name).toBe('Doe')
        expect(result.email).toBe('john@example.com')
        expect(result.phone).toBe('+1234567890')
        expect(result.employee_id).toBe('EMP001')
        expect(result.department_id).toBe(5)
        expect(result.position).toBe('Developer')
        expect(result.level).toBe('Senior')
        expect(result.role).toBe('MENTOR')
        expect(result.is_active).toBe(false)
        expect(result.telegram_id).toBe(123456)
        expect(result).not.toHaveProperty('password')
      })

      it('handles null values correctly', () => {
        const form: UserFormData = {
          first_name: 'John',
          last_name: '',
          email: 'john@example.com',
          phone: '',
          employee_id: 'EMP001',
          department_id: 0,
          position: '',
          level: '',
          role: 'NEWBIE',
          is_active: true,
          password: '',
          telegram_id: null,
        }

        const result = toUpdatePayload(form)
        expect(result.last_name).toBeNull()
        expect(result.phone).toBeNull()
        expect(result.department_id).toBeUndefined()
        expect(result.position).toBeNull()
        expect(result.level).toBeNull()
      })
    })

    describe('toForm', () => {
      it('converts UserItem to FormData', () => {
        const item: UserItem = {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: 5,
          department: 'Engineering',
          position: 'Developer',
          isActive: true,
          createdAt: '2024-01-01T00:00:00Z',
          telegram_id: 123456,
          phone: '+1234567890',
        }

        const result = toForm(item)
        expect(result.first_name).toBe('John')
        expect(result.last_name).toBe('Doe')
        expect(result.email).toBe('john@example.com')
        expect(result.employee_id).toBe('EMP001')
        expect(result.department_id).toBe(5)
        expect(result.position).toBe('Developer')
        expect(result.role).toBe('NEWBIE')
        expect(result.is_active).toBe(true)
        expect(result.telegram_id).toBe(123456)
        expect(result.phone).toBe('+1234567890')
        expect(result.password).toBe('')
        expect(result.level).toBe('')
      })

      it('handles single name', () => {
        const item: UserItem = {
          id: 1,
          name: 'John',
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: null,
          department: '',
          position: '',
          isActive: true,
          createdAt: '2024-01-01T00:00:00Z',
          telegram_id: null,
          phone: null,
        }

        const result = toForm(item)
        expect(result.first_name).toBe('John')
        expect(result.last_name).toBe('')
        expect(result.department_id).toBe(0)
      })

      it('handles null values', () => {
        const item: UserItem = {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          employee_id: 'EMP001',
          role: 'NEWBIE',
          department_id: null,
          department: '',
          position: '',
          isActive: true,
          createdAt: '2024-01-01T00:00:00Z',
          telegram_id: null,
          phone: null,
        }

        const result = toForm(item)
        expect(result.department_id).toBe(0)
        expect(result.phone).toBe('')
        expect(result.telegram_id).toBeNull()
      })
    })
  })

  describe('hook integration', () => {
    it('loads users list', async () => {
      mockFetchResponse({
        users: [
          { id: 1, first_name: 'John', last_name: 'Doe', email: 'john@example.com', employee_id: 'EMP001', role: 'NEWBIE', department_id: 5, department: { id: 5, name: 'Engineering' }, position: 'Developer', is_active: true, created_at: '2024-01-01T00:00:00Z' },
          { id: 2, first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com', employee_id: 'EMP002', role: 'MENTOR', department_id: 5, department: { id: 5, name: 'Engineering' }, position: 'Senior', is_active: true, created_at: '2024-01-02T00:00:00Z' },
        ],
        total: 2,
      })

      const { result } = renderHook(() => useUsers(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.users).toHaveLength(2)
      expect(result.current.users[0].name).toBe('John Doe')
      expect(result.current.totalUsers).toBe(2)
    })

    it('loads departments for filter', async () => {
      mockFetchResponse({
        users: [],
        total: 0,
      })

      const { result } = renderHook(() => useUsers(), { wrapper: createWrapper() })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(Array.isArray(result.current.departments)).toBe(true)
    })

    })
})
