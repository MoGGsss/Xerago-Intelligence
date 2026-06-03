import type { DepartmentImpactView, IntelligenceItem } from '../types/intelligence'
import { departmentForEmail } from '../auth/demoAuth'
import {
  COMPANY_DEPARTMENTS,
  DEPARTMENT_BY_LABEL,
  DEPARTMENT_BY_SLUG,
  FEATURED_DEPARTMENT_SLUGS,
  type CompanyDepartment,
} from '../constants/departments'

export type DepartmentTabId = 'all' | string

export interface DepartmentTab {
  id: DepartmentTabId
  label: string
  departmentName: string
}

export const ALL_DEPARTMENT_TAB: DepartmentTab = {
  id: 'all',
  label: 'All',
  departmentName: '',
}

export const DEPARTMENT_TABS: readonly DepartmentTab[] = [
  ALL_DEPARTMENT_TAB,
  ...COMPANY_DEPARTMENTS.map((dept) => ({
    id: dept.slug,
    label: dept.label,
    departmentName: dept.label,
  })),
]

export const FEATURED_DEPARTMENT_TABS: readonly DepartmentTab[] =
  FEATURED_DEPARTMENT_SLUGS.flatMap((slug) => {
    const dept = DEPARTMENT_BY_SLUG[slug]
    if (!dept) {
      return []
    }
    return [
      {
        id: dept.slug,
        label: dept.label,
        departmentName: dept.label,
      },
    ]
  })

export const MIN_DEPARTMENT_RELEVANCE = 40

export function getDepartmentMapping(
  item: IntelligenceItem,
  departmentName: string,
) {
  return item.departments?.find((dept) => dept.department_name === departmentName)
}

export function getDepartmentRelevance(
  item: IntelligenceItem,
  departmentName: string,
): number | null {
  const match = getDepartmentMapping(item, departmentName)
  if (match) {
    return match.department_relevance_score
  }
  if (item.department === departmentName) {
    return MIN_DEPARTMENT_RELEVANCE
  }
  return null
}

export function getDepartmentImpact(
  item: IntelligenceItem,
  departmentName: string,
): DepartmentImpactView | null {
  const match = getDepartmentMapping(item, departmentName)
  if (!match) {
    return null
  }
  const hasImpact =
    match.impact_summary ||
    match.impact_category ||
    match.opportunity_type ||
    match.department_opportunity_score != null
  if (!hasImpact) {
    return null
  }
  return {
    impact_summary: match.impact_summary ?? null,
    impact_category: match.impact_category ?? null,
    opportunity_type: match.opportunity_type ?? null,
    department_opportunity_score: match.department_opportunity_score ?? null,
  }
}

export function matchesDepartment(
  item: IntelligenceItem,
  departmentName: string,
  minScore: number = MIN_DEPARTMENT_RELEVANCE,
): boolean {
  const score = getDepartmentRelevance(item, departmentName)
  return score !== null && score >= minScore
}

export function matchesDepartmentTab(
  item: IntelligenceItem,
  tab: DepartmentTab,
): boolean {
  if (tab.id === 'all') {
    return true
  }
  return matchesDepartment(item, tab.departmentName)
}

export function filterIntelligenceByTab(
  items: IntelligenceItem[],
  tab: DepartmentTab,
): IntelligenceItem[] {
  return items.filter((item) => matchesDepartmentTab(item, tab))
}

export function sortByDepartmentRelevance(
  items: IntelligenceItem[],
  departmentName: string,
): IntelligenceItem[] {
  return [...items].sort((a, b) => {
    const aScore = getDepartmentRelevance(a, departmentName) ?? -1
    const bScore = getDepartmentRelevance(b, departmentName) ?? -1
    if (bScore !== aScore) {
      return bScore - aScore
    }
    return (b.strategic_score ?? -1) - (a.strategic_score ?? -1)
  })
}

interface DepartmentViewConfig {
  allowedTabs: readonly DepartmentTabId[]
  defaultTab: DepartmentTabId
  departmentLabel: string
  primaryDepartment: string
  sectionTabs: readonly DepartmentTab[]
}

export function getDepartmentView(departmentName: string | null): DepartmentViewConfig {
  if (!departmentName) {
    return {
      allowedTabs: ['all'],
      defaultTab: 'all',
      departmentLabel: 'General',
      primaryDepartment: '',
      sectionTabs: [],
    }
  }

  const dept = DEPARTMENT_BY_LABEL[departmentName.trim()]
  if (!dept) {
    return {
      allowedTabs: ['all'],
      defaultTab: 'all',
      departmentLabel: departmentName,
      primaryDepartment: departmentName,
      sectionTabs: [],
    }
  }

  const tab: DepartmentTab = {
    id: dept.slug,
    label: dept.label,
    departmentName: dept.label,
  }

  return {
    allowedTabs: [dept.slug],
    defaultTab: dept.slug,
    departmentLabel: dept.label,
    primaryDepartment: dept.label,
    sectionTabs: [tab],
  }
}

export function getDepartmentViewForEmail(email: string | null): DepartmentViewConfig {
  const department =
    departmentForEmail(email ?? '') ?? localStorage.getItem('department')
  return getDepartmentView(department)
}

export function findDepartmentByLabel(label: string): CompanyDepartment | undefined {
  return DEPARTMENT_BY_LABEL[label]
}
