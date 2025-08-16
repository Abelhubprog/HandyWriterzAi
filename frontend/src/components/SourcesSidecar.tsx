'use client'

import React, { useMemo } from 'react'
import type { TimelineEvent } from '@/hooks/useStream'

interface SourcesSidecarProps {
  events: TimelineEvent[]
  conversationId?: string | null
}

type SourceItem = { title: string; url?: string; confidence?: number; agent?: string }

function uniqBy<T, K extends keyof any>(arr: T[], getKey: (x: T) => K): T[] {
  const seen = new Set<K>()
  const out: T[] = []
  for (const it of arr) {
    const k = getKey(it)
    if (!seen.has(k)) { seen.add(k); out.push(it) }
  }
  return out
}

export function SourcesSidecar({ events, conversationId }: SourcesSidecarProps) {
  const sources: SourceItem[] = useMemo(() => {
    const items: SourceItem[] = []
    for (const e of events || []) {
      // From agent:tool retriever
      if (e.type === 'agent:tool' && (e.agent === 'retriever' || e.agent === 'search' || e.agent === 'scholar' || e.agent === 'arxiv')) {
        const title = (e.result as string) || (e.title as string)
        if (title) items.push({ title, url: e.url as string | undefined, confidence: (e.confidence as number | undefined), agent: String(e.agent || '') })
      }
      // From sources_update
      if (e.type === 'sources_update' && Array.isArray((e as any).sources)) {
        for (const s of (e as any).sources) {
          const title = s?.title || s?.snippet || s?.url || 'source'
          items.push({ title, url: s?.url, confidence: s?.confidence })
        }
      }
    }
    const uniq = uniqBy(items, (x) => (x.url || x.title) as any)
    return uniq.slice(0, 20)
  }, [events])

  if (!sources.length) return null
  return (
    <aside className="bg-gray-900/50 border border-gray-800 rounded-md p-3">
      <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center justify-between">
        <span>Sources</span>
        {conversationId ? (
          <button
            className="text-[11px] px-2 py-0.5 rounded border bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700"
            title="Download sources CSV"
            onClick={async () => {
              try {
                const res = await fetch(`/api/stream/${conversationId}/sources.csv`)
                if (!res.ok) throw new Error(String(res.status))
                const blob = await res.blob()
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `sources-${conversationId}.csv`
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
              } catch (e) {
                // ignore
              }
            }}
          >Export CSV</button>
        ) : null}
      </div>
      <ul className="space-y-1.5 max-h-64 overflow-auto pr-1">
        {sources.map((s, i) => (
          <li key={i} className="text-xs text-gray-300">
            {s.url ? (
              <a href={s.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">{s.title}</a>
            ) : (
              <span>{s.title}</span>
            )}
            {typeof s.confidence === 'number' ? (
              <span className="text-gray-500"> · conf: {s.confidence.toFixed(2)}</span>
            ) : null}
            {s.agent ? <span className="text-gray-500"> · {s.agent}</span> : null}
          </li>
        ))}
      </ul>
    </aside>
  )
}
