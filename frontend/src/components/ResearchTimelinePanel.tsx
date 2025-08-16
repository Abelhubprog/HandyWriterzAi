'use client'

import React, { useMemo, useState, useEffect } from 'react'
import type { TimelineEvent } from '@/hooks/useStream'

type StageKey = 'planning' | 'files' | 'research' | 'retrieval' | 'writing' | 'evaluation' | 'other'

interface ResearchTimelinePanelProps {
  events: TimelineEvent[]
  isConnected?: boolean
  conversationId?: string | null
}

const stageLabels: Record<StageKey, string> = {
  planning: 'Planning',
  files: 'Files',
  research: 'Research',
  retrieval: 'Retrieval',
  writing: 'Writing',
  evaluation: 'Evaluation',
  other: 'Other'
}

function stageOf(e: TimelineEvent): StageKey {
  const t = (e.type || '').toLowerCase()
  const node = (e.node || '').toLowerCase()
  const agent = (e.agent || '').toLowerCase()

  if (t === 'planning_started' || t.startsWith('progress:plan')) return 'planning'
  if (t.startsWith('files:') || t === 'file_processing') return 'files'
  if (t.startsWith('search') || node === 'search' || node === 'arxiv' || node === 'scholar') return 'research'
  if (t === 'sources_update' || t.startsWith('progress:retriev')) return 'retrieval'
  if (t === 'writer_started' || node === 'writer' || t.startsWith('token') || t === 'content') return 'writing'
  if (t === 'evaluator_started' || t === 'evaluator_feedback' || t === 'formatter_started') return 'evaluation'
  // Agent-classified events
  if (t.startsWith('agent:')) {
    if (agent === 'planner') return 'planning'
    if (agent === 'research_swarm' || agent === 'search' || agent === 'arxiv' || agent === 'scholar') return 'research'
    if (agent === 'retriever' || agent === 'retrieval') return 'retrieval'
    if (agent === 'writer' || agent === 'formatter') return 'writing'
    if (agent === 'evaluator' || agent === 'qa') return 'evaluation'
  }
  return 'other'
}

