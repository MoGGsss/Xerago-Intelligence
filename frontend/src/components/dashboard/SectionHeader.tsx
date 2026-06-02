import type { IntelligenceHeaderStats } from '../../utils/intelligenceStats'

interface SectionHeaderProps {
  title: string
  subtitle: string
  stats?: IntelligenceHeaderStats
  loading?: boolean
  userEmail?: string
  department?: string
  lastLoginAt?: string | null
  onLogout?: () => void
}

function formatDateTime(value: string): string {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(parsed)
}

export default function SectionHeader({
  title,
  subtitle,
  stats,
  loading = false,
  userEmail,
  department,
  lastLoginAt,
  onLogout,
}: SectionHeaderProps) {
  const avatarInitial = userEmail ? userEmail[0]?.toUpperCase() : 'U'

  return (
    <header className="mb-7 border-b border-slate-100 pb-7 md:mb-8 md:pb-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="max-w-3xl">
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          <span className="text-[10px]">●</span>
          <span>Intelligence Engine Active</span>
        </div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
          Xerago Intelligence
        </p>
        <h1 className="mt-2 text-3xl font-semibold leading-tight tracking-[-0.02em] text-slate-900 md:text-4xl">
          {title}
        </h1>
        <p className="mt-2 text-base leading-relaxed text-slate-500 md:text-lg">
          {subtitle}
        </p>
          {userEmail ? (
          <div className="mt-3 space-y-0.5">
            <p className="text-sm text-slate-500">
              Welcome back, <span className="font-medium text-slate-700">{userEmail}</span>
            </p>
            <p className="text-sm text-slate-500">
              Department: <span className="font-medium text-slate-700">{department ?? 'General'}</span>
            </p>
            {lastLoginAt ? (
              <p className="text-sm text-slate-500">
                Last login:{' '}
                <span className="font-medium text-slate-700">{formatDateTime(lastLoginAt)}</span>
              </p>
            ) : null}
          </div>
        ) : null}
        {!loading && stats?.lastUpdated ? (
          <p className="mt-3 text-sm text-slate-400">
            Last updated{' '}
            <time className="font-medium text-slate-600">{stats.lastUpdated}</time>
          </p>
        ) : null}
        {loading ? (
          <div className="mt-3 h-4 w-48 animate-pulse rounded bg-slate-100" />
        ) : null}
        </div>
        {userEmail ? (
          <div className="flex items-center gap-3">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-slate-100 text-sm font-semibold text-slate-700">
              {avatarInitial}
            </div>
            {onLogout ? (
              <button
                type="button"
                onClick={onLogout}
                className="inline-flex h-10 items-center justify-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
              >
                Logout
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
      {!loading && stats ? (
        <div className="mt-5 grid grid-cols-2 gap-2 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Total Articles
            </p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{stats.totalCount}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Critical Signals
            </p>
            <p className="mt-1 text-lg font-semibold text-rose-600">{stats.criticalCount}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              High Signals
            </p>
            <p className="mt-1 text-lg font-semibold text-amber-600">
              {stats.highPriorityCount}
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Last Sync Time
            </p>
            <p className="mt-1 truncate text-sm font-semibold text-slate-900">
              {stats.lastUpdated ?? '--'}
            </p>
          </div>
        </div>
      ) : null}
    </header>
  )
}
