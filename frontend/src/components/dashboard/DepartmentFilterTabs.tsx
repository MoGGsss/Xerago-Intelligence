import {
  DEPARTMENT_TABS,
  type DepartmentTab,
  type DepartmentTabId,
} from '../../utils/departmentFilters'

interface DepartmentFilterTabsProps {
  activeTabId: DepartmentTabId
  onTabChange: (tabId: DepartmentTabId) => void
  counts: Record<DepartmentTabId, number>
  tabs?: readonly DepartmentTab[]
}

export default function DepartmentFilterTabs({
  activeTabId,
  onTabChange,
  counts,
  tabs = DEPARTMENT_TABS,
}: DepartmentFilterTabsProps) {
  return (
    <nav
      className="mb-6 -mx-1 overflow-x-auto pb-1"
      aria-label="Filter intelligence by department"
    >
      <div className="flex min-w-min gap-2 px-1">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTabId
          const count = counts[tab.id]

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              aria-pressed={isActive}
              className={`inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition-all duration-200 ease-out ${
                isActive
                  ? 'border-emerald-600 bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-emerald-200 hover:bg-emerald-50/60 hover:text-emerald-800'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`inline-flex min-w-[1.25rem] items-center justify-center rounded-full px-1.5 py-0.5 text-[11px] font-bold tabular-nums transition-colors duration-200 ${
                  isActive
                    ? 'bg-white/20 text-white'
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {count}
              </span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
