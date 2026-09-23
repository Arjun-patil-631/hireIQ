import type { CSSProperties } from 'react'

interface Props { score?: number | null; label?: string }

export function ScoreRing({ score, label = 'Overall' }: Props) {
  const value = Math.round(score ?? 0)
  return (
    <div className="score-ring" style={{ '--value': `${Math.max(0, Math.min(100, value)) * 3.6}deg` } as CSSProperties}>
      <div className="score-ring-inner">
        <strong>{score == null ? '—' : value}</strong>
        <span>{label}</span>
      </div>
    </div>
  )
}
