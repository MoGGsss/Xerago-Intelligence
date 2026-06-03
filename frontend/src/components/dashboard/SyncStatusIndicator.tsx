import type { SystemStatusResponse } from '../../types/system'

interface SyncStatusIndicatorProps {
  status: SystemStatusResponse | null
  loading?: boolean
  compact?: boolean
}

function formatSyncTime(value: string | null): string {
  if (!value) {
    return '—'
  }
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(parsed)
}

function liveDotClass(status: SystemStatusResponse['status'] | undefined): string {
  if (status === 'healthy') {
    return 'bg-[#1D9E75]'
  }
  if (status === 'degraded') {
    return 'bg-amber-500'
  }
  return 'bg-rose-500'
}

function liveLabel(status: SystemStatusResponse['status'] | undefined, loading: boolean): string {
  if (loading && !status) {
    return 'Syncing…'
  }
  if (status === 'healthy') {
    return 'Live'
  }
  if (status === 'degraded') {
    return 'Degraded'
  }
  if (status === 'unhealthy') {
    return 'Offline'
  }
  return 'Live'
}

function Dot({ status }: { status: SystemStatusResponse['status'] | undefined }) {
  return (
    <span
      className={`inline-block h-2 w-2 shrink-0 rounded-full ${liveDotClass(status)}`}
      aria-hidden
    />
  )
}

function Separator() {
  return (
    <span className="mx-2 text-slate-300" aria-hidden>
      ·
    </span>
  )
}

export default function SyncStatusIndicator({
  status,
  loading = false,
  compact = false,
}: SyncStatusIndicatorProps) {
  const label = liveLabel(status?.status, loading)
  const lastSync = loading && !status ? '…' : formatSyncTime(status?.last_run ?? null)
  const nextRefresh = loading && !status ? '…' : formatSyncTime(status?.next_run ?? null)

  if (compact) {
    return (
      <div
        className="inline-flex h-10 max-w-full items-center rounded-lg border border-slate-200/90 bg-white px-3 text-xs text-slate-500 shadow-sm"
        aria-live="polite"
      >
        <Dot status={status?.status} />
        <span className="ml-2 shrink-0 font-medium text-slate-800">{label}</span>
        <Separator />
        <span className="shrink-0 whitespace-nowrap">
          Last sync <span className="font-medium text-slate-800">{lastSync}</span>
        </span>
        <Separator />
        <span className="hidden shrink-0 whitespace-nowrap sm:inline">
          Next refresh <span className="font-medium text-slate-800">{nextRefresh}</span>
        </span>
      </div>
    )
  }

  return (
    <div
      className="inline-flex min-h-11 max-w-full flex-wrap items-center rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-500"
      aria-live="polite"
    >
      <Dot status={status?.status} />
      <span className="ml-2 font-medium text-slate-800">{label}</span>
      <Separator />
      <span>
        Last sync <span className="font-medium text-slate-800">{lastSync}</span>
      </span>
      <Separator />
      <span>
        Next refresh <span className="font-medium text-slate-800">{nextRefresh}</span>
      </span>
    </div>
  )
}
