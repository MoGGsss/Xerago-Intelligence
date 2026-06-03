import { useEffect, useId, useRef, useState } from 'react'
import { ChevronDown, LogOut } from 'lucide-react'

interface UserAccountMenuProps {
  userEmail: string
  department?: string
  lastLoginAt?: string | null
  lastUpdated?: string | null
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

export default function UserAccountMenu({
  userEmail,
  department,
  lastLoginAt,
  lastUpdated,
  onLogout,
}: UserAccountMenuProps) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const menuId = useId()
  const avatarInitial = userEmail[0]?.toUpperCase() ?? 'U'

  useEffect(() => {
    if (!open) {
      return
    }
    const onPointerDown = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-controls={menuId}
        className="inline-flex h-10 items-center gap-1.5 rounded-full border border-slate-200 bg-slate-100 pl-1 pr-2.5 text-sm font-semibold text-slate-700 transition-colors hover:border-slate-300 hover:bg-slate-200/80"
      >
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white text-sm font-semibold text-slate-800 shadow-sm">
          {avatarInitial}
        </span>
        <ChevronDown
          className={`h-4 w-4 text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`}
          aria-hidden
        />
      </button>

      {open ? (
        <div
          id={menuId}
          role="menu"
          className="absolute right-0 z-50 mt-2 w-72 rounded-xl border border-slate-200 bg-white p-4 shadow-lg"
        >
          <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            Account
          </p>
          <dl className="mt-3 space-y-2 text-sm text-slate-600">
            <div>
              <dt className="text-xs text-slate-400">Signed in as</dt>
              <dd className="font-medium text-slate-800">{userEmail}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-400">Department</dt>
              <dd className="font-medium text-slate-800">{department ?? 'General'}</dd>
            </div>
            {lastLoginAt ? (
              <div>
                <dt className="text-xs text-slate-400">Last login</dt>
                <dd className="font-medium text-slate-800">{formatDateTime(lastLoginAt)}</dd>
              </div>
            ) : null}
            {lastUpdated ? (
              <div>
                <dt className="text-xs text-slate-400">Last updated</dt>
                <dd className="font-medium text-slate-800">{lastUpdated}</dd>
              </div>
            ) : null}
          </dl>
          {onLogout ? (
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false)
                onLogout()
              }}
              className="mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white text-sm font-semibold text-slate-700 transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
            >
              <LogOut className="h-4 w-4" aria-hidden />
              Logout
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
