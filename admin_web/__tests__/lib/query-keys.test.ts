import { describe, it, expect } from 'vitest'
import { queryKeys, getEntityListKey } from '@/lib/query-keys'

describe('queryKeys', () => {
  it('exports queryKeys object', () => {
    expect(queryKeys).toBeDefined()
  })

  it('exports getEntityListKey function', () => {
    expect(typeof getEntityListKey).toBe('function')
  })

  it('departments.all returns correct key', () => {
    expect(queryKeys.departments.all).toEqual(['departments'])
  })

  it('departments.list returns correct key', () => {
    expect(queryKeys.departments.list({ page: 1 })).toEqual(['departments', 'list', { page: 1 }])
  })

  it('users.all returns correct key', () => {
    expect(queryKeys.users.all).toEqual(['users'])
  })

  it('users.list returns correct key', () => {
    expect(queryKeys.users.list({ page: 1 })).toEqual(['users', 'list', { page: 1 }])
  })

  it('users.detail returns correct key', () => {
    expect(queryKeys.users.detail(123)).toEqual(['users', 'detail', 123])
  })

  it('users.mentors returns correct key', () => {
    expect(queryKeys.users.mentors(123)).toEqual(['users', 'mentors', 123])
  })

  it('preferences returns correct key', () => {
    expect(queryKeys.preferences()).toEqual(['preferences'])
  })

  it('categories.all returns correct key', () => {
    expect(queryKeys.categories.all).toEqual(['categories'])
  })

  it('categories.list returns correct key', () => {
    expect(queryKeys.categories.list({ page: 1 })).toEqual(['categories', 'list', { page: 1 }])
  })

  it('categories.list without params returns correct key', () => {
    expect(queryKeys.categories.list()).toEqual(['categories', 'list', undefined])
  })

  it('categories.tree returns correct key', () => {
    expect(queryKeys.categories.tree()).toEqual(['categories', 'tree'])
  })

  it('articles.all returns correct key', () => {
    expect(queryKeys.articles.all).toEqual(['articles'])
  })

  it('articles.list returns correct key', () => {
    expect(queryKeys.articles.list({ page: 1 })).toEqual(['articles', 'list', { page: 1 }])
  })

  it('articles.detail returns correct key', () => {
    expect(queryKeys.articles.detail(123)).toEqual(['articles', 'detail', 123])
  })

  it('templates.all returns correct key', () => {
    expect(queryKeys.templates.all).toEqual(['templates'])
  })

  it('templates.list returns correct key', () => {
    expect(queryKeys.templates.list({ page: 1 })).toEqual(['templates', 'list', { page: 1 }])
  })

  it('templates.detail returns correct key', () => {
    expect(queryKeys.templates.detail(123)).toEqual(['templates', 'detail', 123])
  })

  it('templates.tasks returns correct key', () => {
    expect(queryKeys.templates.tasks(123)).toEqual(['templates', 'tasks', 123])
  })

  it('checklists.all returns correct key', () => {
    expect(queryKeys.checklists.all).toEqual(['checklists'])
  })

  it('checklists.list returns correct key', () => {
    expect(queryKeys.checklists.list({ page: 1 })).toEqual(['checklists', 'list', { page: 1 }])
  })

  it('checklists.detail returns correct key', () => {
    expect(queryKeys.checklists.detail(123)).toEqual(['checklists', 'detail', 123])
  })

  it('dialogues.all returns correct key', () => {
    expect(queryKeys.dialogues.all).toEqual(['dialogues'])
  })

  it('dialogues.list returns correct key', () => {
    expect(queryKeys.dialogues.list({ page: 1 })).toEqual(['dialogues', 'list', { page: 1 }])
  })

  it('dialogues.detail returns correct key', () => {
    expect(queryKeys.dialogues.detail(123)).toEqual(['dialogues', 'detail', 123])
  })

  it('dialogues.steps returns correct key', () => {
    expect(queryKeys.dialogues.steps(123)).toEqual(['dialogues', 'steps', 123])
  })

  it('meetings.all returns correct key', () => {
    expect(queryKeys.meetings.all).toEqual(['meetings'])
  })

  it('meetings.list returns correct key', () => {
    expect(queryKeys.meetings.list({ page: 1 })).toEqual(['meetings', 'list', { page: 1 }])
  })

  it('meetings.detail returns correct key', () => {
    expect(queryKeys.meetings.detail(123)).toEqual(['meetings', 'detail', 123])
  })

  it('userMeetings.all returns correct key', () => {
    expect(queryKeys.userMeetings.all).toEqual(['user-meetings'])
  })

  it('userMeetings.byMeeting returns correct key', () => {
    expect(queryKeys.userMeetings.byMeeting(123)).toEqual(['user-meetings', 'by-meeting', 123])
  })

  it('userMeetings.byUser returns correct key', () => {
    expect(queryKeys.userMeetings.byUser(123)).toEqual(['user-meetings', 'by-user', 123])
  })

  it('userMentors.all returns correct key', () => {
    expect(queryKeys.userMentors.all).toEqual(['user-mentors'])
  })

  it('userMentors.list returns correct key', () => {
    expect(queryKeys.userMentors.list({ page: 1 })).toEqual(['user-mentors', 'list', { page: 1 }])
  })

  it('userMentors.list without params returns correct key', () => {
    expect(queryKeys.userMentors.list()).toEqual(['user-mentors', 'list', undefined])
  })

  it('userMentors.byUser returns correct key', () => {
    expect(queryKeys.userMentors.byUser(123)).toEqual(['user-mentors', 'by-user', 123])
  })

  it('userMentors.byMentor returns correct key', () => {
    expect(queryKeys.userMentors.byMentor(123)).toEqual(['user-mentors', 'by-mentor', 123])
  })

  it('invitations.all returns correct key', () => {
    expect(queryKeys.invitations.all).toEqual(['invitations'])
  })

  it('invitations.list returns correct key', () => {
    expect(queryKeys.invitations.list({ page: 1 })).toEqual(['invitations', 'list', { page: 1 }])
  })

  it('escalations.all returns correct key', () => {
    expect(queryKeys.escalations.all).toEqual(['escalations'])
  })

  it('escalations.list returns correct key', () => {
    expect(queryKeys.escalations.list({ page: 1 })).toEqual(['escalations', 'list', { page: 1 }])
  })

  it('escalations.detail returns correct key', () => {
    expect(queryKeys.escalations.detail(123)).toEqual(['escalations', 'detail', 123])
  })

  it('notifications.all returns correct key', () => {
    expect(queryKeys.notifications.all).toEqual(['notifications'])
  })

  it('notifications.list returns correct key', () => {
    expect(queryKeys.notifications.list({ page: 1 })).toEqual(['notifications', 'list', { page: 1 }])
  })

  it('notifications.list without params returns correct key', () => {
    expect(queryKeys.notifications.list()).toEqual(['notifications', 'list', undefined])
  })

  it('notificationTemplates.all returns correct key', () => {
    expect(queryKeys.notificationTemplates.all).toEqual(['notification-templates'])
  })

  it('notificationTemplates.list returns correct key', () => {
    expect(queryKeys.notificationTemplates.list({ page: 1 })).toEqual(['notification-templates', 'list', { page: 1 }])
  })

  it('notificationTemplates.list without params returns correct key', () => {
    expect(queryKeys.notificationTemplates.list()).toEqual(['notification-templates', 'list', undefined])
  })

  it('notificationTemplates.detail returns correct key', () => {
    expect(queryKeys.notificationTemplates.detail(123)).toEqual(['notification-templates', 'detail', 123])
  })

  it('analytics.all returns correct key', () => {
    expect(queryKeys.analytics.all).toEqual(['analytics'])
  })

  it('analytics.overview returns correct key', () => {
    expect(queryKeys.analytics.overview()).toEqual(['analytics', 'overview'])
  })

  it('analytics.department returns correct key', () => {
    expect(queryKeys.analytics.department(123)).toEqual(['analytics', 'department', 123])
  })

  it('analytics.checklist returns correct key', () => {
    expect(queryKeys.analytics.checklist(123)).toEqual(['analytics', 'checklist', 123])
  })

  it('analytics.knowledge.summary returns correct key', () => {
    expect(queryKeys.analytics.knowledge.summary({ from_date: '2024-01-01' })).toEqual(['analytics', 'knowledge', 'summary', { from_date: '2024-01-01' }])
  })

  it('analytics.knowledge.summary without params returns correct key', () => {
    expect(queryKeys.analytics.knowledge.summary()).toEqual(['analytics', 'knowledge', 'summary', undefined])
  })

  it('analytics.knowledge.topArticles returns correct key', () => {
    expect(queryKeys.analytics.knowledge.topArticles({ limit: 10 })).toEqual(['analytics', 'knowledge', 'top-articles', { limit: 10 }])
  })

  it('analytics.knowledge.timeseries returns correct key', () => {
    expect(queryKeys.analytics.knowledge.timeseries({ granularity: 'day' })).toEqual(['analytics', 'knowledge', 'timeseries', { granularity: 'day' }])
  })

  it('analytics.knowledge.byCategory returns correct key', () => {
    expect(queryKeys.analytics.knowledge.byCategory({ from_date: '2024-01-01' })).toEqual(['analytics', 'knowledge', 'by-category', { from_date: '2024-01-01' }])
  })

  it('analytics.knowledge.byTag returns correct key', () => {
    expect(queryKeys.analytics.knowledge.byTag({ from_date: '2024-01-01' })).toEqual(['analytics', 'knowledge', 'by-tag', { from_date: '2024-01-01' }])
  })

  it('analytics.history.feed returns correct key', () => {
    expect(queryKeys.analytics.history.feed({ page: 1, page_size: 10 })).toEqual(['analytics', 'history', 'feed', { page: 1, page_size: 10 }])
  })

  it('dashboard.all returns correct key', () => {
    expect(queryKeys.dashboard.all).toEqual(['dashboard'])
  })

  it('dashboard.stats returns correct key', () => {
    expect(queryKeys.dashboard.stats()).toEqual(['dashboard', 'stats'])
  })

  it('dashboard.activity returns correct key', () => {
    expect(queryKeys.dashboard.activity()).toEqual(['dashboard', 'activity'])
  })

  it('dashboard.departments returns correct key', () => {
    expect(queryKeys.dashboard.departments()).toEqual(['dashboard', 'departments'])
  })

  it('feedback.all returns correct key', () => {
    expect(queryKeys.feedback.all).toEqual(['feedback'])
  })

  it('feedback.pulse returns correct key', () => {
    expect(queryKeys.feedback.pulse({ page: 1 })).toEqual(['feedback', 'pulse', { page: 1 }])
  })

  it('feedback.pulseStats returns correct key', () => {
    expect(queryKeys.feedback.pulseStats()).toEqual(['feedback', 'pulse', 'stats'])
  })

  it('feedback.pulseAnonymityStats returns correct key', () => {
    expect(queryKeys.feedback.pulseAnonymityStats()).toEqual(['feedback', 'pulse', 'anonymity-stats'])
  })

  it('feedback.experience returns correct key', () => {
    expect(queryKeys.feedback.experience({ page: 1 })).toEqual(['feedback', 'experience', { page: 1 }])
  })

  it('feedback.experienceStats returns correct key', () => {
    expect(queryKeys.feedback.experienceStats()).toEqual(['feedback', 'experience', 'stats'])
  })

  it('feedback.experienceAnonymityStats returns correct key', () => {
    expect(queryKeys.feedback.experienceAnonymityStats()).toEqual(['feedback', 'experience', 'anonymity-stats'])
  })

  it('feedback.comments returns correct key', () => {
    expect(queryKeys.feedback.comments({ page: 1 })).toEqual(['feedback', 'comments', { page: 1 }])
  })

  it('feedback.commentAnonymityStats returns correct key', () => {
    expect(queryKeys.feedback.commentAnonymityStats()).toEqual(['feedback', 'comments', 'anonymity-stats'])
  })

  it('getEntityListKey returns correct key for departments', () => {
    expect(getEntityListKey('departments')).toEqual(['departments'])
  })

  it('getEntityListKey returns correct key for users', () => {
    expect(getEntityListKey('users')).toEqual(['users'])
  })

  it('getEntityListKey returns correct key for preferences', () => {
    expect(getEntityListKey('preferences')).toEqual(['preferences'])
  })

  it('getEntityListKey returns correct key for categories', () => {
    expect(getEntityListKey('categories')).toEqual(['categories'])
  })

  it('getEntityListKey returns correct key for articles', () => {
    expect(getEntityListKey('articles')).toEqual(['articles'])
  })

  it('getEntityListKey returns correct key for templates', () => {
    expect(getEntityListKey('templates')).toEqual(['templates'])
  })

  it('getEntityListKey returns correct key for checklists', () => {
    expect(getEntityListKey('checklists')).toEqual(['checklists'])
  })

  it('getEntityListKey returns correct key for dialogues', () => {
    expect(getEntityListKey('dialogues')).toEqual(['dialogues'])
  })

  it('getEntityListKey returns correct key for meetings', () => {
    expect(getEntityListKey('meetings')).toEqual(['meetings'])
  })

  it('getEntityListKey returns correct key for userMeetings', () => {
    expect(getEntityListKey('userMeetings')).toEqual(['user-meetings'])
  })

  it('getEntityListKey returns correct key for userMentors', () => {
    expect(getEntityListKey('userMentors')).toEqual(['user-mentors'])
  })

  it('getEntityListKey returns correct key for invitations', () => {
    expect(getEntityListKey('invitations')).toEqual(['invitations'])
  })

  it('getEntityListKey returns correct key for escalations', () => {
    expect(getEntityListKey('escalations')).toEqual(['escalations'])
  })

  it('getEntityListKey returns correct key for notifications', () => {
    expect(getEntityListKey('notifications')).toEqual(['notifications'])
  })

  it('getEntityListKey returns correct key for notificationTemplates', () => {
    expect(getEntityListKey('notificationTemplates')).toEqual(['notification-templates'])
  })

  it('getEntityListKey returns correct key for analytics', () => {
    expect(getEntityListKey('analytics')).toEqual(['analytics'])
  })

  it('getEntityListKey returns correct key for dashboard', () => {
    expect(getEntityListKey('dashboard')).toEqual(['dashboard'])
  })

  it('getEntityListKey returns correct key for feedback', () => {
    expect(getEntityListKey('feedback')).toEqual(['feedback'])
  })
})
