'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { DynamicContextProvider } from '@dynamic-labs/sdk-react-core'
import { useSyncBackendAuth } from '@/hooks/useSyncBackendAuth'

// If you want wallet-specific connectors, you can add dynamic packages
// without making them mandatory in dev (Dynamic auto-detects where possible).
// Keeping it minimal to avoid bundling extra connectors unless needed.

export function Providers({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const envId = process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID

  if (!envId) {
    // No Dynamic environment configured; return children unchanged
    return <>{children}</>
  }

  return (
    <DynamicContextProvider
      settings={{
        environmentId: envId,
        // Redirect to chat on successful auth for smoother UX
        events: {
          onAuthSuccess: () => {
            try {
              router.push('/chat')
            } catch {}
          }
        }
      }}
    >
      {/* Sync Dynamic wallet -> backend JWT for API calls */}
      <AuthSync>{children}</AuthSync>
    </DynamicContextProvider>
  )
}

function AuthSync({ children }: { children: React.ReactNode }) {
  useSyncBackendAuth()
  return <>{children}</>
}
