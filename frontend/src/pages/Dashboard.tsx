import AIInActionToday from '../components/dashboard/AIInActionToday'
import { clearLogin } from '../auth/demoAuth'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const navigate = useNavigate()

  const logout = () => {
    clearLogin()
    navigate('/login', { replace: true })
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-100 to-[#f5f7f8] py-6 md:py-10">
      <AIInActionToday onLogout={logout} />
    </main>
  )
}
