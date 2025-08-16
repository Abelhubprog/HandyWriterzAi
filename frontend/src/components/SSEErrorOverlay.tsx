'use client'

import React from 'react'
import { AlertTriangle, X } from 'lucide-react'

interface Props {
  message: string
  onClose?: () => void
}

export function SSEErrorOverlay({ message, onClose }: Props) {
  const [open, setOpen] = React.useState(true)
  const handleClose = () => {
    setOpen(false)
    onClose?.()
  }
  if (!open) return null
  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md w-[90vw] sm:w-[420px] shadow-lg border border-red-600 bg-red-50 dark:bg-red-950 text-red-900 dark:text-red-100 rounded-md p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" />
        <div className="flex-1">
          <div className="font-semibold mb-1">Streaming Error</div>
          <div className="text-sm opacity-90 break-words">{message}</div>
        </div>
        <button className="p-1 hover:opacity-80" onClick={handleClose} aria-label="Close error">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

