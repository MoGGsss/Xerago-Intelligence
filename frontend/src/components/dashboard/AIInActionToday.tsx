import { useMemo, useState } from 'react'
import IntelligenceCard from './IntelligenceCard'
import IntelligenceDetailPanel from './IntelligenceDetailPanel'
import DashboardMetrics from './DashboardMetrics'
import { AlertCircle, ArrowUpRight, Sparkles } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { getLoggedInDepartment, getLoggedInEmail } from '../../auth/demoAuth'
import { useIntelligence } from '../../hooks/useIntelligence'
import { useSystemStatus } from '../../hooks/useSystemStatus'
import type { IntelligenceItem, PriorityLevel } from '../../types/intelligence'
import SectionHeader from './SectionHeader'
import { getDepartmentImpact, getDepartmentView } from '../../utils/departmentFilters'
import { computeIntelligenceHeaderStats } from '../../utils/intelligenceStats'

const cardIcons: LucideIcon[] = [Sparkles, ArrowUpRight, AlertCircle]
type SortOption = 'strategic_score' | 'newest' | 'oldest'
const DEFAULT_VISIBLE_ARTICLES = 6

interface AIInActionTodayProps {
  onLogout?: () => void
}

function IntelligenceSkeletonCard() {
  return (
    <article className="flex h-full min-h-[380px] flex-col overflow-hidden rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <span className="inline-flex h-10 w-10 animate-pulse rounded-xl bg-emerald-50" />
        <div className="flex gap-2">
          <span className="h-6 w-16 animate-pulse rounded-full bg-slate-100" />
          <span className="h-6 w-8 animate-pulse rounded-lg bg-slate-200" />
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <span className="h-5 w-24 animate-pulse rounded-md bg-slate-100" />
        <span className="h-5 w-20 animate-pulse rounded bg-slate-100" />
      </div>
      <div className="mt-4 h-6 w-4/5 animate-pulse rounded bg-slate-100" />
      <div className="mt-3 space-y-2">
        <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
        <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
        <div className="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
      </div>
      <div className="mt-auto border-t border-slate-100 pt-4">
        <div className="h-9 w-full animate-pulse rounded-lg bg-slate-100" />
      </div>
    </article>
  )
}

