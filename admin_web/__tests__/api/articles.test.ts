import { describe, it, expect, vi } from 'vitest'
import { articlesApi, categoriesApi, attachmentsApi } from '@/lib/api/articles'

const mockFetchApi = vi.fn()
const mockFetchUpload = vi.fn()
const mockBuildQueryString = vi.fn(() => '')

vi.mock('@/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
  fetchUpload: () => mockFetchUpload(),
}))

vi.mock('@/lib/utils/query-builder', () => ({
  buildQueryString: () => mockBuildQueryString(),
}))

describe('articlesApi', () => {
  it('list calls fetchApi', () => {
    articlesApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    articlesApi.list({ status: 'published', category_id: 5, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with all params', () => {
    articlesApi.list({
      status: 'published',
      category_id: 5,
      department_id: 10,
      search: 'test',
      skip: 0,
      limit: 10,
      pinned_only: true,
      featured_only: true,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with only status', () => {
    articlesApi.list({ status: 'draft' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with only search', () => {
    articlesApi.list({ search: 'keyword' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with only skip and limit', () => {
    articlesApi.list({ skip: 5, limit: 20 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get with number id', () => {
    articlesApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get with string id', () => {
    articlesApi.get('123')
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with minimal data', () => {
    articlesApi.create({ title: 'Test', content: 'Content' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields', () => {
    articlesApi.create({
      title: 'Test',
      content: 'Content',
      excerpt: 'Excerpt',
      category_id: 5,
      department_id: 10,
      position: 'manager',
      level: 'senior',
      status: 'published',
      is_pinned: true,
      is_featured: true,
      keywords: ['test', 'article'],
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with null category_id', () => {
    articlesApi.create({
      title: 'Test',
      content: 'Content',
      category_id: null,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with single field', () => {
    articlesApi.update(123, { title: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with multiple fields', () => {
    articlesApi.update(123, {
      title: 'Updated',
      content: 'New content',
      status: 'published',
      is_pinned: false,
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with all fields', () => {
    articlesApi.update(123, {
      title: 'Updated',
      content: 'New content',
      excerpt: 'New excerpt',
      category_id: 5,
      department_id: 10,
      position: 'lead',
      level: 'expert',
      status: 'published',
      is_pinned: false,
      is_featured: false,
      keywords: ['updated'],
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    articlesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('publish calls fetchApi', () => {
    articlesApi.publish(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})

describe('categoriesApi', () => {
  it('list calls fetchApi', () => {
    categoriesApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params calls fetchApi', () => {
    categoriesApi.list({ skip: 0, limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with parent_id calls fetchApi', () => {
    categoriesApi.list({ parent_id: 5 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with department_id calls fetchApi', () => {
    categoriesApi.list({ department_id: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with search calls fetchApi', () => {
    categoriesApi.list({ search: 'test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with include_tree calls fetchApi', () => {
    categoriesApi.list({ include_tree: true })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with all params calls fetchApi', () => {
    categoriesApi.list({ skip: 0, limit: 10, parent_id: 5, department_id: 10, search: 'test', include_tree: true })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi', () => {
    categoriesApi.create({ name: 'Test', slug: 'test' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with all fields calls fetchApi', () => {
    categoriesApi.create({
      name: 'Test',
      slug: 'test',
      description: 'Description',
      parent_id: 5,
      order: 1,
      department_id: 10,
      position: 'manager',
      level: 'senior',
      icon: 'icon',
      color: '#000000',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi', () => {
    categoriesApi.update(123, { name: 'Updated' })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update with all fields calls fetchApi', () => {
    categoriesApi.update(123, {
      name: 'Updated',
      description: 'New description',
      parent_id: 5,
      order: 2,
      department_id: 10,
      position: 'lead',
      level: 'expert',
      icon: 'new-icon',
      color: '#ffffff',
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    categoriesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })
})

describe('attachmentsApi', () => {
  it('listByArticle calls fetchApi', () => {
    attachmentsApi.listByArticle(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('upload calls fetchUpload', () => {
    const file = new File(['content'], 'test.pdf')
    attachmentsApi.upload(123, file)
    expect(mockFetchUpload).toHaveBeenCalled()
  })

  it('upload with description calls fetchUpload', () => {
    const file = new File(['content'], 'test.pdf')
    attachmentsApi.upload(123, file, 'Test description')
    expect(mockFetchUpload).toHaveBeenCalled()
  })

  it('uploadMultiple calls fetchUpload', () => {
    const files = [new File(['content1'], 'test1.pdf'), new File(['content2'], 'test2.pdf')]
    attachmentsApi.uploadMultiple(123, files)
    expect(mockFetchUpload).toHaveBeenCalled()
  })

  it('delete calls fetchApi', () => {
    attachmentsApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getDownloadUrl returns correct URL', () => {
    const url = attachmentsApi.getDownloadUrl(123, 'test.pdf')
    expect(url).toContain('/api/v1/attachments/file/123/')
    expect(url).toContain('test.pdf')
  })

  it('getDownloadUrl encodes filename', () => {
    const url = attachmentsApi.getDownloadUrl(123, 'test file.pdf')
    expect(url).toContain('test%20file.pdf')
  })
})
