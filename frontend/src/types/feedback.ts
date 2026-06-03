export type FeedbackType = 'positive' | 'negative'

export type FeedbackReason =
  | 'wrong_department'
  | 'too_technical'
  | 'already_known'
  | 'low_business_impact'
  | 'duplicate_content'
  | 'not_relevant'

export interface FeedbackCreatePayload {
  artifact_id: string
  department_name: string
  feedback_type: FeedbackType
  feedback_reason?: FeedbackReason
}

export interface FeedbackCreateResponse {
  id: string
  artifact_id: string
  department_name: string
  feedback_type: FeedbackType
  feedback_reason: FeedbackReason | null
  created_at: string
}

export const NEGATIVE_FEEDBACK_REASONS: readonly {
  value: FeedbackReason
  label: string
}[] = [
  { value: 'wrong_department', label: 'Wrong department' },
  { value: 'too_technical', label: 'Too technical' },
  { value: 'already_known', label: 'Already known' },
  { value: 'low_business_impact', label: 'Low business impact' },
  { value: 'duplicate_content', label: 'Duplicate content' },
  { value: 'not_relevant', label: 'Not relevant' },
] as const
