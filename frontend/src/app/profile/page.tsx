'use client'

import React from 'react'
import { useDynamicContext } from '@dynamic-labs/sdk-react-core'

export default function ProfilePage() {
  const { user, isAuthenticated, primaryWallet } = useDynamicContext()

  if (!isAuthenticated) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-gray-300">
        <div className="text-center">
          <h1 className="text-2xl font-semibold mb-2">You are not signed in</h1>
          <p>Use the Sign In button in the header to authenticate.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 text-gray-200">
      <h1 className="text-3xl font-semibold mb-6">Profile</h1>
      <div className="space-y-4 bg-gray-900 border border-gray-800 rounded-lg p-6">
        <div>
          <div className="text-sm text-gray-400">User ID</div>
          <div className="font-mono break-all">{(user as any)?.userId || 'N/A'}</div>
        </div>
        <div>
          <div className="text-sm text-gray-400">Email</div>
          <div>{(user as any)?.email || 'N/A'}</div>
        </div>
        <div>
          <div className="text-sm text-gray-400">Primary wallet</div>
          <div className="font-mono break-all">{(primaryWallet as any)?.address || 'N/A'}</div>
        </div>
      </div>
    </div>
  )
}
