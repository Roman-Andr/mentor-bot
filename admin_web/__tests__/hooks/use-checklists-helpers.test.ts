import { describe, it, expect } from 'vitest'
import { mapToItem, toCreatePayload, toUpdatePayload, toForm } from '@/hooks/use-checklists'
import type { ChecklistItem, ChecklistFormData } from '@/hooks/use-checklists'

describe('use-checklists helper functions', () => {
  const mockChecklistItem: ChecklistItem = {
    id: 1,
    userId: 2,
    employeeId: 'EMP-001',
    templateId: 3,
    status: 'IN_PROGRESS',
    progressPercentage: 50,
    completedTasks: 2,
    totalTasks: 4,
    startDate: '2024-01-01',
    dueDate: '2024-02-01',
    mentorId: 5,
    hrId: 6,
    notes: 'Some notes',
    isOverdue: false,
    daysRemaining: 10,
    userName: 'Test User',
    completedAt: null,
    createdAt: '2024-01-01T00:00:00Z',
    certUid: null,
  }

  describe('mapToItem', () => {
    it('maps checklist data to ChecklistItem correctly', () => {
      const data = {
        id: 1,
        user_id: 2,
        employee_id: 'EMP-001',
        template_id: 3,
        status: 'IN_PROGRESS',
        progress_percentage: 50,
        completed_tasks: 2,
        total_tasks: 4,
        start_date: '2024-01-01',
        due_date: '2024-02-01',
        mentor_id: 5,
        hr_id: 6,
        notes: 'Some notes',
        is_overdue: false,
        days_remaining: 10,
        completed_at: null,
        created_at: '2024-01-01T00:00:00Z',
        cert_uid: null,
      }

      const result = mapToItem(data, new Map())

      expect(result.id).toBe(1)
      expect(result.userId).toBe(2)
      expect(result.employeeId).toBe('EMP-001')
      expect(result.status).toBe('IN_PROGRESS')
      expect(result.progressPercentage).toBe(50)
      expect(result.completedTasks).toBe(2)
      expect(result.totalTasks).toBe(4)
    })
  })

  describe('toCreatePayload', () => {
    it('maps form data to create payload correctly', () => {
      const formData: ChecklistFormData = {
        user_id: 2,
        employee_id: 'EMP-001',
        template_id: 3,
        start_date: '2024-01-01',
        due_date: '2024-02-01',
        mentor_id: 5,
        hr_id: 6,
        notes: 'Some notes',
      }

      const result = toCreatePayload(formData)

      expect(result.user_id).toBe(2)
      expect(result.employee_id).toBe('EMP-001')
      expect(result.template_id).toBe(3)
      expect(result.mentor_id).toBe(5)
      expect(result.hr_id).toBe(6)
      expect(result.notes).toBe('Some notes')
    })

    it('converts empty notes to null', () => {
      const formData: ChecklistFormData = {
        user_id: 2,
        employee_id: 'EMP-001',
        template_id: 3,
        start_date: '2024-01-01',
        due_date: '',
        mentor_id: null,
        hr_id: null,
        notes: '',
      }

      const result = toCreatePayload(formData)
      expect(result.notes).toBeNull()
      expect(result.due_date).toBeNull()
    })
  })

  describe('toUpdatePayload', () => {
    it('maps form data to update payload correctly', () => {
      const formData: ChecklistFormData = {
        user_id: 2,
        employee_id: 'EMP-001',
        template_id: 3,
        start_date: '2024-01-01',
        due_date: '2024-02-01',
        mentor_id: 5,
        hr_id: 6,
        notes: 'Updated notes',
      }

      const result = toUpdatePayload(formData)

      expect(result.mentor_id).toBe(5)
      expect(result.hr_id).toBe(6)
      expect(result.notes).toBe('Updated notes')
    })

    it('converts empty notes to null', () => {
      const formData: ChecklistFormData = {
        user_id: 2,
        employee_id: 'EMP-001',
        template_id: 3,
        start_date: '2024-01-01',
        due_date: '',
        mentor_id: null,
        hr_id: null,
        notes: '',
      }

      const result = toUpdatePayload(formData)
      expect(result.notes).toBeNull()
      expect(result.mentor_id).toBeNull()
    })
  })

  describe('toForm', () => {
    it('maps ChecklistItem to form data correctly', () => {
      const result = toForm(mockChecklistItem)

      expect(result.user_id).toBe(2)
      expect(result.employee_id).toBe('EMP-001')
      expect(result.template_id).toBe(3)
      expect(result.start_date).toBe('2024-01-01')
      expect(result.due_date).toBe('2024-02-01')
      expect(result.mentor_id).toBe(5)
      expect(result.hr_id).toBe(6)
      expect(result.notes).toBe('Some notes')
    })

    it('handles null dueDate and notes', () => {
      const item: ChecklistItem = { ...mockChecklistItem, dueDate: null, notes: null }
      const result = toForm(item)

      expect(result.due_date).toBe('')
      expect(result.notes).toBe('')
    })
  })
})
