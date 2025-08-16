'use client'

import React, { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

export function CreditsBadge() {
  const { userId, walletAddress } = useAuth()
  const [remaining, setRemaining] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const res = await fetch('/api/credits/me', {
          headers: {
            ...(userId || walletAddress ? { 'X-User-Id': String(userId || walletAddress) } : {}),
          }
        })
        if (!res.ok) throw new Error(`Failed: ${res.status}`)
        const data = await res.json()
        setRemaining(Number(data?.data?.remaining_today_credits ?? 0))
      } catch {
        setRemaining(null)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId, walletAddress])

  return (
    <div className="px-2 py-1 rounded-md border border-gray-700 text-gray-300 text-xs inline-flex items-center gap-1">
      <span>Credits</span>
      <span className="font-mono">
        {loading ? '...' : (remaining != null ? remaining : '—')}
      </span>
    </div>
  )
}

