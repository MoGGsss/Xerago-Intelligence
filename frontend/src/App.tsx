import { Navigate, Route, Routes } from 'react-router-dom'
import { isLoggedIn } from './auth/demoAuth'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'

function ProtectedDashboard() {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return <Dashboard />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<ProtectedDashboard />} />
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
