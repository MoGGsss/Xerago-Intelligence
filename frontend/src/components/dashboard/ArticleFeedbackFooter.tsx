import { useCallback, useEffect, useRef, useState } from 'react'
import { submitArticleFeedback } from '../../services/api'
import type { FeedbackReason } from '../../types/feedback'
import { NEGATIVE_FEEDBACK_REASONS } from '../../types/feedback'

type FooterState = 'idle' | 'submitting' | 'done' | 'duplicate'

const pillClass =
  'inline-flex h-6 shrink-0 items-center gap-0.5 whitespace-nowrap rounded-full border px-2 text-[11px] font-semibold leading-none transition-colors duration-200 disabled:opacity-50'

interface ArticleFeedbackFooterProps {
  artifactId: string
  departmentName: string
}

export default function ArticleFeedbackFooter({
  artifactId,
  departmentName,
}: ArticleFeedbackFooterProps) {
  const [state, setState] = useState<FooterState>('idle')
  const [showReasons, setShowReasons] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const rootRef = useRef<HTMLDivElement>(null)

  const submit = useCallback(
    async (feedbackType: 'positive' | 'negative', feedbackReason?: FeedbackReason) => {
      setErrorMessage(null)
      setState('submitting')
      try {
        await submitArticleFeedback({
          artifact_id: artifactId,
          department_name: departmentName,
          feedback_type: feedbackType,
          feedback_reason: feedbackReason,
        })
        setState('done')
        setShowReasons(false)
      } catch (error: unknown) {
        const status =
          typeof error === 'object' &&
          error !== null &&
          'response' in error &&
          typeof (error as { response?: { status?: number } }).response?.status === 'number'
            ? (error as { response: { status: number } }).response.status
            : undefined

        if (status === 409) {
          setState('duplicate')
          setShowReasons(false)
          return
        }
        if (!(feedbackType === 'negative' && feedbackReason)) {
          setShowReasons(false)
          setState('idle')
        }
        setErrorMessage('Could not save. Try again.')
      }
    },
    [artifactId, departmentName],
  )

  useEffect(() => {
    if (!showReasons) {
      return
    }
    const handlePointerDown = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setShowReasons(false)
        setState((current) => (current === 'submitting' ? current : 'idle'))
      }
    }
    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [showReasons])

  if (state === 'done' || state === 'duplicate') {
    return (
      <span
        className="inline-flex h-6 shrink-0 items-center text-[11px] font-medium text-emerald-700"
        role="status"
        aria-live="polite"
      >
        {state === 'duplicate' ? 'Recorded' : 'Thanks'}
      </span>
    )
  }

  return (
    <div
      ref={rootRef}
      className="relative inline-flex shrink-0 items-center gap-1.5"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        disabled={state === 'submitting'}
        onClick={() => void submit('positive')}
        className={`${pillClass} border-emerald-200/80 bg-emerald-50/90 text-emerald-800 hover:border-emerald-300 hover:bg-emerald-100`}
        aria-label="Mark as helpful"
      >
        <span className="text-[10px]" aria-hidden="true">
          👍
        </span>
        Helpful
      </button>
      <button
        type="button"
        disabled={state === 'submitting'}
        onClick={() => setShowReasons((open) => !open)}
        className={`${pillClass} border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50`}
        aria-label="Mark as not relevant"
        aria-expanded={showReasons}
        aria-haspopup="menu"
      >
        <span className="text-[10px]" aria-hidden="true">
          👎
        </span>
        Not relevant
      </button>

      {showReasons ? (
        <div
          className="absolute right-0 bottom-full z-20 mb-1 w-44 rounded-lg border border-slate-200/90 bg-white py-1 shadow-lg ring-1 ring-slate-900/5"
          role="menu"
        >
          {NEGATIVE_FEEDBACK_REASONS.map((option) => (
            <button
              key={option.value}
              type="button"
              role="menuitem"
              disabled={state === 'submitting'}
              onClick={() => void submit('negative', option.value)}
              className="block w-full px-2.5 py-1.5 text-left text-[11px] font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-slate-900 disabled:opacity-50"
            >
              {option.label}
            </button>
          ))}
        </div>
      ) : null}

      {errorMessage ? (
        <span className="sr-only" role="alert">
          {errorMessage}
        </span>
      ) : null}
    </div>
  )
}
