'use client'

import React from 'react'
import { DynamicWidget, useDynamicContext } from '@dynamic-labs/sdk-react-core'

interface UserMenuProps {
  compact?: boolean
}

export function UserMenu({ compact = false }: UserMenuProps) {
  const { user, isAuthenticated } = useDynamicContext()

  const envId = process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID
  if (!envId) {
    // Fallback UI when Dynamic is not configured
    return (
      <button
        className="px-3 py-1 rounded-md bg-gray-800 text-gray-200 hover:bg-gray-700 border border-gray-700"
        onClick={() => alert('Authentication not configured. Set NEXT_PUBLIC_DYNAMIC_ENV_ID to enable.')}
      >
        Sign in
      </button>
    )
  }

  // Use Dynamic's built-in widget for sign-in/profile
  return (
    <div className="flex items-center gap-2">
      <DynamicWidget
        variant={compact ? 'modal' : 'dropdown'}
        buttonClassName="!bg-gray-800 !text-gray-200 hover:!bg-gray-700 !border !border-gray-700"
      />
      {isAuthenticated && user?.email && (
        <span className="text-sm text-gray-300 hidden md:block">{user.email}</span>
      )}
    </div>
  )
}

