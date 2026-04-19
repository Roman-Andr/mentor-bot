import { describe, it, expect } from 'vitest'
import { queryKeys, getEntityListKey } from '@/lib/query-keys'

describe('queryKeys', () => {
  describe('departments', () => {
    it('has correct all key', () => {
      expect(queryKeys.departments.all).toEqual(['departments'])
    })

    it('generates list key with params', () => {
      const params = { page: 1 }
      expect(queryKeys.departments.list(params)).toEqual(['departments', 'list', params])
    })
  })

  describe('users', () => {
    it('has correct all key', () => {
      expect(queryKeys.users.all).toEqual(['users'])
    })

    it('generates list key with params', () => {
      const params = { search: 'john' }
      expect(queryKeys.users.list(params)).toEqual(['users', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.users.detail(42)).toEqual(['users', 'detail', 42])
    })

    it('generates mentors key', () => {
      expect(queryKeys.users.mentors(5)).toEqual(['users', 'mentors', 5])
    })
  })

  describe('categories', () => {
    it('has correct all key', () => {
      expect(queryKeys.categories.all).toEqual(['categories'])
    })

    it('generates list key with optional params', () => {
      expect(queryKeys.categories.list()).toEqual(['categories', 'list', undefined])
      expect(queryKeys.categories.list({})).toEqual(['categories', 'list', {}])
    })

    it('generates tree key', () => {
      expect(queryKeys.categories.tree()).toEqual(['categories', 'tree'])
    })
  })

  describe('articles', () => {
    it('has correct all key', () => {
      expect(queryKeys.articles.all).toEqual(['articles'])
    })

    it('generates list key with params', () => {
      const params = { search: 'test' }
      expect(queryKeys.articles.list(params)).toEqual(['articles', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.articles.detail(1)).toEqual(['articles', 'detail', 1])
    })
  })

  describe('attachments', () => {
    it('has correct all key', () => {
      expect(queryKeys.attachments.all).toEqual(['attachments'])
    })

    it('generates byArticle key', () => {
      expect(queryKeys.attachments.byArticle(10)).toEqual(['attachments', 'article', 10])
    })
  })

  describe('templates', () => {
    it('has correct all key', () => {
      expect(queryKeys.templates.all).toEqual(['templates'])
    })

    it('generates list key with params', () => {
      const params = { page: 1 }
      expect(queryKeys.templates.list(params)).toEqual(['templates', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.templates.detail(7)).toEqual(['templates', 'detail', 7])
    })

    it('generates tasks key', () => {
      expect(queryKeys.templates.tasks(7)).toEqual(['templates', 'tasks', 7])
    })
  })

  describe('checklists', () => {
    it('has correct all key', () => {
      expect(queryKeys.checklists.all).toEqual(['checklists'])
    })

    it('generates list key with params', () => {
      const params = { status: 'active' }
      expect(queryKeys.checklists.list(params)).toEqual(['checklists', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.checklists.detail(123)).toEqual(['checklists', 'detail', 123])
    })
  })

  describe('dialogues', () => {
    it('has correct all key', () => {
      expect(queryKeys.dialogues.all).toEqual(['dialogues'])
    })

    it('generates list key with params', () => {
      const params = { userId: 1 }
      expect(queryKeys.dialogues.list(params)).toEqual(['dialogues', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.dialogues.detail(5)).toEqual(['dialogues', 'detail', 5])
    })

    it('generates steps key', () => {
      expect(queryKeys.dialogues.steps(10)).toEqual(['dialogues', 'steps', 10])
    })
  })

  describe('meetings', () => {
    it('has correct all key', () => {
      expect(queryKeys.meetings.all).toEqual(['meetings'])
    })

    it('generates list key with params', () => {
      const params = { date: '2024-01-01' }
      expect(queryKeys.meetings.list(params)).toEqual(['meetings', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.meetings.detail(1)).toEqual(['meetings', 'detail', 1])
    })
  })

  describe('userMeetings', () => {
    it('has correct all key', () => {
      expect(queryKeys.userMeetings.all).toEqual(['user-meetings'])
    })

    it('generates byMeeting key', () => {
      expect(queryKeys.userMeetings.byMeeting(5)).toEqual(['user-meetings', 'by-meeting', 5])
    })

    it('generates byUser key', () => {
      expect(queryKeys.userMeetings.byUser(3)).toEqual(['user-meetings', 'by-user', 3])
    })
  })

  describe('userMentors', () => {
    it('has correct all key', () => {
      expect(queryKeys.userMentors.all).toEqual(['user-mentors'])
    })

    it('generates list key with optional params', () => {
      expect(queryKeys.userMentors.list()).toEqual(['user-mentors', 'list', undefined])
    })

    it('generates byUser key', () => {
      expect(queryKeys.userMentors.byUser(1)).toEqual(['user-mentors', 'by-user', 1])
    })

    it('generates byMentor key', () => {
      expect(queryKeys.userMentors.byMentor(2)).toEqual(['user-mentors', 'by-mentor', 2])
    })
  })

  describe('invitations', () => {
    it('has correct all key', () => {
      expect(queryKeys.invitations.all).toEqual(['invitations'])
    })

    it('generates list key with params', () => {
      const params = { status: 'pending' }
      expect(queryKeys.invitations.list(params)).toEqual(['invitations', 'list', params])
    })
  })

  describe('escalations', () => {
    it('has correct all key', () => {
      expect(queryKeys.escalations.all).toEqual(['escalations'])
    })

    it('generates list key with params', () => {
      const params = { status: 'open' }
      expect(queryKeys.escalations.list(params)).toEqual(['escalations', 'list', params])
    })

    it('generates detail key', () => {
      expect(queryKeys.escalations.detail(1)).toEqual(['escalations', 'detail', 1])
    })
  })

  describe('notifications', () => {
    it('has correct all key', () => {
      expect(queryKeys.notifications.all).toEqual(['notifications'])
    })

    it('generates list key with optional params', () => {
      expect(queryKeys.notifications.list()).toEqual(['notifications', 'list', undefined])
    })
  })

  describe('analytics', () => {
    it('has correct all key', () => {
      expect(queryKeys.analytics.all).toEqual(['analytics'])
    })

    it('generates overview key', () => {
      expect(queryKeys.analytics.overview()).toEqual(['analytics', 'overview'])
    })

    it('generates department key', () => {
      expect(queryKeys.analytics.department(3)).toEqual(['analytics', 'department', 3])
    })

    it('generates checklist key', () => {
      expect(queryKeys.analytics.checklist(5)).toEqual(['analytics', 'checklist', 5])
    })
  })

  describe('dashboard', () => {
    it('has correct all key', () => {
      expect(queryKeys.dashboard.all).toEqual(['dashboard'])
    })

    it('generates stats key', () => {
      expect(queryKeys.dashboard.stats()).toEqual(['dashboard', 'stats'])
    })

    it('generates activity key', () => {
      expect(queryKeys.dashboard.activity()).toEqual(['dashboard', 'activity'])
    })

    it('generates departments key', () => {
      expect(queryKeys.dashboard.departments()).toEqual(['dashboard', 'departments'])
    })
  })

  describe('feedback', () => {
    it('has correct all key', () => {
      expect(queryKeys.feedback.all).toEqual(['feedback'])
    })

    it('generates pulse key with params', () => {
      const params = { period: 'weekly' }
      expect(queryKeys.feedback.pulse(params)).toEqual(['feedback', 'pulse', params])
    })

    it('generates pulse stats key', () => {
      expect(queryKeys.feedback.pulseStats()).toEqual(['feedback', 'pulse', 'stats'])
    })

    it('generates pulse anonymity stats key', () => {
      expect(queryKeys.feedback.pulseAnonymityStats()).toEqual(['feedback', 'pulse', 'anonymity-stats'])
    })

    it('generates experience key with params', () => {
      const params = { period: 'monthly' }
      expect(queryKeys.feedback.experience(params)).toEqual(['feedback', 'experience', params])
    })

    it('generates experience stats key', () => {
      expect(queryKeys.feedback.experienceStats()).toEqual(['feedback', 'experience', 'stats'])
    })

    it('generates experience anonymity stats key', () => {
      expect(queryKeys.feedback.experienceAnonymityStats()).toEqual(['feedback', 'experience', 'anonymity-stats'])
    })

    it('generates comments key with params', () => {
      const params = { category: 'general' }
      expect(queryKeys.feedback.comments(params)).toEqual(['feedback', 'comments', params])
    })

    it('generates comment anonymity stats key', () => {
      expect(queryKeys.feedback.commentAnonymityStats()).toEqual(['feedback', 'comments', 'anonymity-stats'])
    })
  })
})

describe('getEntityListKey', () => {
  it('returns list key for departments', () => {
    expect(getEntityListKey('departments')).toEqual(['departments'])
  })

  it('returns list key for users', () => {
    expect(getEntityListKey('users')).toEqual(['users'])
  })

  it('returns list key for checklists', () => {
    expect(getEntityListKey('checklists')).toEqual(['checklists'])
  })

  it('returns list key for articles', () => {
    expect(getEntityListKey('articles')).toEqual(['articles'])
  })

  it('returns list key for templates', () => {
    expect(getEntityListKey('templates')).toEqual(['templates'])
  })

  it('returns list key for dialogues', () => {
    expect(getEntityListKey('dialogues')).toEqual(['dialogues'])
  })

  it('returns list key for meetings', () => {
    expect(getEntityListKey('meetings')).toEqual(['meetings'])
  })

  it('returns list key for escalations', () => {
    expect(getEntityListKey('escalations')).toEqual(['escalations'])
  })

  it('returns list key for invitations', () => {
    expect(getEntityListKey('invitations')).toEqual(['invitations'])
  })

  it('returns list key for analytics', () => {
    expect(getEntityListKey('analytics')).toEqual(['analytics'])
  })

  it('returns list key for dashboard', () => {
    expect(getEntityListKey('dashboard')).toEqual(['dashboard'])
  })

  it('returns list key for feedback', () => {
    expect(getEntityListKey('feedback')).toEqual(['feedback'])
  })

  it('returns list key for notifications', () => {
    expect(getEntityListKey('notifications')).toEqual(['notifications'])
  })

  it('returns list key for userMeetings', () => {
    expect(getEntityListKey('userMeetings')).toEqual(['user-meetings'])
  })

  it('returns list key for userMentors', () => {
    expect(getEntityListKey('userMentors')).toEqual(['user-mentors'])
  })

  it('returns list key for attachments', () => {
    expect(getEntityListKey('attachments')).toEqual(['attachments'])
  })

  it('returns list key for categories', () => {
    expect(getEntityListKey('categories')).toEqual(['categories'])
  })

  it('returns fallback for unknown entity', () => {
    // @ts-expect-error - testing unknown entity
    expect(getEntityListKey('unknown')).toEqual(['unknown'])
  })
})
