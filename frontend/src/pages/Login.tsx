import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { DEMO_USERS, findDemoUser, isLoggedIn, saveLogin } from '../auth/demoAuth'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const sortedUsers = useMemo(
    () => [...DEMO_USERS].sort((a, b) => a.department.localeCompare(b.department)),
    [],
  )

  if (isLoggedIn()) {
    return <Navigate to="/dashboard" replace />
  }

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const user = findDemoUser(email, password)
    if (!user) {
      setError('Invalid demo credentials. Please use one of the listed users.')
      return
    }
    saveLogin(user)
    navigate('/dashboard', { replace: true })
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-100 to-[#f5f7f8] px-4 py-8 md:px-8 md:py-12">
      <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[1.25fr_1fr]">
        <section className="rounded-3xl border border-slate-200/80 bg-white p-7 shadow-sm md:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
            Xerago Intelligence
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
            Demo Sign In
          </h1>
          <p className="mt-2 text-base text-slate-500">
            Access the Xerago Intelligence Center with a department demo account.
          </p>

          <form className="mt-8 space-y-4" onSubmit={onSubmit}>
            <label className="flex flex-col gap-1.5">
              <span className="text-sm font-medium text-slate-700">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
                placeholder="name@xerago.demo"
              />
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-sm font-medium text-slate-700">Password</span>
              <input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
                placeholder="Xerago@123"
              />
            </label>
            {error ? (
              <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              className="mt-2 inline-flex h-11 w-full items-center justify-center rounded-xl bg-emerald-600 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
            >
              Sign In
            </button>
          </form>
        </section>

        <aside className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm md:p-8">
          <h2 className="text-lg font-semibold text-slate-900">Demo Users</h2>
          <p className="mt-1 text-sm text-slate-500">Password for all accounts: Xerago@123</p>
          <ul className="mt-4 space-y-3">
            {sortedUsers.map((user) => (
              <li
                key={user.email}
                className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
              >
                <p className="text-sm font-semibold text-slate-900">{user.department}</p>
                <p className="mt-1 text-sm text-slate-600">{user.email}</p>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </main>
  )
}
