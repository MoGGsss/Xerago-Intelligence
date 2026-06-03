import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import AppNavbar, { APP_CHROME_MAX_W, APP_CHROME_PX } from '../components/layout/AppNavbar'
import {
  clearLogin,
  getLoggedInDepartment,
  getLoggedInEmail,
} from '../auth/demoAuth'
import CountBarChart from '../components/analytics/CountBarChart'
import FeedbackTrendChart from '../components/analytics/FeedbackTrendChart'
import HorizontalBarChart from '../components/analytics/HorizontalBarChart'
import SourceContributionChart from '../components/analytics/SourceContributionChart'
import { useExecutiveAnalytics } from '../hooks/useExecutiveAnalytics'

function KpiCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-4 shadow-sm md:p-5">
      <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-3xl font-semibold tabular-nums tracking-tight text-slate-900">
        {value}
      </p>
      {hint ? <p className="mt-1 text-xs text-emerald-600">{hint}</p> : null}
    </article>
  )
}

export default function ExecutiveAnalytics() {
  const navigate = useNavigate()
  const userEmail = getLoggedInEmail()
  const department = getLoggedInDepartment()
  const { data, loading, error, refresh } = useExecutiveAnalytics()

  const logout = () => {
    clearLogin()
    navigate('/login', { replace: true })
  }

  return (
    <main className="min-h-screen bg-[#f5f7f8] pb-8 md:pb-12">
      <div className="w-full border-b border-slate-200/90 bg-white">
        <div className={`mx-auto w-full ${APP_CHROME_MAX_W} ${APP_CHROME_PX}`}>
        <AppNavbar
          pageTitle="Intelligence Performance"
          pageSubtitle="Cross-source insights from enrichments, department impact, and feedback"
          userEmail={userEmail ?? undefined}
          department={department ?? undefined}
          onLogout={logout}
          actionTo="/dashboard"
          actionLabel="Intelligence Feed"
          actionIcon={<ArrowLeft className="h-3.5 w-3.5" aria-hidden />}
        />
        </div>
      </div>
      <div className={`mx-auto w-full pt-6 md:pt-8 ${APP_CHROME_MAX_W} ${APP_CHROME_PX}`}>
        <div className="mb-6 flex justify-end">
          <button
            type="button"
            onClick={() => void refresh()}
            className="inline-flex h-10 items-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 hover:border-slate-300"
          >
            Refresh
          </button>
        </div>

        {error ? (
          <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        {loading && !data ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="h-28 animate-pulse rounded-2xl border border-slate-200 bg-slate-100"
              />
            ))}
          </div>
        ) : null}

        {data ? (
          <>
            <section className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <KpiCard label="Articles Today" value={data.overview.articles_today} />
              <KpiCard label="Active Sources" value={data.overview.active_sources} />
              <KpiCard
                label="Avg Strategic Score"
                value={data.overview.average_strategic_score ?? '—'}
              />
              <KpiCard
                label="Feedback (Pos / Neg)"
                value={`${data.overview.feedback_positive} / ${data.overview.feedback_negative}`}
                hint={`${data.overview.enriched_articles} enriched articles`}
              />
            </section>

            <section className="mb-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
              <HorizontalBarChart
                title="Department Opportunity Scores"
                subtitle="Average department opportunity score by team"
                items={data.departments.top_departments}
                valueKey="avg_score"
              />
              <CountBarChart
                title="Opportunity Categories"
                subtitle="Impact category frequency across department mappings"
                items={data.opportunities.top_opportunity_categories}
                barClassName="bg-teal-500"
              />
            </section>

            <section className="mb-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
              <CountBarChart
                title="Opportunity Types"
                subtitle="Opportunity type distribution"
                items={data.opportunities.top_opportunity_types}
                barClassName="bg-indigo-500"
              />
              <SourceContributionChart items={data.sources.source_contribution} />
            </section>

            <section className="mb-6">
              <FeedbackTrendChart summary={data.feedback.positive_vs_negative} />
            </section>

            <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-slate-900">Most Useful Articles</h3>
                <p className="mt-1 text-xs text-slate-500">Ranked by positive department feedback</p>
                <ul className="mt-4 space-y-3">
                  {data.feedback.most_useful_articles.length === 0 ? (
                    <li className="text-sm text-slate-400">No positive feedback yet</li>
                  ) : (
                    data.feedback.most_useful_articles.map((article) => (
                      <li
                        key={article.artifact_id}
                        className="rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2"
                      >
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noreferrer"
                          className="line-clamp-2 text-sm font-medium text-slate-800 hover:text-emerald-700"
                        >
                          {article.title}
                        </a>
                        <p className="mt-1 text-xs text-slate-500">
                          {article.positive_count} positive
                          {article.strategic_score != null
                            ? ` · score ${article.strategic_score}`
                            : ''}
                        </p>
                      </li>
                    ))
                  )}
                </ul>
              </article>

              <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-slate-900">Department Engagement</h3>
                <p className="mt-1 text-xs text-slate-500">
                  Mapped articles and feedback volume by department
                </p>
                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="py-2 pr-3 font-semibold">Department</th>
                        <th className="py-2 pr-3 font-semibold">Mapped</th>
                        <th className="py-2 pr-3 font-semibold">Feedback</th>
                        <th className="py-2 font-semibold">+ / −</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.departments.department_engagement.map((row) => (
                        <tr key={row.department_name} className="border-b border-slate-100">
                          <td className="py-2 pr-3 font-medium text-slate-700">
                            {row.department_name}
                          </td>
                          <td className="py-2 pr-3 tabular-nums text-slate-600">
                            {row.mapped_articles}
                          </td>
                          <td className="py-2 pr-3 tabular-nums text-slate-600">
                            {row.feedback_count}
                          </td>
                          <td className="py-2 tabular-nums">
                            <span className="text-emerald-600">{row.positive_count}</span>
                            <span className="text-slate-400"> / </span>
                            <span className="text-rose-600">{row.negative_count}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            </section>
          </>
        ) : null}
      </div>
    </main>
  )
}
