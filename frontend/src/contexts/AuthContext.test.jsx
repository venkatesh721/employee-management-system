// @vitest-environment jsdom

import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { AuthProvider } from './AuthContext'
import { useAuth } from '../hooks/useAuth'
import { getProfile, logoutApi } from '../services/authService'

vi.mock('../services/authService', () => ({
  login: vi.fn(),
  getProfile: vi.fn(),
  logoutApi: vi.fn(),
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

function SessionProbe() {
  const { user, logout } = useAuth()
  const location = useLocation()
  return (
    <>
      <span>{location.pathname}</span>
      <span>{user?.role || 'no-user'}</span>
      <button type="button" onClick={logout}>Logout</button>
    </>
  )
}

function renderSession(initialPath) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <SessionProbe />
      </AuthProvider>
    </MemoryRouter>,
  )
}

afterEach(() => {
  cleanup()
  localStorage.clear()
  vi.clearAllMocks()
})

describe('AuthProvider logout navigation', () => {
  it.each([
    ['admin', '/admin/dashboard'],
    ['employee', '/employee/dashboard'],
  ])('clears the %s session and routes to login', async (role, initialPath) => {
    localStorage.setItem('token', 'stored-token')
    localStorage.setItem('user', JSON.stringify({ role }))
    getProfile.mockResolvedValue({ data: { id: 'user-1', role } })
    logoutApi.mockResolvedValue({ data: {} })
    renderSession(initialPath)

    await screen.findByText(role)
    fireEvent.click(screen.getByRole('button', { name: 'Logout' }))

    await screen.findByText('/login')
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
    expect(screen.getByText('no-user')).toBeTruthy()
    expect(logoutApi).toHaveBeenCalledOnce()
  })

  it('routes an expired API session to login without a page reload', async () => {
    localStorage.setItem('token', 'expired-token')
    getProfile.mockResolvedValue({ data: { id: 'user-1', role: 'admin' } })
    renderSession('/admin/employees')
    await screen.findByText('admin')

    window.dispatchEvent(new CustomEvent('auth:unauthorized'))

    await waitFor(() => expect(screen.getByText('/login')).toBeTruthy())
    expect(localStorage.getItem('token')).toBeNull()
    expect(screen.getByText('no-user')).toBeTruthy()
  })
})
