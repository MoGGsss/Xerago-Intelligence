import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { isLoggedIn } from './auth/demoAuth'
import Dashboard from './pages/Dashboard'
import ExecutiveAnalytics from './pages/ExecutiveAnalytics'
import Login from './pages/Login'

function requireAuth(element: ReactNode) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return element
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={requireAuth(<Dashboard />)} />
      <Route path="/analytics" element={requireAuth(<ExecutiveAnalytics />)} />
      <Route
        path="/"
        element={<Navigate to={isLoggedIn() ? '/dashboard' : '/login'} replace />}
      />
      <Route
        path="*"
        element={<Navigate to={isLoggedIn() ? '/dashboard' : '/login'} replace />}
      />
    </Routes>
  )
}

export default App
