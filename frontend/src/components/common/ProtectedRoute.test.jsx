// @vitest-environment jsdom

import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { AuthContext } from '../../contexts/AuthContext'
import ProtectedRoute from './ProtectedRoute'

function renderGuard(user, roles) {
  return render(
    <AuthContext.Provider value={{ user, loading: false }}>
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={roles}>
                <div>Protected content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/unauthorized" element={<div>Access denied page</div>} />
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('ProtectedRoute', () => {
  it('allows a user with the required role', () => {
    renderGuard({ role: 'admin' }, ['admin'])
    expect(screen.getByText('Protected content')).toBeTruthy()
  })

  it('redirects a user with the wrong role', () => {
    renderGuard({ role: 'employee' }, ['admin'])
    expect(screen.getByText('Access denied page')).toBeTruthy()
  })

  it('redirects an unauthenticated user to login', () => {
    renderGuard(null, ['admin'])
    expect(screen.getByText('Login page')).toBeTruthy()
  })
})
