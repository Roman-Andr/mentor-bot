import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest'
import { analyticsApi } from '@/lib/api/analytics'
import { mockFetchResponse } from '../setup'

describe('analyticsApi', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('checklistStats', () => {
    it('calls fetchApi without params', async () => {
      mockFetchResponse({ total: 100, completed: 50 })
      await analyticsApi.checklistStats()
      expect(global.fetch).toHaveBeenCalled()
    })

    it('calls fetchApi with department_id', async () => {
      mockFetchResponse({ total: 50, completed: 25 })
      await analyticsApi.checklistStats({ department_id: 5 })
      expect(global.fetch).toHaveBeenCalled()
    })
  })

  describe('monthlyStats', () => {
    it('calls fetchApi with default months', async () => {
      mockFetchResponse([])
      await analyticsApi.monthlyStats()
      expect(global.fetch).toHaveBeenCalled()
    })

    it('calls fetchApi with custom months', async () => {
      mockFetchResponse([])
      await analyticsApi.monthlyStats(12)
      expect(global.fetch).toHaveBeenCalled()
    })
  })

  describe('completionTimeStats', () => {
    it('calls fetchApi', async () => {
      mockFetchResponse([])
      await analyticsApi.completionTimeStats()
      expect(global.fetch).toHaveBeenCalled()
    })
  })

  describe('onboardingProgress', () => {
    it('calls fetchApi', async () => {
      mockFetchResponse({ checklists: [] })
      await analyticsApi.onboardingProgress()
      expect(global.fetch).toHaveBeenCalled()
    })
  })

  describe('knowledge', () => {
    describe('summary', () => {
      it('fetches knowledge summary without date range', async () => {
        mockFetchResponse({
          total_views: 1000,
          unique_viewers: 500,
          total_articles: 50,
          avg_views_per_article: 20.0
        })

        const result = await analyticsApi.knowledge.summary()

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual({
            total_views: 1000,
            unique_viewers: 500,
            total_articles: 50,
            avg_views_per_article: 20.0
          })
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/summary',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })

      it('fetches knowledge summary with date range', async () => {
        mockFetchResponse({
          total_views: 500,
          unique_viewers: 250,
          total_articles: 25,
          avg_views_per_article: 20.0
        })

        const result = await analyticsApi.knowledge.summary({
          from_date: '2026-01-01',
          to_date: '2026-01-31'
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual({
            total_views: 500,
            unique_viewers: 250,
            total_articles: 25,
            avg_views_per_article: 20.0
          })
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/summary?from_date=2026-01-01&to_date=2026-01-31',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })
    })

    describe('topArticles', () => {
      it('fetches top articles with default limit', async () => {
        mockFetchResponse([
          {
            article_id: 1,
            title: 'Test Article',
            view_count: 100,
            unique_viewers: 50
          }
        ])

        const result = await analyticsApi.knowledge.topArticles()

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              article_id: 1,
              title: 'Test Article',
              view_count: 100,
              unique_viewers: 50
            }
          ])
        }
        const fetchCall = (global.fetch as Mock).mock.calls[0]
        expect(fetchCall[0]).toContain('/api/v1/knowledge/analytics/top-articles')
      })

      it('fetches top articles with custom limit and date range', async () => {
        mockFetchResponse([
          {
            article_id: 1,
            title: 'Test Article',
            view_count: 100,
            unique_viewers: 50
          }
        ])

        const result = await analyticsApi.knowledge.topArticles({
          from_date: '2026-01-01',
          to_date: '2026-01-31',
          limit: 5
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              article_id: 1,
              title: 'Test Article',
              view_count: 100,
              unique_viewers: 50
            }
          ])
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/top-articles?from_date=2026-01-01&to_date=2026-01-31&limit=5',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })
    })

    describe('timeseries', () => {
      it('fetches timeseries with day granularity', async () => {
        mockFetchResponse([
          {
            bucket: '2026-01-01T00:00:00',
            views: 42,
            unique_viewers: 17
          }
        ])

        const result = await analyticsApi.knowledge.timeseries({
          granularity: 'day'
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              bucket: '2026-01-01T00:00:00',
              views: 42,
              unique_viewers: 17
            }
          ])
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/views-timeseries?granularity=day',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })

      it('fetches timeseries with week granularity and date range', async () => {
        mockFetchResponse([
          {
            bucket: '2026-01-01T00:00:00',
            views: 42,
            unique_viewers: 17
          }
        ])

        const result = await analyticsApi.knowledge.timeseries({
          from_date: '2026-01-01',
          to_date: '2026-01-31',
          granularity: 'week'
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              bucket: '2026-01-01T00:00:00',
              views: 42,
              unique_viewers: 17
            }
          ])
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/views-timeseries?from_date=2026-01-01&to_date=2026-01-31&granularity=week',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })
    })

    describe('byCategory', () => {
      it('fetches views by category without date range', async () => {
        mockFetchResponse([
          {
            category_id: 1,
            category_name: 'Onboarding',
            view_count: 200
          }
        ])

        const result = await analyticsApi.knowledge.byCategory()

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              category_id: 1,
              category_name: 'Onboarding',
              view_count: 200
            }
          ])
        }
        const fetchCall = (global.fetch as Mock).mock.calls[0]
        expect(fetchCall[0]).toContain('/api/v1/knowledge/analytics/views-by-category')
      })

      it('fetches views by category with date range', async () => {
        mockFetchResponse([
          {
            category_id: 1,
            category_name: 'Onboarding',
            view_count: 200
          }
        ])

        const result = await analyticsApi.knowledge.byCategory({
          from_date: '2026-01-01',
          to_date: '2026-01-31'
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              category_id: 1,
              category_name: 'Onboarding',
              view_count: 200
            }
          ])
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/views-by-category?from_date=2026-01-01&to_date=2026-01-31',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })
    })

    describe('byTag', () => {
      it('fetches views by tag without date range', async () => {
        mockFetchResponse([
          {
            tag_id: 1,
            tag_name: 'hr',
            view_count: 150
          }
        ])

        const result = await analyticsApi.knowledge.byTag()

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              tag_id: 1,
              tag_name: 'hr',
              view_count: 150
            }
          ])
        }
        const fetchCall = (global.fetch as Mock).mock.calls[0]
        expect(fetchCall[0]).toContain('/api/v1/knowledge/analytics/views-by-tag')
      })

      it('fetches views by tag with date range', async () => {
        mockFetchResponse([
          {
            tag_id: 1,
            tag_name: 'hr',
            view_count: 150
          }
        ])

        const result = await analyticsApi.knowledge.byTag({
          from_date: '2026-01-01',
          to_date: '2026-01-31'
        })

        expect(result.success).toBe(true)
        if (result.success) {
          expect(result.data).toEqual([
            {
              tag_id: 1,
              tag_name: 'hr',
              view_count: 150
            }
          ])
        }
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/knowledge/analytics/views-by-tag?from_date=2026-01-01&to_date=2026-01-31',
          expect.objectContaining({
            credentials: 'include'
          })
        )
      })
    })
  })

  describe('search', () => {
    describe('summary', () => {
      it('fetches search summary without params', async () => {
        mockFetchResponse({ total_searches: 1000, unique_queries: 500 })
        await analyticsApi.search.summary()
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches search summary with department_id', async () => {
        mockFetchResponse({ total_searches: 500, unique_queries: 250 })
        await analyticsApi.search.summary({ department_id: 5 })
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches search summary with date range', async () => {
        mockFetchResponse({ total_searches: 500, unique_queries: 250 })
        await analyticsApi.search.summary({ from_date: '2026-01-01', to_date: '2026-01-31' })
        expect(global.fetch).toHaveBeenCalled()
      })
    })

    describe('topQueries', () => {
      it('fetches top queries without params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.topQueries()
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches top queries with limit', async () => {
        mockFetchResponse([])
        await analyticsApi.search.topQueries({ limit: 10 })
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches top queries with all params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.topQueries({
          from_date: '2026-01-01',
          to_date: '2026-01-31',
          department_id: 5,
          limit: 10
        })
        expect(global.fetch).toHaveBeenCalled()
      })
    })

    describe('zeroResults', () => {
      it('fetches zero results without params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.zeroResults()
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches zero results with all params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.zeroResults({
          from_date: '2026-01-01',
          to_date: '2026-01-31',
          department_id: 5,
          limit: 10
        })
        expect(global.fetch).toHaveBeenCalled()
      })
    })

    describe('byDepartment', () => {
      it('fetches by department without params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.byDepartment()
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches by department with date range', async () => {
        mockFetchResponse([])
        await analyticsApi.search.byDepartment({
          from_date: '2026-01-01',
          to_date: '2026-01-31'
        })
        expect(global.fetch).toHaveBeenCalled()
      })
    })

    describe('timeseries', () => {
      it('fetches search timeseries without params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.timeseries()
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches search timeseries with granularity', async () => {
        mockFetchResponse([])
        await analyticsApi.search.timeseries({ granularity: 'day' })
        expect(global.fetch).toHaveBeenCalled()
      })

      it('fetches search timeseries with all params', async () => {
        mockFetchResponse([])
        await analyticsApi.search.timeseries({
          from_date: '2026-01-01',
          to_date: '2026-01-31',
          granularity: 'week'
        })
        expect(global.fetch).toHaveBeenCalled()
      })
    })
  })
})
