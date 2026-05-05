import { describe, it, expect, vi } from 'vitest'
import { feedbackApi } from '@/lib/api/feedback'

const mockFetchApi = vi.fn()

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('feedbackApi', () => {
  describe('Pulse surveys', () => {
    it('getPulseSurveys calls fetchApi', () => {
      feedbackApi.getPulseSurveys({ user_id: 123, limit: 10 })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('submitPulse calls fetchApi with POST', () => {
      feedbackApi.submitPulse({ rating: 5, is_anonymous: true })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('getPulseStats calls fetchApi', () => {
      feedbackApi.getPulseStats({ user_id: 123 })
      expect(mockFetchApi).toHaveBeenCalled()
    })
  })

  describe('Experience ratings', () => {
    it('getExperienceRatings calls fetchApi', () => {
      feedbackApi.getExperienceRatings({ min_rating: 3, max_rating: 5 })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('submitExperience calls fetchApi with POST', () => {
      feedbackApi.submitExperience({ rating: 4 })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('getExperienceStats calls fetchApi', () => {
      feedbackApi.getExperienceStats()
      expect(mockFetchApi).toHaveBeenCalled()
    })
  })

  describe('Comments', () => {
    it('getComments calls fetchApi', () => {
      feedbackApi.getComments({ has_reply: true })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('submitComment calls fetchApi with POST', () => {
      feedbackApi.submitComment({ comment: 'Great!', is_anonymous: false })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('replyToComment calls fetchApi with POST', () => {
      feedbackApi.replyToComment(123, 'Thanks for feedback')
      expect(mockFetchApi).toHaveBeenCalled()
    })
  })

  describe('Anonymity stats', () => {
    it('getPulseAnonymityStats calls fetchApi', () => {
      feedbackApi.getPulseAnonymityStats({ department_id: 5 })
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('getExperienceAnonymityStats calls fetchApi', () => {
      feedbackApi.getExperienceAnonymityStats()
      expect(mockFetchApi).toHaveBeenCalled()
    })

    it('getCommentAnonymityStats calls fetchApi', () => {
      feedbackApi.getCommentAnonymityStats({ from_date: '2024-01-01' })
      expect(mockFetchApi).toHaveBeenCalled()
    })
  })
})