function niceTime(ts?: number | string): string {
  if (!ts) return ''
  const n = typeof ts === 'string' ? Number(ts) : ts
  if (!n || Number.isNaN(n)) return ''
  const d = new Date(n * (n > 1e12 ? 1 : 1000)) // handle seconds vs ms
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export function ResearchTimelinePanel({ events, isConnected, conversationId }: ResearchTimelinePanelProps) {
  const [collapsed, setCollapsed] = useState<Record<StageKey, boolean>>({
    planning: false,
    files: false,
    research: false,
    retrieval: false,
    writing: false,
    evaluation: false,
    other: true,
  })
  const [selected, setSelected] = useState<TimelineEvent | null>(null)
  const [, forceRender] = useState(0)
  useEffect(() => {
    const t = setInterval(() => forceRender(x => x + 1), 1000)
    return () => clearInterval(t)
  }, [])

  const grouped = useMemo(() => {
    const g: Record<StageKey, TimelineEvent[]> = {
      planning: [], files: [], research: [], retrieval: [], writing: [], evaluation: [], other: []
    }
    // Filter by selected agents and stages when selected
    const filterAgents = selectedAgents.size > 0
    const filterStages = selectedStages.size > 0
    for (const e of events || []) {
      const s = stageOf(e)
      if (filterStages && !selectedStages.has(s)) continue
      if (filterAgents) {
        const a = (e.agent ? String(e.agent) : '').toLowerCase()
        if (!selectedAgents.has(a)) continue
      }
      const s = stageOf(e)
      g[s].push(e)
    }
    return g
  }, [events, /* filtering */ selectedAgents])

  const stageOrder: StageKey[] = ['planning', 'files', 'research', 'retrieval', 'writing', 'evaluation']
  // Agent filter chips
  const agentList = useMemo(() => {
    const set = new Set<string>()
    for (const e of events || []) {
      if (e.agent) set.add(String(e.agent).toLowerCase())
    }
    return Array.from(set).sort()
  }, [events])
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set())
  function toggleAgent(agent: string) {
    setSelectedAgents(prev => {
      const next = new Set(prev)
      if (next.has(agent)) next.delete(agent) else next.add(agent)
      return next
    })
  }
  // Stage filter chips
  const [selectedStages, setSelectedStages] = useState<Set<StageKey>>(new Set())
  function toggleStage(stage: StageKey) {
    setSelectedStages(prev => {
      const next = new Set(prev)
      if (next.has(stage)) next.delete(stage) else next.add(stage)
      return next
    })
  }

  function progressFor(stage: StageKey): number {
    const list = grouped[stage] || []
    const hasDone = (events || []).some(e => e.type === 'done' || e.type === 'workflow_finished')
    if (stage === 'planning') {
      const started = list.some(e => e.type === 'planning_started' || (e.type === 'agent:start' && e.agent === 'planner'))
      const finished = (events || []).some(e => e.type === 'agent:result' && e.agent === 'planner' && e.summary === 'prompt_orchestrated')
      return finished ? 100 : started ? 50 : 0
    }
    if (stage === 'files') {
      const proc = list.some(e => e.status === 'processing_files')
      const done = list.some(e => e.status === 'files_processed')
      return done ? 100 : proc ? 50 : 0
    }
    if (stage === 'research') {
      const queries = (events || []).filter(e => e.type === 'agent:tool' && (e.agent === 'search')).length
      const hits = (events || []).filter(e => e.type === 'agent:tool' && (e.agent === 'retriever')).length
      const verified = (events || []).some(e => e.type === 'agent:result' && e.agent === 'research_swarm')
      if (verified) return 100
      const score = Math.min(100, queries * 15 + hits * 10)
      return score
    }
    if (stage === 'retrieval') {
      const updates = list.filter(e => e.type === 'sources_update').length
      return Math.min(100, updates * 50)
    }
    if (stage === 'writing') {
      const started = (events || []).some(e => e.type === 'agent:start' && e.agent === 'writer')
      const tokens = (events || []).filter(e => e.type === 'token').length
      if (hasDone) return 100
      if (started) return Math.min(95, 10 + tokens)
      return 0
    }
    if (stage === 'evaluation') {
      const evalStart = list.some(e => e.type === 'evaluator_started')
      const feedback = list.some(e => e.type === 'evaluator_feedback')
      const fmt = list.some(e => e.type === 'formatter_started')
      return fmt ? 100 : feedback ? 80 : evalStart ? 40 : 0
    }
    return 0
  }

  function toggle(stage: StageKey) {
    setCollapsed(prev => ({ ...prev, [stage]: !prev[stage] }))
  }

  function stageStartTs(stage: StageKey): number | null {
    const list = grouped[stage] || []
    if (!list.length) return null
    const first = list[0]
    const ts = (first.ts as any) || Date.now()/1000
    return typeof ts === 'number' ? (ts > 1e12 ? ts/1000 : ts) : null
  }

  function etaFor(stage: StageKey): string | null {
    const start = stageStartTs(stage)
    if (!start) return null
    const expected: Record<StageKey, number> = {
      planning: 6,
      files: 5,
      research: 25,
      retrieval: 8,
      writing: 30,
      evaluation: 10,
      other: 0,
    }
    const pct = progressFor(stage)
    if (pct >= 100) return 'done'
    const elapsed = (Date.now()/1000) - start
    const remain = Math.max(0, expected[stage] * (1 - pct/100) - elapsed)
    const m = Math.floor(remain/60)
    const s = Math.floor(remain%60)
    return m > 0 ? `${m}m ${s}s` : `${s}s`
  }

  return (
    <aside className="hidden lg:flex lg:flex-col gap-3 border-l border-gray-800 pl-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-200">Research Timeline</h3>
        <div className="flex items-center gap-2">
          {conversationId ? (
            <button
              className="text-[11px] px-2 py-0.5 rounded border bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700"
              title="Download replay JSON"
              onClick={async () => {
                try {
                  const res = await fetch(`/api/stream/${conversationId}/replay`)
                  if (!res.ok) throw new Error(String(res.status))
                  const blob = new Blob([await res.text()], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `timeline-${conversationId}.json`
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                } catch (e) {
                  // ignore
                }
              }}
            >Export JSON</button>
          ) : null}
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-gray-500'}`} title={isConnected ? 'Streaming' : 'Idle'} />
        </div>
      </div>

      {agentList.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {agentList.map(a => (
            <button
              key={a}
              onClick={() => toggleAgent(a)}
              className={`text-[11px] px-2 py-0.5 rounded border ${selectedAgents.has(a) ? 'bg-blue-600 text-white border-blue-500' : 'bg-gray-800 text-gray-300 border-gray-700'}`}
              title={`Filter by ${a}`}
            >
              {a}
            </button>
          ))}
          {selectedAgents.size > 0 && (
            <button onClick={() => setSelectedAgents(new Set())} className="text-[11px] px-2 py-0.5 rounded bg-gray-700 text-gray-200 border border-gray-600">
              Clear
            </button>
          )}
        </div>
      ) : null}

      {/* Stage filter chips */}
      <div className="flex flex-wrap gap-2">
        {(['planning','files','research','retrieval','writing','evaluation'] as StageKey[]).map(st => (
          <button
            key={st}
            onClick={() => toggleStage(st)}
            className={`text-[11px] px-2 py-0.5 rounded border ${selectedStages.has(st) ? 'bg-purple-600 text-white border-purple-500' : 'bg-gray-800 text-gray-300 border-gray-700'}`}
            title={`Filter by ${stageLabels[st]}`}
          >
            {stageLabels[st]}
          </button>
        ))}
        {selectedStages.size > 0 && (
          <button onClick={() => setSelectedStages(new Set())} className="text-[11px] px-2 py-0.5 rounded bg-gray-700 text-gray-200 border border-gray-600">
            Clear
          </button>
        )}
      </div>

      {stageOrder.map((stage) => {
        const list = grouped[stage]
        const pct = progressFor(stage)
        if (!list || list.length === 0) return (
          <section key={stage} className="bg-gray-900/50 border border-gray-800 rounded-md p-3">
            <div className="flex items-center justify-between mb-1">
              <div className="text-xs uppercase tracking-wide text-gray-400">{stageLabels[stage]}</div>
              <div className="flex items-center gap-2">
                {etaFor(stage) ? <span className="text-[10px] text-gray-500">ETA {etaFor(stage)}</span> : null}
                <button onClick={() => toggle(stage)} className="text-[10px] text-gray-500 hover:text-gray-300">{collapsed[stage] ? 'Expand' : 'Collapse'}</button>
              </div>
            </div>
            <div className="h-1.5 bg-gray-800 rounded overflow-hidden mb-2"><div className="h-full bg-blue-500" style={{ width: `${pct}%` }} /></div>
            <div className="text-xs text-gray-500">No activity</div>
          </section>
        )
        return (
          <section key={stage} className="bg-gray-900/50 border border-gray-800 rounded-md p-3">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center justify-between gap-2">
              <span>{stageLabels[stage]}</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-gray-800 rounded overflow-hidden"><div className="h-full bg-blue-500" style={{ width: `${pct}%` }} /></div>
                <span className="text-[10px] text-gray-500">{list.length} evt</span>
                {etaFor(stage) ? <span className="text-[10px] text-gray-500">ETA {etaFor(stage)}</span> : null}
                <button onClick={() => toggle(stage)} className="text-[10px] text-gray-500 hover:text-gray-300">{collapsed[stage] ? 'Expand' : 'Collapse'}</button>
              </div>
            </div>
            {!collapsed[stage] && (
              <ul className="space-y-1.5 max-h-56 overflow-auto pr-1">
              {list.map((e, idx) => (
                <li key={idx} className="flex items-start gap-2 cursor-pointer" onClick={() => setSelected(e)}>
                  <span className="mt-1 w-1.5 h-1.5 rounded-full bg-blue-400/80" />
                  <div className="min-w-0">
                    <div className="text-xs text-gray-300 truncate">
                      {e.type}
                      {e.agent ? <span className="text-gray-500"> · {String(e.agent)}</span> : null}
                      {!e.agent && e.node ? <span className="text-gray-500"> · {e.node}</span> : null}
                    </div>
                    {(() => {
                      const line = (e.summary as string) || (e.action as string) || (e.result as string) || (e.text as string) || (e.message as string) || (e.delta as string)
                      if (e.url && (e.result || e.title || e.summary)) {
                        const label = (e.result as string) || (e.title as string) || (e.summary as string)
                        return (
                          <div className="text-[11px] text-gray-300 line-clamp-2">
                            <a href={String(e.url)} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
                              {label}
                            </a>
                            {e.query ? <span className="text-gray-500"> · q: {String(e.query)}</span> : null}
                          </div>
                        )
                      }
                      return line ? (
                        <div className="text-[11px] text-gray-400 line-clamp-2">{line}{e.query ? <span className="text-gray-500"> · q: {String(e.query)}</span> : null}</div>
                      ) : null
                    })()}
                    <div className="text-[10px] text-gray-500">{niceTime(e.ts as any)}</div>
                  </div>
                </li>
              ))}
              </ul>
            )}
          </section>
        )
      })}

      {grouped.other?.length ? (
        <section className="bg-gray-900/50 border border-gray-800 rounded-md p-3">
          <div className="text-xs uppercase tracking-wide text-gray-400 mb-2">{stageLabels.other}</div>
          <ul className="space-y-1.5 max-h-40 overflow-auto pr-1">
            {grouped.other.map((e, idx) => (
              <li key={idx} className="text-xs text-gray-300 truncate">
                {e.type} {e.node ? <span className="text-gray-500">· {e.node}</span> : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {/* Details Drawer */}
      {selected && (
        <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setSelected(null)}>
          <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-gray-900 border-l border-gray-800 p-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-semibold text-gray-200">Event Details</div>
              <button className="text-gray-400 hover:text-gray-200 text-sm" onClick={() => setSelected(null)}>Close</button>
            </div>
            <div className="text-xs text-gray-400 mb-3">{selected.type}{selected.agent ? ` · ${selected.agent}` : selected.node ? ` · ${selected.node}` : ''} · {niceTime(selected.ts as any)}</div>
            <div className="space-y-1 text-sm">
              {selected.summary ? <div><span className="text-gray-400">Summary:</span> <span className="text-gray-200">{String(selected.summary)}</span></div> : null}
              {selected.action ? <div><span className="text-gray-400">Action:</span> <span className="text-gray-200">{String(selected.action)}</span></div> : null}
              {selected.query ? <div><span className="text-gray-400">Query:</span> <span className="text-gray-200">{String(selected.query)}</span></div> : null}
              {selected.result ? <div><span className="text-gray-400">Result:</span> <span className="text-gray-200">{String(selected.result)}</span></div> : null}
              {selected.url ? <div><span className="text-gray-400">URL:</span> <a className="text-blue-400 hover:underline" href={String(selected.url)} target="_blank" rel="noreferrer">{String(selected.url)}</a></div> : null}
              {typeof selected.confidence === 'number' ? <div><span className="text-gray-400">Confidence:</span> <span className="text-gray-200">{Number(selected.confidence).toFixed(2)}</span></div> : null}
              {(selected.text || selected.message) ? <div><span className="text-gray-400">Text:</span> <span className="text-gray-200">{String(selected.text || selected.message)}</span></div> : null}
              {Array.isArray((selected as any).feedback_samples) && (selected as any).feedback_samples.length > 0 ? (
                <div>
                  <div className="text-gray-400">Feedback:</div>
                  <ul className="mt-1 list-disc list-inside text-gray-200 text-sm space-y-1">
                    {((selected as any).feedback_samples as any[]).map((f, i) => (
                      <li key={i} className="text-[13px]">{String(f)}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
            <div className="mt-3">
              <div className="text-xs text-gray-400 mb-1">Raw</div>
              <pre className="text-[11px] text-gray-300 bg-gray-950 border border-gray-800 rounded p-2 max-h-64 overflow-auto whitespace-pre-wrap break-all">{JSON.stringify(selected, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
