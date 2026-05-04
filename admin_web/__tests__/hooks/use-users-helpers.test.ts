import { describe, it, expect } from 'vitest'
import { mapUser, toForm, toCreatePayload, toUpdatePayload } from '@/hooks/use-users'
import type { User } from '@/types'

describe('use-users helper functions', () => {
  const mockUser: User = {
    id: 1,
    telegram_id: 123456789,
    username: 'testuser',
    first_name: 'Ivan',
    last_name: 'Petrov',
    email: 'ivan.petrov@company.com',
    phone: '+7 (999) 123-45-67',
    employee_id: 'EMP-001',
    department_id: 1,
    department: { id: 1, name: 'Engineering', description: null, created_at: '2024-01-01T00:00:00Z', updated_at: null },
    position: 'Backend Developer',
    level: 'MIDDLE',
    hire_date: '2024-01-01T00:00:00Z',
    role: 'DEVELOPER',
    is_active: true,
    is_verified: true,
    created_at: '2024-01-01T00:00:00Z',
  }

  describe('mapUser', () => {
    it('maps User to UserItem correctly with all fields', () => {
      const result = mapUser(mockUser)

      expect(result.id).toBe(mockUser.id)
      expect(result.name).toBe('Ivan Petrov')
      expect(result.email).toBe(mockUser.email)
      expect(result.employee_id).toBe(mockUser.employee_id)
      expect(result.role).toBe(mockUser.role)
      expect(result.department_id).toBe(mockUser.department_id)
      expect(result.department).toBe('Engineering')
      expect(result.position).toBe(mockUser.position)
      expect(result.isActive).toBe(mockUser.is_active)
      expect(result.createdAt).toBe(mockUser.created_at)
      expect(result.telegram_id).toBe(mockUser.telegram_id)
      expect(result.phone).toBe(mockUser.phone)
    })

    it('handles null last_name correctly', () => {
      const userWithoutLastName: User = { ...mockUser, last_name: null }
      const result = mapUser(userWithoutLastName)

      expect(result.name).toBe('Ivan')
    })

    it('handles null phone correctly', () => {
      const userWithoutPhone: User = { ...mockUser, phone: null }
      const result = mapUser(userWithoutPhone)

      expect(result.phone).toBeNull()
    })

    it('handles null department correctly', () => {
      const userWithoutDepartment: User = { ...mockUser, department: null }
      const result = mapUser(userWithoutDepartment)

      expect(result.department).toBe('')
    })

    it('handles null position correctly', () => {
      const userWithoutPosition: User = { ...mockUser, position: null }
      const result = mapUser(userWithoutPosition)

      expect(result.position).toBe('')
    })

    it('handles null department_id correctly', () => {
      const userWithoutDepartmentId: User = { ...mockUser, department_id: null }
      const result = mapUser(userWithoutDepartmentId)

      expect(result.department_id).toBeNull()
    })
  })

  describe('toForm', () => {
    it('maps UserItem to UserFormData correctly with all fields', () => {
      const userItem = mapUser(mockUser)
      const result = toForm(userItem)

      expect(result.first_name).toBe('Ivan')
      expect(result.last_name).toBe('Petrov')
      expect(result.email).toBe(mockUser.email)
      expect(result.phone).toBe(mockUser.phone) // This was the bug - it was always ""
      expect(result.employee_id).toBe(mockUser.employee_id)
      expect(result.department_id).toBe(mockUser.department_id)
      expect(result.position).toBe(mockUser.position)
      expect(result.role).toBe(mockUser.role)
      expect(result.is_active).toBe(mockUser.is_active)
      expect(result.telegram_id).toBe(mockUser.telegram_id)
    })

    it('handles null phone by setting empty string', () => {
      const userItem = mapUser({ ...mockUser, phone: null })
      const result = toForm(userItem)

      expect(result.phone).toBe('')
    })

    it('handles undefined phone by setting empty string', () => {
      const userItem = mapUser({ ...mockUser, phone: undefined as any })
      const result = toForm(userItem)

      expect(result.phone).toBe('')
    })

    it('handles empty phone string correctly', () => {
      const userItem = mapUser({ ...mockUser, phone: '' })
      const result = toForm(userItem)

      expect(result.phone).toBe('')
    })

    it('splits name into first_name and last_name correctly', () => {
      const userItem = mapUser(mockUser)
      const result = toForm(userItem)

      expect(result.first_name).toBe('Ivan')
      expect(result.last_name).toBe('Petrov')
    })

    it('handles single-word name correctly', () => {
      const userItem = mapUser({ ...mockUser, last_name: null })
      const result = toForm(userItem)

      expect(result.first_name).toBe('Ivan')
      expect(result.last_name).toBe('')
    })

    it('handles multi-word last name correctly', () => {
      const userWithMultiWordLastName = mapUser({ ...mockUser, last_name: 'Van Der Berg' })
      const result = toForm(userWithMultiWordLastName)

      expect(result.last_name).toBe('Van Der Berg')
    })

    it('sets password to empty string', () => {
      const userItem = mapUser(mockUser)
      const result = toForm(userItem)

      expect(result.password).toBe('')
    })

    it('sets level to empty string', () => {
      const userItem = mapUser(mockUser)
      const result = toForm(userItem)

      expect(result.level).toBe('')
    })
  })

  describe('toCreatePayload', () => {
    const formData = {
      first_name: 'Ivan',
      last_name: 'Petrov',
      email: 'ivan.petrov@company.com',
      phone: '+7 (999) 123-45-67',
      employee_id: 'EMP-001',
      department_id: 1,
      position: 'Backend Developer',
      level: 'MIDDLE',
      role: 'DEVELOPER',
      is_active: true,
      password: 'securepassword123',
      telegram_id: 123456789,
    }

    it('maps UserFormData to create payload correctly', () => {
      const result = toCreatePayload(formData)

      expect(result.first_name).toBe(formData.first_name)
      expect(result.last_name).toBe(formData.last_name)
      expect(result.email).toBe(formData.email)
      expect(result.phone).toBe(formData.phone)
      expect(result.employee_id).toBe(formData.employee_id)
      expect(result.department_id).toBe(formData.department_id)
      expect(result.position).toBe(formData.position)
      expect(result.level).toBe(formData.level)
      expect(result.role).toBe(formData.role)
      expect(result.is_active).toBe(formData.is_active)
      expect(result.password).toBe(formData.password)
      expect(result.telegram_id).toBe(formData.telegram_id)
    })

    it('converts empty phone to null', () => {
      const formDataWithEmptyPhone = { ...formData, phone: '' }
      const result = toCreatePayload(formDataWithEmptyPhone)

      expect(result.phone).toBeNull()
    })

    it('converts null last_name to null', () => {
      const formDataWithNullLastName = { ...formData, last_name: null as any }
      const result = toCreatePayload(formDataWithNullLastName)

      expect(result.last_name).toBeNull()
    })

    it('converts empty position to null', () => {
      const formDataWithEmptyPosition = { ...formData, position: '' }
      const result = toCreatePayload(formDataWithEmptyPosition)

      expect(result.position).toBeNull()
    })

    it('converts empty level to null', () => {
      const formDataWithEmptyLevel = { ...formData, level: '' }
      const result = toCreatePayload(formDataWithEmptyLevel)

      expect(result.level).toBeNull()
    })

    it('converts department_id 0 to undefined', () => {
      const formDataWithZeroDept = { ...formData, department_id: 0 }
      const result = toCreatePayload(formDataWithZeroDept)

      expect(result.department_id).toBeUndefined()
    })

    it('includes password in payload', () => {
      const result = toCreatePayload(formData)

      expect(result.password).toBe(formData.password)
    })
  })

  describe('toUpdatePayload', () => {
    const formData = {
      first_name: 'Ivan',
      last_name: 'Petrov',
      email: 'ivan.petrov@company.com',
      phone: '+7 (999) 123-45-67',
      employee_id: 'EMP-001',
      department_id: 1,
      position: 'Backend Developer',
      level: 'MIDDLE',
      role: 'DEVELOPER',
      is_active: true,
      password: '',
      telegram_id: 123456789,
    }

    it('maps UserFormData to update payload correctly', () => {
      const result = toUpdatePayload(formData)

      expect(result.first_name).toBe(formData.first_name)
      expect(result.last_name).toBe(formData.last_name)
      expect(result.email).toBe(formData.email)
      expect(result.phone).toBe(formData.phone)
      expect(result.employee_id).toBe(formData.employee_id)
      expect(result.department_id).toBe(formData.department_id)
      expect(result.position).toBe(formData.position)
      expect(result.level).toBe(formData.level)
      expect(result.role).toBe(formData.role)
      expect(result.is_active).toBe(formData.is_active)
      expect(result.telegram_id).toBe(formData.telegram_id)
    })

    it('converts empty phone to null', () => {
      const formDataWithEmptyPhone = { ...formData, phone: '' }
      const result = toUpdatePayload(formDataWithEmptyPhone)

      expect(result.phone).toBeNull()
    })

    it('converts null last_name to null', () => {
      const formDataWithNullLastName = { ...formData, last_name: null as any }
      const result = toUpdatePayload(formDataWithNullLastName)

      expect(result.last_name).toBeNull()
    })

    it('converts empty position to null', () => {
      const formDataWithEmptyPosition = { ...formData, position: '' }
      const result = toUpdatePayload(formDataWithEmptyPosition)

      expect(result.position).toBeNull()
    })

    it('converts empty level to null', () => {
      const formDataWithEmptyLevel = { ...formData, level: '' }
      const result = toUpdatePayload(formDataWithEmptyLevel)

      expect(result.level).toBeNull()
    })

    it('converts department_id 0 to undefined', () => {
      const formDataWithZeroDept = { ...formData, department_id: 0 }
      const result = toUpdatePayload(formDataWithZeroDept)

      expect(result.department_id).toBeUndefined()
    })

    it('does not include password in update payload', () => {
      const result = toUpdatePayload(formData)

      expect(result).not.toHaveProperty('password')
    })

    it('handles null telegram_id correctly', () => {
      const formDataWithNullTelegram = { ...formData, telegram_id: null }
      const result = toUpdatePayload(formDataWithNullTelegram)

      expect(result.telegram_id).toBeNull()
    })
  })
})
