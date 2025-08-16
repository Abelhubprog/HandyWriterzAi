'use client'

import React from 'react'
import { CheckCircle2, Circle, Clock } from 'lucide-react'

type Chip = {
  key: string
  label: string
  activeWhen: (type: string) => boolean
}

interface ProgressChipsProps {
  events: { type: string; ts?: number | string }[]
}

const CHIPS: Chip[] = [
  { key: 'planning', label: 'Planning', activeWhen: t => t === 'planning_started' },
  { key: 'search', label: 'Research', activeWhen: t => t === 'search_started' || t === 'search_progress' },
  { key: 'writer', label: 'Writing', activeWhen: t => t === 'writer_started' || t === 'token' || t === 'content' },
  { key: 'evaluate', label: 'Evaluate', activeWhen: t => t === 'evaluator_started' || t === 'evaluator_feedback' },
  { key: 'format', label: 'Formatting', activeWhen: t => t === 'formatter_started' },
]

export function ProgressChips({ events }: ProgressChipsProps) {
  if (!events || events.length === 0) return null

  const lastType = events[events.length - 1]?.type

  return (
    <div className="flex flex-wrap gap-2 py-2 px-4">
      {CHIPS.map((chip, idx) => {
        const completed = events.some(e => e.type === 'done' || e.type === 'workflow_finished')
        const active = chip.activeWhen(lastType)
        const Icon = completed || active ? CheckCircle2 : Circle
        const tone = completed || active ? 'text-emerald-500 border-emerald-600' : 'text-gray-400 border-gray-600'

        return (
          <span key={chip.key} className={`inline-flex items-center gap-1 text-xs border rounded-full px-2 py-0.5 ${tone}`}>
            <Icon className="h-3 w-3" />
            {chip.label}
          </span>
        )
      })}
      {/* Fallback idle chip */}
      {!CHIPS.some(c => c.activeWhen(lastType)) && lastType && (
        <span className="inline-flex items-center gap-1 text-xs border rounded-full px-2 py-0.5 text-gray-400 border-gray-600">
          <Clock className="h-3 w-3" />
          Working...
        </span>
      )}
    </div>
  )
}

