// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import EmployeeForm from './EmployeeForm'
import {
  createDepartment,
  getDepartments,
  normalizeDepartments,
} from '../services/departmentService'
import { createEmployee } from '../services/employeeService'

vi.mock('../services/departmentService', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    createDepartment: vi.fn(),
    getDepartments: vi.fn(),
  }
})

vi.mock('../services/employeeService', () => ({
  createEmployee: vi.fn(),
  getEmployee: vi.fn(),
  updateEmployee: vi.fn(),
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

function renderForm() {
  return render(
    <MemoryRouter>
      <EmployeeForm />
    </MemoryRouter>,
  )
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('department response normalization', () => {
  const departments = [{ id: 'department-1', name: 'Engineering' }]

  it.each([
    ['array', departments],
    ['items wrapper', { items: departments }],
    ['departments wrapper', { departments }],
    ['Axios array response', { data: departments }],
    ['Axios items response', { data: { items: departments } }],
  ])('supports %s', (_label, response) => {
    expect(normalizeDepartments(response)).toEqual(departments)
  })
})

describe('EmployeeForm department dropdown', () => {
  it('shows loading, populates options, and submits the selected department ID', async () => {
    let resolveDepartments
    getDepartments.mockReturnValue(
      new Promise((resolve) => {
        resolveDepartments = resolve
      }),
    )
    createEmployee.mockResolvedValue({ data: {} })
    const { container } = renderForm()
    const departmentSelect = container.querySelector(
      'select[name="department_id"]',
    )

    expect(departmentSelect).toBeTruthy()
    expect(screen.getByText('Loading departments...')).toBeTruthy()

    resolveDepartments({
      data: {
        items: [{ id: 'dept-uuid-123', name: 'Engineering' }],
      },
    })
    await screen.findByRole('option', { name: 'Engineering' })

    fireEvent.change(container.querySelector('input[name="first_name"]'), {
      target: { value: 'Aisha' },
    })
    fireEvent.change(container.querySelector('input[name="last_name"]'), {
      target: { value: 'Kumar' },
    })
    fireEvent.change(container.querySelector('input[name="email"]'), {
      target: { value: 'aisha@example.com' },
    })
    fireEvent.change(container.querySelector('input[name="password"]'), {
      target: { value: 'Employee123!' },
    })
    fireEvent.change(departmentSelect, {
      target: { value: 'dept-uuid-123' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create Employee' }))

    await waitFor(() => expect(createEmployee).toHaveBeenCalledOnce())
    expect(createEmployee.mock.calls[0][0].department_id).toBe('dept-uuid-123')
  })

  it('creates and selects a department without leaving the employee form', async () => {
    getDepartments.mockResolvedValue({ data: { departments: [] } })
    createDepartment.mockResolvedValue({
      data: { id: 'new-department-id', name: 'Engineering' },
    })
    const { container } = renderForm()

    await screen.findByRole('option', { name: 'No department (optional)' })
    fireEvent.click(screen.getByRole('button', { name: '+ Create department' }))
    fireEvent.change(screen.getByLabelText('Name *'), {
      target: { value: 'Engineering' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create and select' }))

    await waitFor(() => {
      expect(createDepartment).toHaveBeenCalledWith({
        name: 'Engineering',
        description: '',
      })
    })
    expect(container.querySelector('select[name="department_id"]').value)
      .toBe('new-department-id')
  })

  it('shows and logs a clear request error', async () => {
    const requestError = new Error('Network unavailable')
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    getDepartments.mockRejectedValue(requestError)
    renderForm()

    expect(
      await screen.findByText(
        'Unable to load departments. Please refresh the page and try again.',
      ),
    ).toBeTruthy()
    expect(consoleError).toHaveBeenCalledWith(
      'Failed to load departments:',
      requestError,
    )
    consoleError.mockRestore()
  })
})
