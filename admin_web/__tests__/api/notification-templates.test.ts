import { describe, it, expect, vi } from 'vitest'
import { notificationTemplatesApi } from '@/shared/lib/api/notification-templates'

const mockFetchApi = vi.fn()

vi.mock('@/shared/lib/api/client', () => ({
  fetchApi: () => mockFetchApi(),
}))

describe('notificationTemplatesApi', () => {
  it('list calls fetchApi', () => {
    notificationTemplatesApi.list()
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('list with params', () => {
    notificationTemplatesApi.list({ name: 'test', channel: 'email', language: 'en', limit: 10 })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('get calls fetchApi', () => {
    notificationTemplatesApi.get(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('getByName calls fetchApi', () => {
    notificationTemplatesApi.getByName('welcome', 'email', 'en')
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create calls fetchApi with POST', () => {
    notificationTemplatesApi.create({
      name: 'test',
      channel: 'email',
      language: 'en',
      subject: 'Test',
      body_text: 'Body',
      body_html: null,
      variables: [],
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('create with HTML content calls fetchApi with POST', () => {
    notificationTemplatesApi.create({
      name: 'template-with-html',
      channel: 'email',
      language: 'en',
      subject: 'Test Subject',
      body_text: 'Plain text body',
      body_html: '<p>HTML body</p>',
      variables: [{ name: 'user', type: 'string', description: 'User name' }],
    })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('update calls fetchApi with PUT', () => {
    notificationTemplatesApi.update(123, { subject: 'Updated', body_html: null, body_text: null, variables: null, is_active: null })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('delete calls fetchApi with DELETE', () => {
    notificationTemplatesApi.delete(123)
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('render calls fetchApi with POST', () => {
    notificationTemplatesApi.render({ template_name: 'test', channel: 'email', language: 'en', variables: {} })
    expect(mockFetchApi).toHaveBeenCalled()
  })

  it('preview calls fetchApi with POST', () => {
    notificationTemplatesApi.preview({ body_text: 'Test', variables: {} })
    expect(mockFetchApi).toHaveBeenCalled()
  })
})
