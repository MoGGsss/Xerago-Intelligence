import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { LogOut } from 'lucide-react'

export const APP_CHROME_MAX_W = 'max-w-[1600px]'
export const APP_CHROME_PX = 'px-5 sm:px-8 lg:px-12 xl:px-16'

interface AppNavbarProps {
  pageTitle: string
  pageSubtitle: string
  userEmail?: string
  department?: string
  onLogout?: () => void
  actionTo?: string
  actionLabel?: string
  actionIcon?: ReactNode
}

export default function AppNavbar({
  pageTitle,
  pageSubtitle,
  userEmail,
  department,
  onLogout,
  actionTo,
  actionLabel,
  actionIcon,
}: AppNavbarProps) {
  return (
    <header className="flex flex-col gap-4 py-5 md:flex-row md:items-center md:justify-between md:py-6">
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
          Xerago Intelligence
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">
          {pageTitle}
        </h1>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">{pageSubtitle}</p>
        {department || userEmail ? (
          <p className="mt-2 text-xs text-slate-500">
            {department ? (
              <span className="font-semibold text-slate-700">{department}</span>
            ) : null}
            {department && userEmail ? <span className="mx-1.5 text-slate-300">·</span> : null}
            {userEmail ? <span>{userEmail}</span> : null}
          </p>
        ) : null}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {actionTo && actionLabel ? (
          <Link
            to={actionTo}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 text-sm font-semibold text-slate-700 transition-colors hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
          >
            {actionIcon}
            {actionLabel}
          </Link>
        ) : null}
        {onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 text-sm font-semibold text-slate-700 transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
          >
            <LogOut className="h-4 w-4" aria-hidden />
            Logout
          </button>
        ) : null}
      </div>
    </header>
  )
}
