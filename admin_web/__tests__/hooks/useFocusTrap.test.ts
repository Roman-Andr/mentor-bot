import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFocusTrap } from '@/hooks/use-focus-trap'

describe('useFocusTrap', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('returns a ref object', () => {
    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))
    expect(result.current).toHaveProperty('current')
    expect(result.current.current).toBeNull()
  })

  it('ref is assignable to HTMLDivElement', () => {
    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const div = document.createElement('div')
    result.current.current = div

    expect(result.current.current).toBe(div)
  })

  it('handles null container ref gracefully', () => {
    // Should not throw even when container ref is null
    expect(() => {
      renderHook(() => useFocusTrap<HTMLDivElement>(true))
    }).not.toThrow()
  })

  it('ref can be reassigned', () => {
    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const div1 = document.createElement('div')
    const div2 = document.createElement('div')

    result.current.current = div1
    expect(result.current.current).toBe(div1)

    result.current.current = div2
    expect(result.current.current).toBe(div2)
  })

  it('works with different element types', () => {
    const { result: dialogResult } = renderHook(() => useFocusTrap<HTMLDialogElement>(true))
    const { result: formResult } = renderHook(() => useFocusTrap<HTMLFormElement>(true))

    const dialog = document.createElement('dialog')
    const form = document.createElement('form')

    dialogResult.current.current = dialog
    formResult.current.current = form

    expect(dialogResult.current.current).toBe(dialog)
    expect(formResult.current.current).toBe(form)
  })

  it('handles enabled=true with container containing focusable elements', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
        <button id="btn2">Button 2</button>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    // Hook should mount without errors
    expect(result.current.current).toBe(container)
  })

  it('handles enabled=false', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(false))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })

  it('handles container with no focusable elements', () => {
    document.body.innerHTML = `
      <div id="container">
        <span>No buttons here</span>
        <p>Just text</p>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })

  it('handles various focusable element types', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn">Button</button>
        <a href="#" id="link">Link</a>
        <input id="input" />
        <select id="select"><option>Opt</option></select>
        <textarea id="textarea"></textarea>
        <div tabIndex={0} id="tabindex">Tabbable</div>
        <div contentEditable id="editable">Editable</div>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })

  it('handles disabled focusable elements', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="enabled">Enabled</button>
        <button id="disabled" disabled>Disabled</button>
        <input id="disabled-input" disabled />
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })

  it('handles elements with tabindex=-1', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn">Button</button>
        <div tabIndex="-1" id="skip">Should skip</div>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })

  it('cleans up on unmount', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
      </div>
    `

    const { result, unmount } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    // Unmount should not throw
    expect(() => unmount()).not.toThrow()
  })

  it('handles keyboard events when enabled', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
        <button id="btn2">Button 2</button>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    // Simulate Tab key - should not throw
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Tab', bubbles: true })
      document.dispatchEvent(event)
    })

    // Simulate Shift+Tab - should not throw
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true })
      document.dispatchEvent(event)
    })

    expect(result.current.current).toBe(container)
  })

  it('ignores non-Tab keyboard events', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    // Simulate Escape key - should not throw
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
      document.dispatchEvent(event)
    })

    // Simulate Enter key - should not throw
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })
      document.dispatchEvent(event)
    })

    expect(result.current.current).toBe(container)
  })

  it('handles toggling enabled state', () => {
    document.body.innerHTML = `
      <div id="container">
        <button id="btn1">Button 1</button>
      </div>
    `

    const { result, rerender } = renderHook(
      ({ enabled }) => useFocusTrap<HTMLDivElement>(enabled),
      { initialProps: { enabled: false } }
    )

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    // Enable the trap
    rerender({ enabled: true })
    expect(result.current.current).toBe(container)

    // Disable the trap
    rerender({ enabled: false })
    expect(result.current.current).toBe(container)
  })

  it('handles links without href', () => {
    document.body.innerHTML = `
      <div id="container">
        <a id="no-href">No href</a>
        <a href="/path" id="with-href">With href</a>
      </div>
    `

    const { result } = renderHook(() => useFocusTrap<HTMLDivElement>(true))

    const container = document.getElementById('container') as HTMLDivElement
    result.current.current = container

    expect(result.current.current).toBe(container)
  })
})
