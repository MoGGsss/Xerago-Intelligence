import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { BarChart3 } from 'lucide-react'
import type { SystemStatusResponse } from '../../types/system'
import { getLastLoginAt } from '../../auth/demoAuth'
import SyncStatusIndicator from './SyncStatusIndicator'
import UserAccountMenu from './UserAccountMenu'

interface SectionHeaderProps {
  title: string
  subtitle: string
  dataLastUpdated?: string | null
  systemStatus?: SystemStatusResponse | null
  systemStatusLoading?: boolean
  userEmail?: string
  department?: string
  onLogout?: () => void
  headerControls?: ReactNode
}

export default function SectionHeader({
  title,
  subtitle,
  dataLastUpdated,
  systemStatus,
  systemStatusLoading = false,
  userEmail,
  department,
  onLogout,
  headerControls,
}: SectionHeaderProps) {
  const lastLoginAt = getLastLoginAt()

  return (
    <header className="border-b border-slate-100 pb-6">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              <span className="text-[10px]">●</span>
              <span>Intelligence Engine Active</span>
            </div>
            {headerControls}
          </div>
          <p className="mt-2 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
            Xerago Intelligence
          </p>
          <h1 className="mt-1 text-3xl font-semibold leading-tight tracking-[-0.02em] text-slate-900 md:text-4xl">
            {title}
          </h1>
          <p className="mt-1 text-base text-slate-500 md:text-lg">{subtitle}</p>
        </div>

        {userEmail ? (
          <div className="flex w-full flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-end xl:w-auto xl:max-w-[52rem] xl:shrink-0">
            <SyncStatusIndicator
              status={systemStatus ?? null}
              loading={systemStatusLoading}
              compact
            />
            <Link
              to="/analytics"
              className="inline-flex h-10 shrink-0 items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3.5 text-sm font-semibold text-emerald-800 transition-colors hover:border-emerald-300 hover:bg-emerald-100"
            >
              <BarChart3 className="h-4 w-4" aria-hidden />
              Executive Analytics
            </Link>
            <UserAccountMenu
              userEmail={userEmail}
              department={department}
              lastLoginAt={lastLoginAt}
              lastUpdated={dataLastUpdated ?? undefined}
              onLogout={onLogout}
            />
          </div>
        ) : null}
      </div>
    </header>
  )
}
