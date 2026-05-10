import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ConfirmDialog, ConfirmProvider, useConfirm } from '@/shared/ui/confirm-dialog'
import { NextIntlClientProvider } from 'next-intl'
import messages from '../../messages/en.json'

const TestComponent = () => {
  const confirm = useConfirm()
  
  const handleClick = async () => {
    const result = await confirm('Are you sure?')
    console.log('Confirmed:', result)
  }

  return (
    <button onClick={handleClick}>
      Test Confirm
    </button>
  )
}

const createWrapper = () => ({ children }: { children: React.ReactNode }) => (
  <NextIntlClientProvider locale="en" messages={messages}>
    <ConfirmProvider>
      {children}
    </ConfirmProvider>
  </NextIntlClientProvider>
)

describe('ConfirmDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders ConfirmDialog with props', () => {
    const onOpenChange = vi.fn()
    const onConfirm = vi.fn()
    
    render(
      <ConfirmDialog
        open={true}
        onOpenChange={onOpenChange}
        onConfirm={onConfirm}
        title="Test Title"
        description="Test Description"
        confirmText="Confirm"
        cancelText="Cancel"
        variant="destructive"
      />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
    expect(screen.getByText('Confirm')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  it('calls onConfirm when confirm button is clicked', () => {
    const onOpenChange = vi.fn()
    const onConfirm = vi.fn()
    
    render(
      <ConfirmDialog
        open={true}
        onOpenChange={onOpenChange}
        onConfirm={onConfirm}
        title="Test Dialog"
        description="Test description for accessibility"
      />,
      { wrapper: createWrapper() }
    )

    const confirmButton = screen.getByRole('button', { name: 'Confirm' })
    fireEvent.click(confirmButton)

    expect(onConfirm).toHaveBeenCalled()
    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('calls onOpenChange when cancel button is clicked', () => {
    const onOpenChange = vi.fn()
    const onConfirm = vi.fn()
    
    render(
      <ConfirmDialog
        open={true}
        onOpenChange={onOpenChange}
        onConfirm={onConfirm}
        title="Test Dialog"
        description="Test description for accessibility"
      />,
      { wrapper: createWrapper() }
    )

    const cancelButton = screen.getByRole('button', { name: 'Cancel' })
    fireEvent.click(cancelButton)

    expect(onOpenChange).toHaveBeenCalledWith(false)
    expect(onConfirm).not.toHaveBeenCalled()
  })

  it('works with ConfirmProvider and useConfirm hook', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    render(<TestComponent />, { wrapper: createWrapper() })

    const button = screen.getByText('Test Confirm')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Are you sure?')).toBeInTheDocument()
    })

    const confirmButton = screen.getByRole('button', { name: 'Confirm' })
    fireEvent.click(confirmButton)

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Confirmed:', true)
    })

    consoleSpy.mockRestore()
  })

  it('handles cancel in ConfirmProvider', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    render(<TestComponent />, { wrapper: createWrapper() })

    const button = screen.getByText('Test Confirm')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Are you sure?')).toBeInTheDocument()
    })

    const cancelButton = screen.getByRole('button', { name: 'Cancel' })
    fireEvent.click(cancelButton)

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Confirmed:', false)
    })

    consoleSpy.mockRestore()
  })

  it('handles custom options in useConfirm', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    const TestComponentWithOptions = () => {
      const confirm = useConfirm()
      
      const handleClick = async () => {
        const result = await confirm({
          title: 'Custom Title',
          description: 'Custom Description',
          confirmText: 'Yes',
          cancelText: 'No',
          variant: 'default'
        })
        console.log('Confirmed:', result)
      }

      return (
        <button onClick={handleClick}>
          Test Custom Confirm
        </button>
      )
    }

    render(<TestComponentWithOptions />, { wrapper: createWrapper() })

    const button = screen.getByText('Test Custom Confirm')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Custom Title')).toBeInTheDocument()
      expect(screen.getByText('Custom Description')).toBeInTheDocument()
      expect(screen.getByText('Yes')).toBeInTheDocument()
      expect(screen.getByText('No')).toBeInTheDocument()
    })

    consoleSpy.mockRestore()
  })
})
