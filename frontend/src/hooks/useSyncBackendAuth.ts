'use client'

import { useEffect } from 'react'
import { useDynamicContext } from '@dynamic-labs/sdk-react-core'

export function useSyncBackendAuth() {
  const { isAuthenticated, primaryWallet } = useDynamicContext()
  const address = (primaryWallet as any)?.address as string | undefined

  useEffect(() => {
    const sync = async () => {
      try {
        if (isAuthenticated && address) {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
          })
          if (!res.ok) throw new Error(`Login failed: ${res.status}`)
          const data = await res.json()
          if (data?.access_token) {
            localStorage.setItem('access_token', data.access_token)
          }
        } else {
          // Clear token on logout
          localStorage.removeItem('access_token')
        }
      } catch (e) {
        // Swallow errors to avoid blocking UI
        console.warn('Backend auth sync failed', e)
      }
    }
    sync()
  }, [isAuthenticated, address])
}

