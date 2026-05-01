import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { analyticsApi } from '@/lib/api/analytics'
import { mockFetchResponse } from '../setup'

describe('analyticsApi', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { location: { href: '' } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
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
        const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
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
        const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
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
        const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
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
})
