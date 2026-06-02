import type { IntelligenceItem } from '../types/intelligence'

export type DepartmentTabId =
  | 'all'
  | 'ai'
  | 'analytics'
  | 'research-signals'
  | 'cloud'
  | 'marketing'
  | 'leadership'

export interface DepartmentTab {
  id: DepartmentTabId
  label: string
  /** Xerago domain slugs from API `domain` field (categories.md registry). */
  domains: readonly string[]
}

/**
 * Department-style tabs mapped to taxonomy domain slugs returned by the API.
 * @see docs/categories.md — Domain Registry
 */
export const DEPARTMENT_TABS: readonly DepartmentTab[] = [
  { id: 'all', label: 'All', domains: [] },
  { id: 'ai', label: 'AI', domains: ['enterprise-ai', 'ai-ml'] },
  { id: 'analytics', label: 'Analytics', domains: ['analytics'] },
  {
    id: 'research-signals',
    label: 'Research Signals',
    domains: ['research-signals'],
  },
  { id: 'cloud', label: 'Cloud', domains: ['cloud-platforms'] },
  { id: 'marketing', label: 'Marketing', domains: ['martech'] },
  {
    id: 'leadership',
    label: 'Leadership',
    domains: ['industry-trends', 'customer-experience'],
  },
] as const

export function normalizeDomainSlug(domain: string): string {
  return domain.trim().toLowerCase()
}

export function matchesDepartmentTab(
  item: IntelligenceItem,
  tab: DepartmentTab,
): boolean {
  if (tab.id === 'all') {
    return true
  }
  const slug = normalizeDomainSlug(item.domain)
  return tab.domains.includes(slug)
}

export function filterIntelligenceByTab(
  items: IntelligenceItem[],
  tab: DepartmentTab,
): IntelligenceItem[] {
  return items.filter((item) => matchesDepartmentTab(item, tab))
}

interface DepartmentViewConfig {
  allowedTabs: readonly DepartmentTabId[]
  defaultTab: DepartmentTabId
  departmentLabel: string
}

const DEFAULT_DEPARTMENT_VIEW: DepartmentViewConfig = {
  allowedTabs: [
    'all',
    'ai',
    'analytics',
    'research-signals',
    'cloud',
    'marketing',
    'leadership',
  ],
  defaultTab: 'all',
  departmentLabel: 'General',
}

export function getDepartmentViewForEmail(email: string | null): DepartmentViewConfig {
  const normalized = (email ?? '').trim().toLowerCase()
  if (normalized === 'ai@xerago.demo') {
    return {
      allowedTabs: ['all', 'ai'],
      defaultTab: 'ai',
      departmentLabel: 'AI',
    }
  }
  if (normalized === 'cloud@xerago.demo') {
    return {
      allowedTabs: ['all', 'cloud'],
      defaultTab: 'cloud',
      departmentLabel: 'Cloud',
    }
  }
  if (normalized === 'marketing@xerago.demo') {
    return {
      allowedTabs: ['all', 'marketing'],
      defaultTab: 'marketing',
      departmentLabel: 'Marketing',
    }
  }
  if (normalized === 'analytics@xerago.demo') {
    return {
      allowedTabs: ['all', 'analytics'],
      defaultTab: 'analytics',
      departmentLabel: 'Analytics',
    }
  }
  if (normalized === 'leadership@xerago.demo') {
    return {
      allowedTabs: ['all', 'leadership', 'research-signals'],
      defaultTab: 'leadership',
      departmentLabel: 'Leadership',
    }
  }
  return DEFAULT_DEPARTMENT_VIEW
}
