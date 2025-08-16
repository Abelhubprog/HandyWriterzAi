'use client'

import { useMemo } from 'react'
import { useDynamicContext } from '@dynamic-labs/sdk-react-core'

export interface AuthInfo {
  isAuthenticated: boolean
  userId: string | null
  walletAddress: string | null
  email: string | null
}

export function useAuth(): AuthInfo {
  const { user, isAuthenticated, primaryWallet } = useDynamicContext()

  return useMemo(() => ({
    isAuthenticated: !!isAuthenticated,
    userId: (user as any)?.userId ?? null,
    walletAddress: (primaryWallet as any)?.address ?? null,
    email: (user as any)?.email ?? null,
  }), [user, isAuthenticated, primaryWallet])
}