export default function AIInActionToday({ onLogout }: AIInActionTodayProps) {
  const { data, loading, error } = useIntelligence()
  const { data: systemStatus, loading: systemStatusLoading } = useSystemStatus()
  const loggedInDepartment = getLoggedInDepartment()
  const userEmail = getLoggedInEmail()
  const departmentView = useMemo(
    () => getDepartmentView(loggedInDepartment),
    [loggedInDepartment],
  )
  const [selectedItem, setSelectedItem] = useState<IntelligenceItem | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<'ALL' | PriorityLevel>('ALL')
  const [domainFilter, setDomainFilter] = useState<string>('ALL')
  const [sortBy, setSortBy] = useState<SortOption>('strategic_score')
  const [showAll, setShowAll] = useState(false)

  const headerStats = useMemo(
    () => computeIntelligenceHeaderStats(data),
    [data],
  )

  const domainOptions = useMemo(() => {
    const domains = new Set<string>()
    for (const item of data) {
      if (item.domain.trim()) {
        domains.add(item.domain.trim())
      }
    }
    return ['ALL', ...Array.from(domains).sort()]
  }, [data])

  const filteredItems = useMemo(() => {
    const searched = data.filter((item) => {
      const q = searchQuery.trim().toLowerCase()
      if (!q) {
        return true
      }
      return (
        item.title.toLowerCase().includes(q) || item.summary.toLowerCase().includes(q)
      )
    })

    const priorityFiltered =
      priorityFilter === 'ALL'
        ? searched
        : searched.filter((item) => item.priority_level === priorityFilter)

    const domainFiltered =
      domainFilter === 'ALL'
        ? priorityFiltered
        : priorityFiltered.filter((item) => item.domain === domainFilter)

    return [...domainFiltered].sort((a, b) => {
      if (sortBy === 'strategic_score') {
        return (b.strategic_score ?? -1) - (a.strategic_score ?? -1)
      }
      const at = new Date(a.published_at).getTime()
      const bt = new Date(b.published_at).getTime()
      if (sortBy === 'newest') {
        return bt - at
      }
      return at - bt
    })
  }, [data, searchQuery, priorityFilter, domainFilter, sortBy])

  const visibleItems = showAll
    ? filteredItems
    : filteredItems.slice(0, DEFAULT_VISIBLE_ARTICLES)

  const criticalCount = filteredItems.filter(
    (item) => item.priority_level === 'CRITICAL',
  ).length
  const highCount = filteredItems.filter((item) => item.priority_level === 'HIGH').length
  const mediumCount = filteredItems.filter(
    (item) => item.priority_level === 'MEDIUM',
  ).length

  return (
    <div className="mx-auto w-full max-w-[1600px] px-5 sm:px-8 lg:px-12 xl:px-16">
      <section className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm md:p-8 lg:p-10">
        <SectionHeader
          title="Intelligence Center"
          subtitle={`Strategic signals curated for ${departmentView.departmentLabel}`}
          dataLastUpdated={!loading && !error ? headerStats.lastUpdated : undefined}
          systemStatus={systemStatus}
          systemStatusLoading={systemStatusLoading}
          userEmail={userEmail ?? undefined}
          department={departmentView.departmentLabel}
          onLogout={onLogout}
        />

        {!error ? (
          <div className="mt-6">
            <DashboardMetrics stats={headerStats} loading={loading} />
          </div>
        ) : null}

        {!loading && !error ? (
        <section className="mt-6 rounded-xl border border-slate-200/90 bg-slate-50/60 p-4 md:p-5">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search title or summary"
                className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
              />
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Priority
              </span>
              <select
                value={priorityFilter}
                onChange={(event) =>
                  setPriorityFilter(event.target.value as 'ALL' | PriorityLevel)
                }
                className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
              >
                <option value="ALL">All</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Domain
              </span>
              <select
                value={domainFilter}
                onChange={(event) => setDomainFilter(event.target.value)}
                className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
              >
                {domainOptions.map((domain) => (
                  <option key={domain} value={domain}>
                    {domain === 'ALL' ? 'All domains' : domain}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Sort
              </span>
              <select
                value={sortBy}
                onChange={(event) => setSortBy(event.target.value as SortOption)}
                className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition-colors focus:border-emerald-300"
              >
                <option value="strategic_score">Department relevance</option>
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
              </select>
            </label>
          </div>
        </section>
        ) : null}

        {loading ? (
        <div className="mt-8 grid grid-cols-1 gap-5 border-t border-slate-100 pt-6 transition-opacity duration-300 ease-out md:grid-cols-2 md:gap-6 lg:grid-cols-3 lg:auto-rows-fr animate-in fade-in">
          {Array.from({ length: 3 }).map((_, index) => (
            <IntelligenceSkeletonCard key={`skeleton-${index}`} />
          ))}
        </div>
        ) : null}

        {!loading && error ? (
        <article className="mt-6 flex min-h-[200px] items-center justify-center rounded-xl border border-rose-100 bg-rose-50/50 p-8 text-center text-base font-medium text-rose-800">
          Unable to load intelligence insights. Please try again later.
        </article>
        ) : null}

        {!loading && !error ? (
        <section className="mt-8 border-t border-slate-100 pt-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-semibold tracking-tight text-slate-900">
                {departmentView.departmentLabel} Feed ({filteredItems.length} articles)
              </h2>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-xs font-semibold uppercase tracking-wide text-slate-600">
                <span className="rounded-md bg-rose-50 px-2 py-1 text-rose-700">
                  Critical: {criticalCount}
                </span>
                <span className="rounded-md bg-amber-50 px-2 py-1 text-amber-700">
                  High: {highCount}
                </span>
                <span className="rounded-md bg-sky-50 px-2 py-1 text-sky-700">
                  Medium: {mediumCount}
                </span>
              </div>
            </div>
            {filteredItems.length > DEFAULT_VISIBLE_ARTICLES ? (
              <button
                type="button"
                onClick={() => setShowAll((current) => !current)}
                className="inline-flex items-center rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-semibold text-slate-700 transition-all duration-200 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
              >
                {showAll ? 'Show less' : 'View all'}
              </button>
            ) : null}
          </div>

          {filteredItems.length === 0 ? (
            <article className="flex min-h-[140px] items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-6 text-center text-base font-medium text-slate-600">
              No intelligence signals mapped to {departmentView.departmentLabel} yet.
            </article>
          ) : (
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6 lg:grid-cols-3 lg:auto-rows-fr">
              {visibleItems.map((card, index) => (
                <IntelligenceCard
                  key={card.artifact_id}
                  artifactId={card.artifact_id}
                  feedbackDepartmentName={loggedInDepartment}
                  title={card.title}
                  description={card.summary}
                  whyItMatters={card.why_it_matters}
                  priorityLevel={card.priority_level}
                  strategicScore={card.strategic_score}
                  publishedAt={card.published_at}
                  domain={card.domain}
                  url={card.url}
                  icon={cardIcons[index % cardIcons.length]}
                  departmentImpact={
                    departmentView.primaryDepartment
                      ? getDepartmentImpact(card, departmentView.primaryDepartment)
                      : null
                  }
                  departmentLabel={departmentView.departmentLabel}
                  onSelect={() => setSelectedItem(card)}
                />
              ))}
            </div>
          )}
        </section>
        ) : null}
      </section>
      <IntelligenceDetailPanel
        item={selectedItem}
        open={selectedItem !== null}
        onClose={() => setSelectedItem(null)}
      />
    </div>
  )
}
